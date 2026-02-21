"""Encryption utilities for sensitive data using GCP KMS.

Implements AES-256-GCM encryption via Google Cloud KMS for secure
storage of sensitive credentials like Twilio auth tokens.
"""
import base64
import os
from typing import Optional, Tuple
from dataclasses import dataclass

from google.cloud import kms
from google.api_core import exceptions as gcp_exceptions
import structlog

logger = structlog.get_logger()


@dataclass
class EncryptionConfig:
    """Configuration for KMS encryption."""
    project_id: str
    location: str
    key_ring: str
    key_name: str
    
    @property
    def key_path(self) -> str:
        """Full path to the KMS key."""
        return kms.KeyManagementServiceClient.crypto_key_path(
            self.project_id, self.location, self.key_ring, self.key_name
        )


class EncryptionService:
    """Service for encrypting/decrypting sensitive data using GCP KMS.
    
    Uses envelope encryption pattern:
    1. KMS generates a Data Encryption Key (DEK)
    2. DEK is used to encrypt data locally with AES-256-GCM
    3. Encrypted DEK is stored alongside encrypted data
    
    This approach minimizes KMS API calls and improves performance.
    """
    
    def __init__(self, config: Optional[EncryptionConfig] = None):
        """Initialize encryption service.
        
        Args:
            config: Encryption configuration. If not provided, uses env vars.
        """
        if config:
            self.config = config
        else:
            self.config = EncryptionConfig(
                project_id=os.getenv("GCP_PROJECT_ID", "salon-saas-487508"),
                location=os.getenv("KMS_LOCATION", "asia-south1"),
                key_ring=os.getenv("KMS_KEY_RING", "salon-flow-keyring"),
                key_name=os.getenv("KMS_KEY_NAME", "twilio-credentials-key"),
            )
        
        self._client: Optional[kms.KeyManagementServiceClient] = None
        self._cached_dek: Optional[Tuple[bytes, bytes]] = None  # (dek, encrypted_dek)
    
    @property
    def client(self) -> kms.KeyManagementServiceClient:
        """Lazy initialization of KMS client."""
        if self._client is None:
            self._client = kms.KeyManagementServiceClient()
        return self._client
    
    def _generate_dek(self) -> Tuple[bytes, bytes]:
        """Generate a Data Encryption Key using KMS.
        
        Returns:
            Tuple of (plaintext_dek, encrypted_dek)
        """
        try:
            response = self.client.generate_random_bytes(
                request={
                    "location": f"projects/{self.config.project_id}/locations/{self.config.location}",
                    "length_bytes": 32,  # 256 bits for AES-256
                }
            )
            plaintext_dek = response.data
            
            # Encrypt the DEK with KMS
            encrypt_response = self.client.encrypt(
                request={
                    "name": self.config.key_path,
                    "plaintext": plaintext_dek,
                }
            )
            encrypted_dek = encrypt_response.ciphertext
            
            return plaintext_dek, encrypted_dek
            
        except gcp_exceptions.NotFound:
            logger.warning("KMS key not found, falling back to local encryption")
            # Fallback for development without KMS
            import secrets
            plaintext_dek = secrets.token_bytes(32)
            encrypted_dek = b"dev_mode:" + plaintext_dek  # Insecure, only for dev
            return plaintext_dek, encrypted_dek
    
    def _get_dek(self) -> Tuple[bytes, bytes]:
        """Get or generate a DEK.
        
        Caches the DEK for reuse within the same instance.
        
        Returns:
            Tuple of (plaintext_dek, encrypted_dek)
        """
        if self._cached_dek is None:
            self._cached_dek = self._generate_dek()
        return self._cached_dek
    
    def _decrypt_dek(self, encrypted_dek: bytes) -> bytes:
        """Decrypt a Data Encryption Key.
        
        Args:
            encrypted_dek: The encrypted DEK
            
        Returns:
            The plaintext DEK
        """
        # Check for dev mode
        if encrypted_dek.startswith(b"dev_mode:"):
            return encrypted_dek[9:]  # Remove prefix
        
        response = self.client.decrypt(
            request={
                "name": self.config.key_path,
                "ciphertext": encrypted_dek,
            }
        )
        return response.plaintext
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string value.
        
        Uses AES-256-GCM for encryption with the DEK.
        
        Args:
            plaintext: The string to encrypt
            
        Returns:
            Base64-encoded encrypted data (encrypted_dek + nonce + ciphertext)
        """
        if not plaintext:
            return ""
        
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            import secrets
            
            # Get DEK
            dek, encrypted_dek = self._get_dek()
            
            # Generate nonce
            nonce = secrets.token_bytes(12)  # 96 bits for GCM
            
            # Encrypt with AES-256-GCM
            aesgcm = AESGCM(dek)
            ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
            
            # Combine: encrypted_dek_length(4) + encrypted_dek + nonce + ciphertext
            result = (
                len(encrypted_dek).to_bytes(4, 'big') +
                encrypted_dek +
                nonce +
                ciphertext
            )
            
            return base64.b64encode(result).decode('utf-8')
            
        except Exception as e:
            logger.error("Encryption failed", error=str(e))
            raise
    
    def decrypt(self, encrypted: str) -> str:
        """Decrypt an encrypted string.
        
        Args:
            encrypted: Base64-encoded encrypted data
            
        Returns:
            The decrypted plaintext string
        """
        if not encrypted:
            return ""
        
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            
            # Decode base64
            data = base64.b64decode(encrypted)
            
            # Extract components
            dek_length = int.from_bytes(data[:4], 'big')
            encrypted_dek = data[4:4+dek_length]
            nonce = data[4+dek_length:4+dek_length+12]
            ciphertext = data[4+dek_length+12:]
            
            # Decrypt DEK
            dek = self._decrypt_dek(encrypted_dek)
            
            # Decrypt data
            aesgcm = AESGCM(dek)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            
            return plaintext.decode('utf-8')
            
        except Exception as e:
            logger.error("Decryption failed", error=str(e))
            raise


# Singleton instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """Get the singleton encryption service instance."""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service


def encrypt_credential(plaintext: str) -> str:
    """Convenience function to encrypt a credential."""
    return get_encryption_service().encrypt(plaintext)


def decrypt_credential(encrypted: str) -> str:
    """Convenience function to decrypt a credential."""
    return get_encryption_service().decrypt(encrypted)
