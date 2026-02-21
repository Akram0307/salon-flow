"""Plugin Loader for Agent Discovery and Hot-Reloading

Implements the Microkernel pattern for dynamic agent loading.
Supports auto-discovery, hot-reloading, and dependency injection.
"""
import os
import sys
import importlib
import importlib.util
import inspect
from typing import Dict, Type, Optional, List
from pathlib import Path
import structlog
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .base import AgentPlugin, AgentMetadata, AgentExecutionError

logger = structlog.get_logger()


class PluginLoader:
    """Auto-discovers and loads agent plugins from specified directories.
    
    The PluginLoader implements the Microkernel architecture pattern:
    - Auto-discovery: Scans directories for agent plugins
    - Hot-reload: Reload plugins without service restart
    - Dependency injection: Inject services into plugins
    - Lifecycle management: Initialize and cleanup plugins
    
    Example:
        loader = PluginLoader()
        plugins = loader.discover()
        booking_agent = loader.load("booking")
        
        # Hot-reload after code change
        loader.reload("booking")
    """
    
    def __init__(
        self,
        plugins_dir: Optional[str] = None,
        agents_module: str = "app.services.agents",
        auto_discover: bool = True
    ):
        """Initialize the plugin loader.
        
        Args:
            plugins_dir: Directory containing plugin files (optional)
            agents_module: Python module path for agents (default: app.services.agents)
            auto_discover: Whether to auto-discover on init
        """
        self.plugins_dir = Path(plugins_dir) if plugins_dir else None
        self.agents_module = agents_module
        self._loaded_plugins: Dict[str, Type[AgentPlugin]] = {}
        self._plugin_instances: Dict[str, AgentPlugin] = {}
        self._module_timestamps: Dict[str, float] = {}
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        if auto_discover:
            self.discover()
    
    def discover(self) -> Dict[str, Type[AgentPlugin]]:
        """Discover all plugins in the configured locations.
        
        Searches both:
        1. The agents module (app.services.agents) for existing agents
        2. The plugins directory for new plugin-based agents
        
        Returns:
            Dictionary mapping plugin names to plugin classes
        """
        discovered = {}
        
        # Discover from agents module (backward compatibility)
        module_plugins = self._discover_from_module()
        discovered.update(module_plugins)
        
        # Discover from plugins directory if configured
        if self.plugins_dir and self.plugins_dir.exists():
            dir_plugins = self._discover_from_directory()
            discovered.update(dir_plugins)
        
        self._loaded_plugins.update(discovered)
        logger.info(
            "plugin_discovery_complete",
            total_plugins=len(discovered),
            plugin_names=list(discovered.keys())
        )
        
        return discovered
    
    def _discover_from_module(self) -> Dict[str, Type[AgentPlugin]]:
        """Discover plugins from the agents module.
        
        This provides backward compatibility with existing agents
        by wrapping them as plugins.
        
        Returns:
            Dictionary of discovered plugins
        """
        plugins = {}
        
        try:
            # Import the agents module
            module = importlib.import_module(self.agents_module)
            
            # Find all agent classes
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and hasattr(obj, 'name') and hasattr(obj, 'generate'):
                    # Check if it's an agent class (has name and generate method)
                    if obj.__module__ == module.__name__ and obj.__name__ != 'BaseAgent':
                        # Create a plugin wrapper for the agent
                        plugin_class = self._create_plugin_wrapper(obj)
                        if plugin_class:
                            agent_name = getattr(obj, 'name', obj.__name__.lower().replace('agent', ''))
                            plugins[agent_name] = plugin_class
                            logger.debug(
                                "discovered_agent_from_module",
                                agent_name=agent_name,
                                original_class=obj.__name__
                            )
        except ImportError as e:
            logger.warning("module_import_failed", module=self.agents_module, error=str(e))
        except Exception as e:
            logger.error("module_discovery_error", error=str(e))
        
        return plugins
    
    def _discover_from_directory(self) -> Dict[str, Type[AgentPlugin]]:
        """Discover plugins from the plugins directory.
        
        Scans for Python files containing AgentPlugin subclasses.
        
        Returns:
            Dictionary of discovered plugins
        """
        plugins = {}
        
        if not self.plugins_dir:
            return plugins
        
        for file_path in self.plugins_dir.glob("**/*.py"):
            if file_path.name.startswith("_"):
                continue
            
            try:
                # Load module from file
                module_name = f"plugins.{file_path.stem}"
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    
                    # Find AgentPlugin subclasses
                    for name, obj in inspect.getmembers(module):
                        if (
                            inspect.isclass(obj) and
                            issubclass(obj, AgentPlugin) and
                            obj != AgentPlugin and
                            obj.__module__ == module_name
                        ):
                            # Get plugin name from metadata or class name
                            instance = obj()
                            plugin_name = instance.metadata.name
                            plugins[plugin_name] = obj
                            
                            # Track module timestamp for hot-reload
                            self._module_timestamps[plugin_name] = file_path.stat().st_mtime
                            
                            logger.debug(
                                "discovered_plugin_from_directory",
                                plugin_name=plugin_name,
                                file=str(file_path)
                            )
            except Exception as e:
                logger.warning(
                    "plugin_file_load_error",
                    file=str(file_path),
                    error=str(e)
                )
        
        return plugins
    
    def _create_plugin_wrapper(self, agent_class: type) -> Optional[Type[AgentPlugin]]:
        """Create a plugin wrapper for an existing agent class.
        
        This enables backward compatibility with existing agents
        by wrapping them in the AgentPlugin interface.
        
        Args:
            agent_class: The original agent class to wrap
            
        Returns:
            A plugin class that wraps the original agent
        """
        try:
            # Get agent metadata
            agent_name = getattr(agent_class, 'name', agent_class.__name__.lower().replace('agent', ''))
            description = getattr(agent_class, 'description', f"Agent for {agent_name}")
            
            class AgentPluginWrapper(AgentPlugin):
                """Wrapper for legacy agents"""
                
                def __init__(wrapper_self):
                    wrapper_self._agent = agent_class()
                    wrapper_self._name = agent_name
                
                @property
                def metadata(wrapper_self) -> AgentMetadata:
                    return AgentMetadata(
                        name=agent_name,
                        version="1.0.0",
                        description=description,
                        capabilities=self._extract_capabilities(wrapper_self._agent),
                        model_tier="standard",
                        channels=["web", "whatsapp"]
                    )
                
                async def execute(
                    wrapper_self,
                    request: dict,
                    context: Optional[dict] = None
                ) -> dict:
                    """Execute using the wrapped agent"""
                    prompt = request.get("prompt", "")
                    ctx = request.get("context", context)
                    history = request.get("history", None)
                    use_cache = request.get("use_cache", True)
                    skip_guardrail = request.get("skip_guardrail", False)
                    
                    # Call the original agent's generate method
                    response = await wrapper_self._agent.generate(
                        prompt=prompt,
                        context=ctx,
                        history=history,
                        use_cache=use_cache,
                        skip_guardrail=skip_guardrail
                    )
                    
                    return response.model_dump()
                
                def _extract_capabilities(agent) -> List[str]:
                    """Extract capabilities from agent methods"""
                    capabilities = []
                    for method_name in dir(agent):
                        if method_name.startswith('_'):
                            continue
                        if callable(getattr(agent, method_name, None)) and method_name not in ['generate', 'metadata']:
                            capabilities.append(method_name)
                    return capabilities[:5]  # Limit to 5 main capabilities
            
            return AgentPluginWrapper
            
        except Exception as e:
            logger.error(
                "plugin_wrapper_creation_failed",
                agent_class=agent_class.__name__,
                error=str(e)
            )
            return None
    
    def load(self, agent_name: str) -> AgentPlugin:
        """Load a specific plugin by name.
        
        Args:
            agent_name: Name of the agent to load
            
        Returns:
            Agent plugin instance
            
        Raises:
            AgentExecutionError: If plugin not found or load fails
        """
        if agent_name in self._plugin_instances:
            return self._plugin_instances[agent_name]
        
        plugin_class = self._loaded_plugins.get(agent_name)
        if not plugin_class:
            # Try to discover again
            self.discover()
            plugin_class = self._loaded_plugins.get(agent_name)
        
        if not plugin_class:
            raise AgentExecutionError(
                agent_name=agent_name,
                message=f"Plugin '{agent_name}' not found in registry"
            )
        
        try:
            instance = plugin_class()
            self._plugin_instances[agent_name] = instance
            logger.info("plugin_loaded", agent_name=agent_name)
            return instance
        except Exception as e:
            raise AgentExecutionError(
                agent_name=agent_name,
                message=f"Failed to instantiate plugin: {str(e)}"
            )
    
    def reload(self, agent_name: str) -> AgentPlugin:
        """Hot-reload a plugin.
        
        Reloads the plugin from disk, useful for development
        and updates without service restart.
        
        Args:
            agent_name: Name of the agent to reload
            
        Returns:
            Reloaded agent plugin instance
        """
        logger.info("hot_reloading_plugin", agent_name=agent_name)
        
        # Clear cached instance
        if agent_name in self._plugin_instances:
            del self._plugin_instances[agent_name]
        
        # Re-import the module if it's a directory-based plugin
        if agent_name in self._module_timestamps:
            # Find the module and reload it
            for module_name, module in list(sys.modules.items()):
                if module_name.startswith("plugins."):
                    try:
                        importlib.reload(module)
                    except Exception as e:
                        logger.warning(
                            "module_reload_failed",
                            module=module_name,
                            error=str(e)
                        )
        
        # Re-discover plugins
        self.discover()
        
        # Load fresh instance
        return self.load(agent_name)
    
    def unload(self, agent_name: str) -> bool:
        """Unload a plugin from memory.
        
        Args:
            agent_name: Name of the agent to unload
            
        Returns:
            True if unloaded, False if not found
        """
        if agent_name in self._plugin_instances:
            del self._plugin_instances[agent_name]
            logger.info("plugin_unloaded", agent_name=agent_name)
            return True
        
        if agent_name in self._loaded_plugins:
            del self._loaded_plugins[agent_name]
            logger.info("plugin_class_removed", agent_name=agent_name)
            return True
        
        return False
    
    def list_loaded(self) -> List[str]:
        """List all loaded plugin names.
        
        Returns:
            List of loaded plugin names
        """
        return list(self._loaded_plugins.keys())
    
    def get_plugin_info(self, agent_name: str) -> Optional[Dict]:
        """Get detailed information about a plugin.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Plugin information dictionary or None if not found
        """
        if agent_name not in self._loaded_plugins:
            return None
        
        try:
            instance = self.load(agent_name)
            metadata = instance.metadata
            return {
                "name": metadata.name,
                "version": metadata.version,
                "description": metadata.description,
                "capabilities": metadata.capabilities,
                "model_tier": metadata.model_tier,
                "channels": metadata.channels,
                "loaded": agent_name in self._plugin_instances
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Run health check on all loaded plugins.
        
        Returns:
            Dictionary mapping plugin names to health status
        """
        results = {}
        
        for name in self._loaded_plugins:
            try:
                instance = self.load(name)
                results[name] = await instance.health_check()
            except Exception as e:
                logger.warning("plugin_health_check_failed", plugin=name, error=str(e))
                results[name] = False
        
        return results


# Singleton instance
_loader_instance: Optional[PluginLoader] = None


def get_plugin_loader() -> PluginLoader:
    """Get or create the singleton plugin loader instance."""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = PluginLoader()
    return _loader_instance
