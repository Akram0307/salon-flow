"""Pytest configuration for AI service tests"""
import pytest
import sys
import os

# Add AI service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../services/ai'))


@pytest.fixture
def mock_openrouter_response():
    """Mock OpenRouter API response"""
    return {
        "id": "chatcmpl-123",
        "model": "google/gemini-2.0-flash-exp:free",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "I recommend booking at 2 PM with our senior stylist Priya."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    from unittest.mock import AsyncMock
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=None)
    mock.setex = AsyncMock(return_value=True)
    mock.ping = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client"""
    from unittest.mock import AsyncMock, MagicMock
    mock = AsyncMock()
    mock.post = AsyncMock()
    mock.is_closed = False
    mock.aclose = AsyncMock()
    return mock


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    from unittest.mock import MagicMock
    settings = MagicMock()
    settings.openrouter_api_key = "test-api-key"
    settings.openrouter_base_url = "https://openrouter.ai/api/v1"
    settings.default_model = "google/gemini-2.0-flash-exp:free"
    settings.fallback_model = "google/gemini-flash-1.5"
    settings.max_tokens = 4096
    settings.temperature = 0.7
    settings.redis_url = "redis://localhost:6379/2"
    settings.cache_ttl = 3600
    settings.enable_cache = False  # Disable cache for tests
    settings.enable_logging = False
    return settings
