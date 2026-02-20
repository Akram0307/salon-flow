"""Analytics API endpoints for AI Service"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
import structlog

from app.schemas.requests import AnalyticsRequest, ComplaintRequest
from app.schemas.responses import AIResponse, AnalyticsResponse
from app.services.agents import get_agent, AnalyticsAgent, CustomerSupportAgent

logger = structlog.get_logger()
router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.post("", response_model=AIResponse)
async def analyze_data(request: AnalyticsRequest):
    """Analyze business data with AI"""
    try:
        agent: AnalyticsAgent = get_agent("analytics")
        
        # In production, fetch actual data from API service
        mock_data = {
            "period": request.period,
            "filters": request.filters,
        }
        
        if request.analysis_type == "revenue":
            response = await agent.analyze_revenue(
                period=request.period,
                revenue_data=mock_data,
                context={"salon_id": request.salon_id},
            )
        elif request.analysis_type == "staff":
            response = await agent.analyze_staff_performance(
                staff_id=request.filters.get("staff_id") if request.filters else None,
                performance_data=mock_data,
                context={"salon_id": request.salon_id},
            )
        elif request.analysis_type == "demand":
            response = await agent.predict_demand(
                service_category=request.filters.get("category") if request.filters else None,
                historical_data=mock_data,
                context={"salon_id": request.salon_id},
            )
        else:
            response = await agent.generate(
                prompt=f"Analyze {request.analysis_type} for period {request.period}",
                context={"salon_id": request.salon_id, **(request.filters or {})},
            )
        
        return response
        
    except Exception as e:
        logger.error("analytics_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/{salon_id}")
async def get_insights(
    salon_id: str,
    insight_type: str = Query(default="general", description="Type: general, revenue, staff, trends"),
    period: str = Query(default="month", description="Time period"),
):
    """Get AI-generated business insights"""
    try:
        agent: AnalyticsAgent = get_agent("analytics")
        
        response = await agent.generate(
            prompt=f"Provide {insight_type} insights for the last {period}",
            context={"salon_id": salon_id},
        )
        
        return {
            "salon_id": salon_id,
            "insight_type": insight_type,
            "period": period,
            "insights": response.message,
            "confidence": response.confidence,
        }
        
    except Exception as e:
        logger.error("insights_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/complaint", response_model=AIResponse)
async def handle_complaint(request: ComplaintRequest):
    """Handle customer complaint with AI"""
    try:
        agent: CustomerSupportAgent = get_agent("support")
        
        response = await agent.handle_complaint(
            complaint=request.complaint,
            customer_info={"customer_id": request.customer_id},
            booking_details={"booking_id": request.booking_id} if request.booking_id else None,
            context={"salon_id": request.salon_id},
        )
        
        return response
        
    except Exception as e:
        logger.error("complaint_handling_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/{salon_id}")
async def get_recommendations(salon_id: str):
    """Get AI-powered business recommendations"""
    try:
        agent: AnalyticsAgent = get_agent("analytics")
        
        response = await agent.generate(
            prompt="Provide 5 actionable business recommendations to improve salon performance",
            context={"salon_id": salon_id},
        )
        
        return {
            "salon_id": salon_id,
            "recommendations": response.message,
            "confidence": response.confidence,
        }
        
    except Exception as e:
        logger.error("recommendations_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
