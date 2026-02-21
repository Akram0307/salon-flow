"""Agent Plugin System

Microkernel architecture for hot-reloadable, discoverable agent plugins.

Components:
- AgentPlugin: Base class for all agents
- PluginLoader: Auto-discovers and loads plugins
- AgentRegistry: Central registry for agent management

Usage:
    from app.plugins import AgentPlugin, AgentRegistry, get_registry
    
    # Get the registry
    registry = get_registry()
    
    # Get an agent
    agent = registry.get("booking")
    
    # Execute the agent
    response = await registry.execute("booking", {"prompt": "Book a haircut"})
"""
from .base import (
    AgentPlugin,
    AgentMetadata,
    AgentContext,
    AgentRequest,
    AgentResponse,
    AgentExecutionError,
    AgentValidationError,
    AgentNotFoundError,
    ModelTier,
    ChannelType,
)
from .loader import PluginLoader, get_plugin_loader
from .registry import AgentRegistry, get_registry, initialize_registry

__all__ = [
    # Base classes
    "AgentPlugin",
    "AgentMetadata",
    "AgentContext",
    "AgentRequest",
    "AgentResponse",
    # Exceptions
    "AgentExecutionError",
    "AgentValidationError",
    "AgentNotFoundError",
    # Enums
    "ModelTier",
    "ChannelType",
    # Loader
    "PluginLoader",
    "get_plugin_loader",
    # Registry
    "AgentRegistry",
    "get_registry",
    "initialize_registry",
]
