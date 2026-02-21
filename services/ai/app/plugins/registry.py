"""Agent Registry for Centralized Plugin Management

Implements a singleton registry pattern for managing all agent plugins.
Provides registration, lookup, and lifecycle management capabilities.
"""
from typing import Dict, List, Optional, Type, Any
import structlog
import asyncio
from datetime import datetime

from .base import AgentPlugin, AgentMetadata, AgentNotFoundError, AgentExecutionError
from .loader import PluginLoader, get_plugin_loader

logger = structlog.get_logger()


class AgentRegistry:
    """Central registry for all agent plugins.
    
    Implements the Singleton pattern to ensure a single source of truth
    for all agent plugins in the system.
    
    Features:
    - Plugin registration with validation
    - Plugin lookup by name or capability
    - Lifecycle management (initialize, health check, cleanup)
    - Metrics collection
    
    Example:
        registry = AgentRegistry.get_instance()
        
        # Register an agent
        registry.register(my_agent_plugin)
        
        # Get agent by name
        agent = registry.get("booking")
        
        # List all agents
        all_agents = registry.list_all()
    """
    
    _instance: Optional['AgentRegistry'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'AgentRegistry':
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the registry (only once due to singleton)."""
        if AgentRegistry._initialized:
            return
        
        self._agents: Dict[str, AgentPlugin] = {}
        self._metadata_cache: Dict[str, AgentMetadata] = {}
        self._loader: Optional[PluginLoader] = None
        self._metrics: Dict[str, Dict[str, Any]] = {}
        self._initialized_at: datetime = datetime.utcnow()
        
        AgentRegistry._initialized = True
        logger.info("agent_registry_initialized")
    
    @classmethod
    def get_instance(cls) -> 'AgentRegistry':
        """Get the singleton registry instance.
        
        Returns:
            The AgentRegistry singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        if cls._instance is not None:
            cls._instance._agents.clear()
            cls._instance._metadata_cache.clear()
            cls._instance._metrics.clear()
        cls._initialized = False
        cls._instance = None
    
    def set_loader(self, loader: PluginLoader) -> None:
        """Set the plugin loader for auto-discovery.
        
        Args:
            loader: PluginLoader instance
        """
        self._loader = loader
    
    def register(self, agent: AgentPlugin) -> None:
        """Register an agent plugin.
        
        Args:
            agent: AgentPlugin instance to register
            
        Raises:
            AgentExecutionError: If registration fails
        """
        try:
            metadata = agent.metadata
            name = metadata.name
            
            if name in self._agents:
                logger.warning(
                    "agent_already_registered",
                    agent_name=name,
                    action="replacing"
                )
            
            self._agents[name] = agent
            self._metadata_cache[name] = metadata
            self._metrics[name] = {
                "registered_at": datetime.utcnow().isoformat(),
                "execution_count": 0,
                "error_count": 0,
                "total_execution_time_ms": 0.0
            }
            
            logger.info(
                "agent_registered",
                agent_name=name,
                version=metadata.version,
                capabilities=metadata.capabilities
            )
            
        except Exception as e:
            raise AgentExecutionError(
                agent_name=getattr(agent, 'metadata', AgentMetadata(name="unknown", description="")).name,
                message=f"Failed to register agent: {str(e)}"
            )
    
    def unregister(self, name: str) -> bool:
        """Unregister an agent plugin.
        
        Args:
            name: Name of the agent to unregister
            
        Returns:
            True if unregistered, False if not found
        """
        if name in self._agents:
            del self._agents[name]
            del self._metadata_cache[name]
            del self._metrics[name]
            logger.info("agent_unregistered", agent_name=name)
            return True
        return False
    
    def get(self, name: str) -> AgentPlugin:
        """Get agent by name.
        
        Args:
            name: Name of the agent to retrieve
            
        Returns:
            AgentPlugin instance
            
        Raises:
            AgentNotFoundError: If agent not found
        """
        if name in self._agents:
            return self._agents[name]
        
        # Try to load from loader if available
        if self._loader:
            try:
                agent = self._loader.load(name)
                self.register(agent)
                return agent
            except AgentExecutionError:
                pass
        
        raise AgentNotFoundError(name)
    
    def get_metadata(self, name: str) -> AgentMetadata:
        """Get agent metadata by name.
        
        Args:
            name: Name of the agent
            
        Returns:
            AgentMetadata for the agent
            
        Raises:
            AgentNotFoundError: If agent not found
        """
        if name in self._metadata_cache:
            return self._metadata_cache[name]
        
        # Load agent to get metadata
        agent = self.get(name)
        return agent.metadata
    
    def list_all(self) -> List[AgentMetadata]:
        """List all registered agents.
        
        Returns:
            List of AgentMetadata for all registered agents
        """
        return list(self._metadata_cache.values())
    
    def list_names(self) -> List[str]:
        """List all registered agent names.
        
        Returns:
            List of agent names
        """
        return list(self._agents.keys())
    
    def find_by_capability(self, capability: str) -> List[AgentMetadata]:
        """Find agents by capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of AgentMetadata for matching agents
        """
        matching = []
        for metadata in self._metadata_cache.values():
            if capability in metadata.capabilities:
                matching.append(metadata)
        return matching
    
    def find_by_channel(self, channel: str) -> List[AgentMetadata]:
        """Find agents by supported channel.
        
        Args:
            channel: Channel to search for (web, whatsapp, voice)
            
        Returns:
            List of AgentMetadata for matching agents
        """
        matching = []
        for metadata in self._metadata_cache.values():
            if channel in metadata.channels:
                matching.append(metadata)
        return matching
    
    def find_by_tier(self, tier: str) -> List[AgentMetadata]:
        """Find agents by model tier.
        
        Args:
            tier: Model tier to search for (economy, standard, premium)
            
        Returns:
            List of AgentMetadata for matching agents
        """
        matching = []
        for metadata in self._metadata_cache.values():
            if metadata.model_tier == tier:
                matching.append(metadata)
        return matching
    
    async def execute(
        self,
        name: str,
        request: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute an agent with metrics tracking.
        
        Args:
            name: Name of the agent to execute
            request: Request data
            context: Optional execution context
            
        Returns:
            Agent response
            
        Raises:
            AgentNotFoundError: If agent not found
            AgentExecutionError: If execution fails
        """
        agent = self.get(name)
        start_time = datetime.utcnow()
        
        try:
            # Validate input
            is_valid = await agent.validate_input(request)
            if not is_valid:
                raise AgentExecutionError(
                    agent_name=name,
                    message="Input validation failed"
                )
            
            # Execute
            response = await agent.execute(request, context)
            
            # Post-process
            response = await agent.post_process(response)
            
            # Update metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._update_metrics(name, execution_time, success=True)
            response["execution_time_ms"] = execution_time
            
            return response
            
        except AgentExecutionError:
            self._update_metrics(name, 0, success=False)
            raise
        except Exception as e:
            self._update_metrics(name, 0, success=False)
            raise AgentExecutionError(
                agent_name=name,
                message=f"Execution failed: {str(e)}"
            )
    
    def _update_metrics(self, name: str, execution_time_ms: float, success: bool) -> None:
        """Update agent metrics.
        
        Args:
            name: Agent name
            execution_time_ms: Execution time in milliseconds
            success: Whether execution succeeded
        """
        if name not in self._metrics:
            return
        
        self._metrics[name]["execution_count"] += 1
        self._metrics[name]["total_execution_time_ms"] += execution_time_ms
        
        if not success:
            self._metrics[name]["error_count"] += 1
    
    def get_metrics(self, name: str) -> Optional[Dict[str, Any]]:
        """Get metrics for an agent.
        
        Args:
            name: Agent name
            
        Returns:
            Metrics dictionary or None if not found
        """
        return self._metrics.get(name)
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all agents.
        
        Returns:
            Dictionary mapping agent names to metrics
        """
        return self._metrics.copy()
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Run health check on all registered agents.
        
        Returns:
            Dictionary mapping agent names to health status
        """
        results = {}
        tasks = []
        
        for name, agent in self._agents.items():
            tasks.append(self._check_agent_health(name, agent))
        
        if tasks:
            health_results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, name in enumerate(self._agents.keys()):
                result = health_results[i]
                results[name] = result if isinstance(result, bool) else False
        
        return results
    
    async def _check_agent_health(self, name: str, agent: AgentPlugin) -> bool:
        """Check health of a single agent."""
        try:
            return await agent.health_check()
        except Exception as e:
            logger.warning("agent_health_check_failed", agent=name, error=str(e))
            return False
    
    async def initialize_all(self) -> Dict[str, bool]:
        """Initialize all agents.
        
        Returns:
            Dictionary mapping agent names to initialization status
        """
        results = {}
        
        for name, agent in self._agents.items():
            try:
                # Agents can override health_check for initialization
                results[name] = await agent.health_check()
                logger.info("agent_initialized", agent=name)
            except Exception as e:
                logger.error("agent_initialization_failed", agent=name, error=str(e))
                results[name] = False
        
        return results
    
    def get_registry_info(self) -> Dict[str, Any]:
        """Get registry information.
        
        Returns:
            Registry information dictionary
        """
        return {
            "initialized_at": self._initialized_at.isoformat(),
            "total_agents": len(self._agents),
            "agent_names": self.list_names(),
            "agents_by_tier": {
                "economy": len(self.find_by_tier("economy")),
                "standard": len(self.find_by_tier("standard")),
                "premium": len(self.find_by_tier("premium"))
            },
            "agents_by_channel": {
                "web": len(self.find_by_channel("web")),
                "whatsapp": len(self.find_by_channel("whatsapp")),
                "voice": len(self.find_by_channel("voice"))
            }
        }


# Convenience function
def get_registry() -> AgentRegistry:
    """Get the AgentRegistry singleton instance.
    
    Returns:
        AgentRegistry instance
    """
    return AgentRegistry.get_instance()


# Auto-initialize registry with loader on import
def initialize_registry() -> AgentRegistry:
    """Initialize the registry with auto-discovery.
    
    Returns:
        Initialized AgentRegistry
    """
    registry = get_registry()
    loader = get_plugin_loader()
    registry.set_loader(loader)
    
    # Discover and register all plugins
    for name in loader.list_loaded():
        try:
            agent = loader.load(name)
            registry.register(agent)
        except Exception as e:
            logger.warning("auto_register_failed", agent=name, error=str(e))
    
    return registry
