"""Chat API endpoints for AI Service"""
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, Dict, Any
import uuid
import structlog

from app.schemas.requests import ChatRequest, BookingSuggestionRequest, StylistRecommendationRequest
from app.schemas.responses import ChatResponse, AIResponse
from app.services.agents import get_agent, BookingAgent
from app.services.cache_service import get_cache_service

logger = structlog.get_logger()
router = APIRouter(prefix="/chat", tags=["Chat"])


# Session storage (in production, use Redis)
sessions: Dict[str, list] = {}


async def get_salon_context(salon_id: str) -> Dict[str, Any]:
    """Fetch salon context from API service"""
    # In production, fetch from API service
    # For now, return basic context
    return {
        "salon_id": salon_id,
        "timezone": "Asia/Kolkata",
        "currency": "INR",
    }


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint for AI conversations"""
    try:
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get session history
        history = sessions.get(session_id, [])
        
        # Get salon context
        context = await get_salon_context(request.salon_id)
        if request.context:
            context.update(request.context)
        
        # Get appropriate agent
        agent = get_agent(request.agent_type)
        
        # Generate response
        from app.services.openrouter_client import ChatMessage
        
        response = await agent.generate(
            prompt=request.message,
            context=context,
            history=[ChatMessage(**msg) for msg in history] if history else None,
        )
        
        # Update session history
        history.append({"role": "user", "content": request.message})
        if response.success:
            history.append({"role": "assistant", "content": response.message})
        sessions[session_id] = history[-10:]  # Keep last 10 messages
        
        return ChatResponse(
            response=response.message,
            session_id=session_id,
            agent_type=request.agent_type,
            suggestions=response.suggestions,
        )
        
    except Exception as e:
        logger.error("chat_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/booking/suggest", response_model=AIResponse)
async def suggest_booking(request: BookingSuggestionRequest):
    """Get AI-powered booking suggestions"""
    try:
        agent: BookingAgent = get_agent("booking")
        
        context = await get_salon_context(request.salon_id)
        
        response = await agent.suggest_time_slots(
            service_ids=request.service_ids,
            preferred_date=request.preferred_date,
            preferred_time=request.preferred_time,
            staff_preference=request.staff_preference,
            context=context,
        )
        
        return response
        
    except Exception as e:
        logger.error("booking_suggestion_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/booking/recommend-stylist", response_model=AIResponse)
async def recommend_stylist(request: StylistRecommendationRequest):
    """Get AI-powered stylist recommendations"""
    try:
        agent: BookingAgent = get_agent("booking")
        
        context = await get_salon_context(request.salon_id)
        
        response = await agent.recommend_stylist(
            service_ids=request.service_ids,
            customer_preferences=request.customer_preferences,
            context=context,
        )
        
        return response
        
    except Exception as e:
        logger.error("stylist_recommendation_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear chat session history"""
    if session_id in sessions:
        del sessions[session_id]
    return {"status": "cleared", "session_id": session_id}
