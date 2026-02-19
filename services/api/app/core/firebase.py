"""Firebase initialization"""
import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
from firebase_admin.firestore import client
import structlog

logger = structlog.get_logger()

_firestore_client = None


def init_firebase():
    """Initialize Firebase Admin SDK"""
    global _firestore_client
    
    # Check if already initialized
    if firebase_admin._apps:
        logger.info("Firebase already initialized")
        _firestore_client = firestore.client()
        return
    
    # Set emulator environment variables
    project_id = os.getenv("FIREBASE_PROJECT_ID", "salon-flow-dev")
    
    # For emulator, use default credentials
    os.environ["FIRESTORE_EMULATOR_HOST"] = os.getenv("FIRESTORE_EMULATOR_HOST", "localhost:8080")
    os.environ["FIREBASE_AUTH_EMULATOR_HOST"] = os.getenv("FIREBASE_AUTH_EMULATOR_HOST", "localhost:9099")
    
    # Initialize with default project
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        "projectId": project_id,
    })
    
    _firestore_client = firestore.client()
    logger.info("Firebase initialized", project_id=project_id)


def get_firestore():
    """Get Firestore client"""
    global _firestore_client
    if _firestore_client is None:
        init_firebase()
    return _firestore_client


def get_auth():
    """Get Firebase Auth"""
    return auth
