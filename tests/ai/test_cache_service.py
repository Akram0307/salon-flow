"""Tests for Cache Service

Tests for the caching functionality.
"""
import pytest
import sys
import os
from unittest.mock import patch, AsyncMock, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../services/ai'))


class TestCacheService:
    """Test cache service functionality"""

    @pytest.mark.asyncio
    async def test_cache_disabled_get(self):
        """Test cache get when disabled"""
        with patch("app.core.config.get_settings") as mock:
            settings = MagicMock()
            settings.enable_cache = False
            settings.upstash_redis_rest_url = None
            settings.upstash_redis_rest_token = None
            mock.return_value = settings

            from app.services.cache_service import CacheService
            service = CacheService()

            result = await service.get("test_key")
            assert result is None

    @pytest.mark.asyncio
    async def test_cache_disabled_set(self):
        """Test cache set when disabled"""
        with patch("app.core.config.get_settings") as mock:
            settings = MagicMock()
            settings.enable_cache = False
            settings.upstash_redis_rest_url = None
            settings.upstash_redis_rest_token = None
            mock.return_value = settings

            from app.services.cache_service import CacheService
            service = CacheService()

            result = await service.set("test_key", "test_value")
            assert result is False

    @pytest.mark.asyncio
    async def test_cache_disabled_get_or_compute(self):
        """Test get_or_compute when disabled"""
        with patch("app.core.config.get_settings") as mock:
            settings = MagicMock()
            settings.enable_cache = False
            settings.upstash_redis_rest_url = None
            settings.upstash_redis_rest_token = None
            mock.return_value = settings

            from app.services.cache_service import CacheService
            service = CacheService()

            async def compute():
                return "computed_result"

            result = await service.get_or_compute(
                "prefix",
                {"key": "value"},
                compute
            )
            assert result == "computed_result"

    def test_generate_key(self):
        """Test cache key generation"""
        with patch("app.core.config.get_settings") as mock:
            settings = MagicMock()
            settings.enable_cache = False
            settings.upstash_redis_rest_url = None
            settings.upstash_redis_rest_token = None
            mock.return_value = settings

            from app.services.cache_service import CacheService
            service = CacheService()

            key = service._generate_key("prefix", {"key": "value"})
            assert key.startswith("ai:prefix:")

    def test_generate_key_consistency(self):
        """Test cache key generation consistency"""
        with patch("app.core.config.get_settings") as mock:
            settings = MagicMock()
            settings.enable_cache = False
            settings.upstash_redis_rest_url = None
            settings.upstash_redis_rest_token = None
            mock.return_value = settings

            from app.services.cache_service import CacheService
            service = CacheService()

            key1 = service._generate_key("prefix", {"key": "value"})
            key2 = service._generate_key("prefix", {"key": "value"})
            assert key1 == key2

    def test_generate_key_different_data(self):
        """Test cache key differs for different data"""
        with patch("app.core.config.get_settings") as mock:
            settings = MagicMock()
            settings.enable_cache = False
            settings.upstash_redis_rest_url = None
            settings.upstash_redis_rest_token = None
            mock.return_value = settings

            from app.services.cache_service import CacheService
            service = CacheService()

            key1 = service._generate_key("prefix", {"key": "value1"})
            key2 = service._generate_key("prefix", {"key": "value2"})
            assert key1 != key2

    @pytest.mark.asyncio
    async def test_close(self):
        """Test cache close"""
        with patch("app.core.config.get_settings") as mock:
            settings = MagicMock()
            settings.enable_cache = False
            settings.upstash_redis_rest_url = None
            settings.upstash_redis_rest_token = None
            mock.return_value = settings

            from app.services.cache_service import CacheService
            service = CacheService()
            service._client = MagicMock()

            await service.close()
            assert service._client is None


# Run tests with: pytest tests/ai/test_cache_service.py -v
