"""Marketing API endpoints for AI Service"""
from fastapi import APIRouter, HTTPException
import structlog

from app.schemas.requests import CampaignRequest, FeedbackRequest
from app.schemas.responses import AIResponse, CampaignResponse
from app.services.agents import get_agent, MarketingAgent, CustomerSupportAgent

logger = structlog.get_logger()
router = APIRouter(prefix="/marketing", tags=["Marketing"])


@router.post("/campaign", response_model=AIResponse)
async def generate_campaign(request: CampaignRequest):
    """Generate AI-powered marketing campaign"""
    try:
        agent: MarketingAgent = get_agent("marketing")
        
        response = await agent.generate_campaign(
            campaign_type=request.campaign_type,
            target_audience=request.target_audience,
            offer_details=request.offer_details,
            context={"salon_id": request.salon_id},
        )
        
        return response
        
    except Exception as e:
        logger.error("campaign_generation_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/birthday-offer")
async def generate_birthday_offer(
    salon_id: str,
    customer_name: str,
    customer_history: list,
):
    """Generate personalized birthday offer"""
    try:
        agent: MarketingAgent = get_agent("marketing")
        
        response = await agent.generate_birthday_offer(
            customer_name=customer_name,
            customer_history=customer_history,
            context={"salon_id": salon_id},
        )
        
        return response
        
    except Exception as e:
        logger.error("birthday_offer_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rebooking-reminder")
async def generate_rebooking_reminder(
    salon_id: str,
    customer_name: str,
    last_service: dict,
    recommended_services: list,
):
    """Generate rebooking reminder message"""
    try:
        agent: MarketingAgent = get_agent("marketing")
        
        response = await agent.generate_rebooking_reminder(
            customer_name=customer_name,
            last_service=last_service,
            recommended_services=recommended_services,
            context={"salon_id": salon_id},
        )
        
        return response
        
    except Exception as e:
        logger.error("rebooking_reminder_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback-request", response_model=AIResponse)
async def generate_feedback_request(request: FeedbackRequest):
    """Generate feedback request message"""
    try:
        agent: CustomerSupportAgent = get_agent("support")
        
        response = await agent.generate_feedback_request(
            service_details=request.service_details,
            customer_name=request.customer_name,
            context={"salon_id": request.salon_id},
        )
        
        return response
        
    except Exception as e:
        logger.error("feedback_request_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
