"""Agent Plugin Base Classes

Provides the foundation for the Microkernel architecture with plugin-based agent management.
All agents must inherit from AgentPlugin for hot-reloadable, discoverable functionality.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Type, ClassVar
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class ModelTier(str, Enum):
    """Model tier for cost/performance optimization"""
    ECONOMY = "economy"      # Fast, cheap models (gemini-2.0-flash)
    STANDARD = "standard"    # Balanced models (gemini-2.0-flash)
    PREMIUM = "premium"      # High-quality models (gemini-2.0-pro)


class ChannelType(str, Enum):
    """Supported communication channels"""
    WEB = "web"
    WHATSAPP = "whatsapp"
    VOICE = "voice"


class AgentMetadata(BaseModel):
    """Metadata describing an agent plugin"""
    name: str = Field(..., description="Unique agent identifier")
    version: str = Field(default="1.0.0", description="Agent version")
    description: str = Field(..., description="Human-readable agent description")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    model_tier: ModelTier = Field(default=ModelTier.STANDARD, description="Required model tier")
    channels: List[ChannelType] = Field(
        default_factory=lambda: [ChannelType.WEB],
        description="Supported channels"
    )
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    author: str = Field(default="Salon Flow Team", description="Agent author")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {"use_enum_values": True}


class AgentContext(BaseModel):
    """Execution context for agent operations"""
    salon_id: str = Field(..., description="Salon identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    channel: ChannelType = Field(default=ChannelType.WEB, description="Request channel")
    language: str = Field(default="en", description="User language preference")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    
    model_config = {"use_enum_values": True}


class AgentRequest(BaseModel):
    """Standardized request for agent execution"""
    prompt: str = Field(..., description="User prompt/query")
    context: Optional[AgentContext] = None
    history: List[Dict[str, str]] = Field(default_factory=list, description="Conversation history")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Agent-specific parameters")
    use_cache: bool = Field(default=True, description="Enable caching")
    skip_guardrail: bool = Field(default=False, description="Skip guardrail check")


class AgentResponse(BaseModel):
    """Standardized response from agent execution"""
    success: bool = Field(default=True, description="Whether execution succeeded")
    message: str = Field(default="", description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Structured response data")
    suggestions: List[str] = Field(default_factory=list, description="Follow-up suggestions")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Response confidence")
    blocked: bool = Field(default=False, description="Whether blocked by guardrail")
    cached: bool = Field(default=False, description="Whether from cache")
    model_used: Optional[str] = Field(None, description="Model used for generation")
    execution_time_ms: Optional[float] = Field(None, description="Execution time in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AgentPlugin(ABC):
    """Base class for all agent plugins in the Microkernel architecture.
    
    All agents must inherit from this class to be discoverable and loadable
    by the plugin system. Provides standardized interface for:
    - Metadata declaration
    - Input validation
    - Execution
    - Response post-processing
    
    Example:
        class BookingAgentPlugin(AgentPlugin):
            @property
            def metadata(self) -> AgentMetadata:
                return AgentMetadata(
                    name="booking",
                    description="Handles appointment booking",
                    capabilities=["schedule", "reschedule", "cancel"],
                    model_tier=ModelTier.STANDARD
                )
            
            async def execute(self, request: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
                # Implementation
                pass
    """
    
    # Class-level registry for auto-registration
    _plugin_name: ClassVar[str] = ""
    
    @property
    @abstractmethod
    def metadata(self) -> AgentMetadata:
        """Return agent metadata describing capabilities and requirements.
        
        Returns:
            AgentMetadata: Complete agent metadata
        """
        pass
    
    @abstractmethod
    async def execute(
        self,
        request: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute agent logic with given request and context.
        
        Args:
            request: The request data containing prompt and parameters
            context: Optional execution context (salon_id, user_id, etc.)
            
        Returns:           Dict containing response data
        
        Raises:
            AgentExecutionError: If execution fails
        """
        pass
    
    async def validate_input(self, request: Dict[str, Any]) -> bool:
        """Validate input before execution.
        
        Override this method to implement custom validation logic.
        Default implementation always returns True.
        
        Args:
            request: The request to validate
            
        Returns:
            True if valid, False otherwise
        """
        return True
    
    async def post_process(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process response after execution.
        
        Override this method to implement custom post-processing.
        Default implementation returns response unchanged.
        
        Args:
            response: The response to post-process
            
        Returns:
            Post-processed response
        """
        return response
    
    async def health_check(self) -> bool:
        """Check if agent is healthy and ready to process requests.
        
        Returns:
            True if healthy, False otherwise
        """
        return True
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent.
        
        Override to provide custom system prompt.
        
        Returns:
            System prompt string
        """
        return f"You are a {self.metadata.name} assistant for a salon."


class AgentExecutionError(Exception):
    """Error during agent execution"""
    def __init__(self, agent_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        self.agent_name = agent_name
        self.message = message
        self.details = details or {}
        super().__init__(f"Agent '{agent_name}' execution error: {message}")


class AgentValidationError(Exception):
    """Error during agent input validation"""
    def __init__(self, agent_name: str, message: str, field: Optional[str] = None):
        self.agent_name = agent_name
        self.message = message
        self.field = field
        super().__init__(f"Agent '{agent_name}' validation error: {message}")


class AgentNotFoundError(Exception):
    """Error when agent is not found in registry"""
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        super().__init__(f"Agent '{agent_name}' not found in registry")
