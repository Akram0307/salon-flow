"""AI Service Proxy Router

Proxies requests to the AI service with shared authentication and context injection.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
import structlog

from app.core.config import settings
from app.api.dependencies import get_current_user, get_current_salon

router = APIRouter(prefix="/ai", tags=["AI Service"])
logger = structlog.get_logger()
# settings already imported


class ChatRequest(BaseModel):
    """Chat request to AI service"""
    message: str
    agent: Optional[str] = "booking"
    context: Optional[Dict[str, Any]] = None
    stream: Optional[bool] = False


class ChatResponse(BaseModel):
    """Chat response from AI service"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    confidence: float = 0.8


class AgentInfo(BaseModel):
    """Agent information"""
    type: str
    name: str
    description: str


class AgentsListResponse(BaseModel):
    """List of available agents"""
    agents: List[AgentInfo]


@router.get("/health", summary="Check AI service health")
async def check_ai_health():
    """Check if AI service is healthy"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{settings.AI_SERVICE_URL}/health")
            return response.json()
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


@router.get("/agents", response_model=AgentsListResponse, summary="List available AI agents")
async def list_agents(
    current_user = Depends(get_current_user),
    salon_id: str = Depends(get_current_salon)
):
    """List all available AI agents"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{settings.AI_SERVICE_URL}/agents")
            data = response.json()
            return AgentsListResponse(
                agents=[AgentInfo(**agent) for agent in data.get("agents", [])]
            )
        except Exception as e:
            logger.error("ai_service_error", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service unavailable"
            )


@router.post("/chat", response_model=ChatResponse, summary="Chat with AI agent")
async def chat_with_agent(
    request: ChatRequest,
    current_user = Depends(get_current_user),
    salon_id: str = Depends(get_current_salon)
):
    """Send a chat message to an AI agent"""
    
    # Inject salon context
    context = request.context or {}
    context["salon_id"] = salon_id
    context["user_id"] = current_user.get("uid")
    context["user_role"] = current_user.get("role")
    
    payload = {
        "message": request.message,
        "agent": request.agent,
        "context": context,
        "stream": request.stream
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{settings.AI_SERVICE_URL}/api/v1/chat",
                json=payload
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.text
                )
            
            return ChatResponse(**response.json())
            
        except httpx.TimeoutException:
            logger.error("ai_service_timeout")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="AI service request timed out"
            )
        except Exception as e:
            logger.error("ai_service_error", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"AI service error: {str(e)}"
            )


@router.post("/chat/stream", summary="Stream chat with AI agent")
async def stream_chat(
    request: ChatRequest,
    current_user = Depends(get_current_user),
    salon_id: str = Depends(get_current_salon)
):
    """Stream a chat response from an AI agent"""
    
    # Inject salon context
    context = request.context or {}
    context["salon_id"] = salon_id
    context["user_id"] = current_user.get("uid")
    
    payload = {
        "message": request.message,
        "agent": request.agent,
        "context": context,
        "stream": True
    }
    
    async def stream_generator():
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{settings.AI_SERVICE_URL}/api/v1/chat/stream",
                json=payload
            ) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk
    
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream"
    )


@router.post("/insights", summary="Get AI-generated business insights")
async def get_business_insights(
    insight_type: str = "revenue",
    period: str = "week",
    current_user = Depends(get_current_user),
    salon_id: str = Depends(get_current_salon)
):
    """Get AI-generated business insights"""
    
    # Only owners and managers can access insights
    if current_user.get("role") not in ["owner", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insights available for owners and managers only"
        )
    
    payload = {
        "insight_type": insight_type,
        "period": period,
        "salon_id": salon_id
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{settings.AI_SERVICE_URL}/api/v1/analytics/insights",
                json=payload
            )
            return response.json()
        except Exception as e:
            logger.error("ai_insights_error", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"AI service error: {str(e)}"
            )




@router.post("/agents/{agent_name}/invoke", summary="Invoke specific agent")
async def invoke_agent(
    agent_name: str,
    request: Dict[str, Any],
    current_user = Depends(get_current_user),
    salon_id: str = Depends(get_current_salon)
):
    """Invoke a specific agent with custom parameters.

    Args:
        agent_name: Name of the agent to invoke
        request: Custom parameters for the agent
        salon_id: Current salon ID from auth context
        current_user: Authenticated user context

    Returns:
        Agent response
    """
    # Inject salon context
    context = request.get("context", {})
    context["salon_id"] = salon_id
    context["user_id"] = current_user.get("uid")
    context["user_role"] = current_user.get("role")

    payload = {
        "agent": agent_name,
        "context": context,
        "params": request.get("params", {}),
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{settings.AI_SERVICE_URL}/api/v1/agents/{agent_name}/invoke",
                json=payload
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.text
                )

            return response.json()

        except httpx.TimeoutException:
            logger.error("ai_agent_timeout", agent=agent_name)
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Agent invocation timed out"
            )
        except Exception as e:
            logger.error("ai_agent_error", agent=agent_name, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Agent invocation error: {str(e)}"
            )

@router.post("/marketing/campaign", summary="Generate marketing campaign")
async def generate_campaign(
    campaign_type: str,
    target_segment: str,
    current_user = Depends(get_current_user),
    salon_id: str = Depends(get_current_salon)
):
    """Generate a marketing campaign"""
    
    # Only owners and managers can generate campaigns
    if current_user.get("role") not in ["owner", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Campaign generation available for owners and managers only"
        )
    
    payload = {
        "campaign_type": campaign_type,
        "target_segment": target_segment,
        "salon_id": salon_id
    }
    
    async with httpx.AsyncClient(timeout=45.0) as client:
        try:
            response = await client.post(
                f"{settings.AI_SERVICE_URL}/api/v1/marketing/campaign",
                json=payload
            )
            return response.json()
        except Exception as e:
            logger.error("ai_campaign_error", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"AI service error: {str(e)}"
            )
