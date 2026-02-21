"""Tests for Plugin System

Tests for the plugin loader and registry.
"""
import pytest
import sys
import os
from unittest.mock import patch, AsyncMock, MagicMock, PropertyMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../services/ai'))


@pytest.fixture(autouse=True)
def mock_settings():
    """Mock settings for all tests"""
    with patch("app.core.config.get_settings") as mock:
        settings = MagicMock()
        settings.openrouter_api_key = "test-api-key"
        settings.openrouter_base_url = "https://openrouter.ai/api/v1"
        settings.openrouter_site_url = "https://salonflow.app"
        settings.openrouter_site_name = "Salon Flow"
        settings.default_model = "google/gemini-2.0-flash-exp:free"
        settings.fallback_model = "google/gemini-flash-1.5"
        settings.max_tokens = 4096
        settings.temperature = 0.7
        settings.redis_url = "redis://localhost:6379/2"
        settings.cache_ttl = 3600
        settings.enable_cache = False
        settings.enable_logging = False
        settings.app_version = "0.1.0"
        settings.upstash_redis_rest_url = None
        settings.upstash_redis_rest_token = None
        mock.return_value = settings
        yield settings


def create_mock_agent(name="test_agent"):
    """Helper to create a properly mocked agent"""
    from app.plugins.base import AgentMetadata, ModelTier, ChannelType

    mock_agent = MagicMock()
    mock_metadata = AgentMetadata(
        name=name,
        version="1.0.0",
        description="Test agent",
        capabilities=["test"],
        channels=[ChannelType.WEB],
        model_tier=ModelTier.STANDARD
    )
    type(mock_agent).metadata = PropertyMock(return_value=mock_metadata)
    mock_agent.health_check = AsyncMock(return_value=True)
    mock_agent.initialize = AsyncMock(return_value=True)
    return mock_agent


class TestPluginLoader:
    """Test plugin loader functionality"""

    def test_init(self, mock_settings):
        """Test plugin loader initialization"""
        from app.plugins.loader import PluginLoader

        loader = PluginLoader(auto_discover=False)
        assert loader._loaded_plugins == {}
        assert loader._plugin_instances == {}

    def test_init_with_plugins_dir(self, mock_settings, tmp_path):
        """Test plugin loader initialization with plugins directory"""
        from app.plugins.loader import PluginLoader

        plugins_dir = str(tmp_path / "plugins")
        os.makedirs(plugins_dir, exist_ok=True)

        loader = PluginLoader(plugins_dir=plugins_dir, auto_discover=False)
        assert loader.plugins_dir is not None

    def test_discover(self, mock_settings):
        """Test plugin discovery"""
        from app.plugins.loader import PluginLoader

        loader = PluginLoader(auto_discover=False)
        with patch.object(loader, '_discover_from_module', return_value={"booking": MagicMock()}):
            result = loader.discover()
            assert "booking" in result

    def test_discover_with_directory(self, mock_settings, tmp_path):
        """Test plugin discovery with directory"""
        from app.plugins.loader import PluginLoader

        plugins_dir = str(tmp_path / "plugins")
        os.makedirs(plugins_dir, exist_ok=True)

        loader = PluginLoader(plugins_dir=plugins_dir, auto_discover=False)
        with patch.object(loader, '_discover_from_module', return_value={}):
            with patch.object(loader, '_discover_from_directory', return_value={}):
                result = loader.discover()
                assert isinstance(result, dict)

    def test_list_loaded(self, mock_settings):
        """Test listing loaded plugins"""
        from app.plugins.loader import PluginLoader

        loader = PluginLoader(auto_discover=False)
        loader._loaded_plugins = {"booking": MagicMock(), "marketing": MagicMock()}

        result = loader.list_loaded()
        assert "booking" in result
        assert "marketing" in result

    def test_get_plugin_info(self, mock_settings):
        """Test getting plugin info - checks _loaded_plugins first"""
        from app.plugins.loader import PluginLoader
        from app.plugins.base import AgentMetadata, ModelTier, ChannelType

        loader = PluginLoader(auto_discover=False)

        # Mock the plugin class and instance
        mock_plugin_class = MagicMock()
        mock_instance = MagicMock()
        mock_metadata = AgentMetadata(
            name="booking",
            version="1.0.0",
            description="Booking agent",
            capabilities=["booking"],
            channels=[ChannelType.WEB, ChannelType.WHATSAPP],
            model_tier=ModelTier.STANDARD
        )
        type(mock_instance).metadata = PropertyMock(return_value=mock_metadata)

        # Set up the loader with the plugin class
        loader._loaded_plugins["booking"] = mock_plugin_class

        # Mock the load method to return our instance
        with patch.object(loader, 'load', return_value=mock_instance):
            result = loader.get_plugin_info("booking")
            assert result is not None
            assert result["name"] == "booking"

    def test_get_plugin_info_not_found(self, mock_settings):
        """Test getting plugin info for non-existent plugin"""
        from app.plugins.loader import PluginLoader

        loader = PluginLoader(auto_discover=False)
        result = loader.get_plugin_info("nonexistent")
        assert result is None

    def test_unload_from_instances(self, mock_settings):
        """Test unloading a plugin from _plugin_instances"""
        from app.plugins.loader import PluginLoader

        loader = PluginLoader(auto_discover=False)
        loader._plugin_instances["booking"] = MagicMock()
        # Don't add to _loaded_plugins - should remove from instances

        result = loader.unload("booking")
        assert result is True
        assert "booking" not in loader._plugin_instances

    def test_unload_from_loaded_plugins(self, mock_settings):
        """Test unloading a plugin from _loaded_plugins"""
        from app.plugins.loader import PluginLoader

        loader = PluginLoader(auto_discover=False)
        loader._loaded_plugins["booking"] = MagicMock()
        # Don't add to _plugin_instances - should remove from loaded_plugins

        result = loader.unload("booking")
        assert result is True
        assert "booking" not in loader._loaded_plugins

    def test_unload_not_found(self, mock_settings):
        """Test unloading a non-existent plugin"""
        from app.plugins.loader import PluginLoader

        loader = PluginLoader(auto_discover=False)
        result = loader.unload("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_all(self, mock_settings):
        """Test health check for all plugins - iterates _loaded_plugins"""
        from app.plugins.loader import PluginLoader

        loader = PluginLoader(auto_discover=False)

        # Create mock plugin class and instance
        mock_plugin_class = MagicMock()
        mock_instance = MagicMock()
        mock_instance.health_check = AsyncMock(return_value=True)

        # Add to _loaded_plugins (which health_check_all iterates)
        loader._loaded_plugins["booking"] = mock_plugin_class

        # Mock the load method to return our instance
        with patch.object(loader, 'load', return_value=mock_instance):
            result = await loader.health_check_all()
            assert "booking" in result
            assert result["booking"] is True


class TestAgentRegistry:
    """Test agent registry functionality"""

    def test_singleton(self, mock_settings):
        """Test registry is singleton"""
        from app.plugins.registry import AgentRegistry

        # Reset first
        AgentRegistry.reset()

        instance1 = AgentRegistry.get_instance()
        instance2 = AgentRegistry.get_instance()

        assert instance1 is instance2

    def test_register(self, mock_settings):
        """Test registering an agent"""
        from app.plugins.registry import AgentRegistry

        AgentRegistry.reset()
        registry = AgentRegistry.get_instance()

        mock_agent = create_mock_agent("test_agent")
        registry.register(mock_agent)
        result = registry.get("test_agent")

        assert result is mock_agent

    def test_unregister(self, mock_settings):
        """Test unregistering an agent"""
        from app.plugins.registry import AgentRegistry

        AgentRegistry.reset()
        registry = AgentRegistry.get_instance()

        mock_agent = create_mock_agent("test_agent")
        registry.register(mock_agent)
        result = registry.unregister("test_agent")

        assert result is True

    def test_unregister_not_found(self, mock_settings):
        """Test unregistering a non-existent agent"""
        from app.plugins.registry import AgentRegistry

        AgentRegistry.reset()
        registry = AgentRegistry.get_instance()

        result = registry.unregister("nonexistent")
        assert result is False

    def test_list_names(self, mock_settings):
        """Test listing agent names"""
        from app.plugins.registry import AgentRegistry

        AgentRegistry.reset()
        registry = AgentRegistry.get_instance()

        mock_agent = create_mock_agent("test_agent")
        registry.register(mock_agent)
        names = registry.list_names()

        assert "test_agent" in names

    def test_find_by_capability(self, mock_settings):
        """Test finding agents by capability"""
        from app.plugins.registry import AgentRegistry
        from app.plugins.base import AgentMetadata, ModelTier, ChannelType

        AgentRegistry.reset()
        registry = AgentRegistry.get_instance()

        mock_agent = MagicMock()
        mock_metadata = AgentMetadata(
            name="test_agent",
            version="1.0.0",
            description="Test agent",
            capabilities=["booking", "scheduling"],
            channels=[ChannelType.WEB],
            model_tier=ModelTier.STANDARD
        )
        type(mock_agent).metadata = PropertyMock(return_value=mock_metadata)
        registry.register(mock_agent)
        results = registry.find_by_capability("booking")

        assert len(results) == 1
        assert results[0].name == "test_agent"

    def test_find_by_channel(self, mock_settings):
        """Test finding agents by channel"""
        from app.plugins.registry import AgentRegistry
        from app.plugins.base import AgentMetadata, ModelTier, ChannelType

        AgentRegistry.reset()
        registry = AgentRegistry.get_instance()

        mock_agent = MagicMock()
        mock_metadata = AgentMetadata(
            name="test_agent",
            version="1.0.0",
            description="Test agent",
            capabilities=["test"],
            channels=[ChannelType.WEB, ChannelType.WHATSAPP],
            model_tier=ModelTier.STANDARD
        )
        type(mock_agent).metadata = PropertyMock(return_value=mock_metadata)
        registry.register(mock_agent)
        results = registry.find_by_channel("whatsapp")

        assert len(results) == 1

    def test_find_by_tier(self, mock_settings):
        """Test finding agents by model tier"""
        from app.plugins.registry import AgentRegistry
        from app.plugins.base import AgentMetadata, ModelTier, ChannelType

        AgentRegistry.reset()
        registry = AgentRegistry.get_instance()

        mock_agent = MagicMock()
        mock_metadata = AgentMetadata(
            name="test_agent",
            version="1.0.0",
            description="Test agent",
            capabilities=["test"],
            channels=[ChannelType.WEB],
            model_tier=ModelTier.PREMIUM
        )
        type(mock_agent).metadata = PropertyMock(return_value=mock_metadata)
        registry.register(mock_agent)
        results = registry.find_by_tier("premium")

        assert len(results) == 1

    def test_get_metrics(self, mock_settings):
        """Test getting agent metrics"""
        from app.plugins.registry import AgentRegistry

        AgentRegistry.reset()
        registry = AgentRegistry.get_instance()

        mock_agent = create_mock_agent("test_agent")
        registry.register(mock_agent)
        metrics = registry.get_metrics("test_agent")
        assert metrics is not None

    def test_get_all_metrics(self, mock_settings):
        """Test getting all agent metrics"""
        from app.plugins.registry import AgentRegistry

        AgentRegistry.reset()
        registry = AgentRegistry.get_instance()

        mock_agent = create_mock_agent("test_agent")
        registry.register(mock_agent)
        metrics = registry.get_all_metrics()

        assert "test_agent" in metrics

    @pytest.mark.asyncio
    async def test_health_check_all(self, mock_settings):
        """Test health check for all agents"""
        from app.plugins.registry import AgentRegistry

        AgentRegistry.reset()
        registry = AgentRegistry.get_instance()

        mock_agent = create_mock_agent("test_agent")
        registry.register(mock_agent)
        result = await registry.health_check_all()

        assert "test_agent" in result

    @pytest.mark.asyncio
    async def test_initialize_all(self, mock_settings):
        """Test initializing all agents"""
        from app.plugins.registry import AgentRegistry

        AgentRegistry.reset()
        registry = AgentRegistry.get_instance()

        mock_agent = create_mock_agent("test_agent")
        registry.register(mock_agent)
        result = await registry.initialize_all()

        assert "test_agent" in result

    def test_get_registry_info(self, mock_settings):
        """Test getting registry info"""
        from app.plugins.registry import AgentRegistry

        AgentRegistry.reset()
        registry = AgentRegistry.get_instance()

        info = registry.get_registry_info()

        assert "total_agents" in info
        assert "agent_names" in info


class TestAgentMetadata:
    """Test agent metadata"""

    def test_metadata_creation(self, mock_settings):
        """Test creating agent metadata"""
        from app.plugins.base import AgentMetadata, ModelTier, ChannelType

        metadata = AgentMetadata(
            name="test_agent",
            version="1.0.0",
            description="Test agent",
            capabilities=["test"],
            channels=[ChannelType.WEB],
            model_tier=ModelTier.STANDARD
        )

        assert metadata.name == "test_agent"
        assert metadata.version == "1.0.0"
        assert metadata.description == "Test agent"
        assert "test" in metadata.capabilities
        assert ChannelType.WEB in metadata.channels
        assert metadata.model_tier == ModelTier.STANDARD


# Run tests with: pytest tests/ai/test_plugins.py -v
