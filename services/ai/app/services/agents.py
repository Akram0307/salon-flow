"""AI Agents for Salon Management

Specialized agents for booking, marketing, analytics, and customer support.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
import structlog

from app.services.openrouter_client import OpenRouterClient, ChatMessage, get_openrouter_client
from app.services.cache_service import get_cache_service

logger = structlog.get_logger()


class AgentResponse(BaseModel):
    """Standard agent response"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    name: str = "base_agent"
    description: str = "Base agent class"
    system_prompt: str = "You are a helpful AI assistant."
    
    def __init__(self, client: Optional[OpenRouterClient] = None):
        self._client = client
        self._cache = None
    
    async def _get_client(self) -> OpenRouterClient:
        if self._client is None:
            self._client = await get_openrouter_client()
        return self._client
    
    async def _get_cache(self):
        if self._cache is None:
            self._cache = await get_cache_service()
        return self._cache
    
    async def generate(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        history: Optional[List[ChatMessage]] = None,
        use_cache: bool = True,
    ) -> AgentResponse:
        """Generate AI response with optional caching"""
        client = await self._get_client()
        
        # Build enhanced system prompt with context
        system_prompt = self.system_prompt
        if context:
            context_str = self._format_context(context)
            system_prompt = f"{self.system_prompt}\n\nCurrent Context:\n{context_str}"
        
        # Check cache if enabled
        if use_cache:
            cache = await self._get_cache()
            cache_data = {
                "agent": self.name,
                "prompt": prompt,
                "context": context,
            }
            cached = await cache.get(cache._generate_key(self.name, cache_data))
            if cached:
                logger.info("agent_cache_hit", agent=self.name)
                return AgentResponse.parse_raw(cached)
        
        # Generate response
        try:
            response = await client.chat(
                prompt=prompt,
                system_prompt=system_prompt,
                history=history,
            )
            
            result = AgentResponse(
                success=True,
                message=response.content,
                confidence=0.9
            )
            
            # Cache the result
            if use_cache:
                cache = await self._get_cache()
                await cache.set(
                    cache._generate_key(self.name, {"prompt": prompt, "context": context}),
                    result.json()
                )
            
            return result
            
        except Exception as e:
            logger.error("agent_generation_error", agent=self.name, error=str(e))
            return AgentResponse(
                success=False,
                message=f"Error generating response: {str(e)}",
                confidence=0.0
            )
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context for prompt injection"""
        lines = []
        for key, value in context.items():
            if isinstance(value, (dict, list)):
                import json
                lines.append(f"{key}: {json.dumps(value, indent=2)}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)


class BookingAgent(BaseAgent):
    """AI agent for booking assistance"""
    
    name = "booking_agent"
    description = "Handles appointment booking, rescheduling, and availability"
    system_prompt = """You are an intelligent booking assistant for a salon management system.
Your role is to help customers book appointments, check availability, and manage their bookings.

Guidelines:
- Be friendly and professional
- Suggest optimal time slots based on customer preferences
- Consider staff expertise when recommending stylists
- Handle rescheduling and cancellations gracefully
- Always confirm booking details before finalizing

When checking availability, consider:
- Staff schedules and breaks
- Service duration
- Buffer time between appointments
- Room/chair availability

Format your responses clearly with booking details when confirming appointments."""

    async def suggest_time_slots(
        self,
        service_ids: List[str],
        preferred_date: str,
        preferred_time: Optional[str] = None,
        staff_preference: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Suggest available time slots for booking"""
        prompt = f"""Suggest available time slots for the following booking request:

Services: {', '.join(service_ids)}
Preferred Date: {preferred_date}
Preferred Time: {preferred_time or 'Flexible'}
Staff Preference: {staff_preference or 'No preference'}

Please provide 3-5 suitable time slots with reasoning for each."""
        
        return await self.generate(prompt, context)

    async def recommend_stylist(
        self,
        service_ids: List[str],
        customer_preferences: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Recommend best stylist for services"""
        prompt = f"""Recommend the best stylist for these services:

Services: {', '.join(service_ids)}
Customer Preferences: {customer_preferences or 'None specified'}

Consider staff expertise, availability, and customer history.
Provide reasoning for your recommendation."""
        
        return await self.generate(prompt, context)

    async def handle_reschedule(
        self,
        booking_id: str,
        new_date: str,
        new_time: str,
        reason: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Handle booking reschedule request"""
        prompt = f"""Process a reschedule request:

Booking ID: {booking_id}
New Date: {new_date}
New Time: {new_time}
Reason: {reason or 'Not specified'}

Check availability and confirm the reschedule. If there are conflicts, suggest alternatives."""
        
        return await self.generate(prompt, context)


class MarketingAgent(BaseAgent):
    """AI agent for marketing automation"""
    
    name = "marketing_agent"
    description = "Handles marketing campaigns, promotions, and customer engagement"
    system_prompt = """You are a marketing specialist for a salon business.
Your role is to create engaging marketing content, design promotions, and improve customer retention.

Guidelines:
- Create personalized, relevant content
- Focus on customer value and benefits
- Use a warm, inviting tone
- Include clear calls to action
- Consider seasonal trends and events

Marketing channels:
- WhatsApp messages
- Email campaigns
- In-app notifications
- Social media posts

Always consider customer preferences and privacy when designing campaigns."""

    async def generate_campaign(
        self,
        campaign_type: str,
        target_audience: Dict[str, Any],
        offer_details: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Generate marketing campaign content"""
        prompt = f"""Create a marketing campaign:

Campaign Type: {campaign_type}
Target Audience: {target_audience}
Offer Details: {offer_details}

Generate:
1. Campaign headline
2. Main message (suitable for WhatsApp)
3. Call to action
4. Best time to send
5. Expected engagement tips"""
        
        return await self.generate(prompt, context)

    async def generate_birthday_offer(
        self,
        customer_name: str,
        customer_history: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Generate personalized birthday offer"""
        prompt = f"""Create a personalized birthday offer:

Customer Name: {customer_name}
Service History: {customer_history[:3] if customer_history else 'New customer'}

Generate a warm birthday message with a special offer tailored to their preferences.
Include a unique promo code and validity period."""
        
        return await self.generate(prompt, context)

    async def generate_rebooking_reminder(
        self,
        customer_name: str,
        last_service: Dict[str, Any],
        recommended_services: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Generate rebooking reminder message"""
        prompt = f"""Create a rebooking reminder:

Customer Name: {customer_name}
Last Service: {last_service}
Recommended Services: {', '.join(recommended_services)}

Generate a friendly reminder suggesting it's time for their next appointment.
Include available slots and a gentle call to action."""
        
        return await self.generate(prompt, context)


class AnalyticsAgent(BaseAgent):
    """AI agent for business analytics and insights"""
    
    name = "analytics_agent"
    description = "Provides business insights, reports, and recommendations"
    system_prompt = """You are a business analytics expert for salon management.
Your role is to analyze data, identify trends, and provide actionable insights.

Guidelines:
- Base insights on data, not assumptions
- Provide specific, actionable recommendations
- Consider seasonal patterns and trends
- Compare metrics against industry benchmarks
- Identify opportunities for growth

Key metrics to track:
- Revenue and growth
- Customer retention and lifetime value
- Staff performance and utilization
- Service popularity and profitability
- Peak hours and booking patterns

Present data in clear, understandable formats."""

    async def analyze_revenue(
        self,
        period: str,
        revenue_data: Dict[str, Any],
        comparison_period: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Analyze revenue trends"""
        prompt = f"""Analyze revenue performance:

Period: {period}
Revenue Data: {revenue_data}
Comparison Period: {comparison_period or 'Previous period'}

Provide:
1. Revenue summary
2. Growth/decline analysis
3. Top performing services
4. Recommendations for improvement"""
        
        return await self.generate(prompt, context)

    async def analyze_staff_performance(
        self,
        staff_id: Optional[str],
        performance_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Analyze staff performance"""
        prompt = f"""Analyze staff performance:

Staff ID: {staff_id or 'All staff'}
Performance Data: {performance_data}

Provide:
1. Performance summary
2. Strengths and areas for improvement
3. Utilization rate analysis
4. Customer satisfaction insights
5. Recommendations"""
        
        return await self.generate(prompt, context)

    async def predict_demand(
        self,
        service_category: Optional[str],
        historical_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Predict service demand"""
        prompt = f"""Predict service demand:

Service Category: {service_category or 'All services'}
Historical Data: {historical_data}

Provide:
1. Demand forecast for next 2 weeks
2. Peak times prediction
3. Staffing recommendations
4. Inventory considerations"""
        
        return await self.generate(prompt, context)


class CustomerSupportAgent(BaseAgent):
    """AI agent for customer support"""
    
    name = "support_agent"
    description = "Handles customer queries, complaints, and feedback"
    system_prompt = """You are a customer support specialist for a salon.
Your role is to handle customer inquiries, resolve complaints, and collect feedback.

Guidelines:
- Be empathetic and understanding
- Respond promptly and professionally
- Escalate serious issues to management
- Offer solutions and alternatives
- Follow up to ensure satisfaction

Common issues:
- Booking changes and cancellations
- Service quality concerns
- Pricing inquiries
- Membership and loyalty questions
- Staff feedback

Always aim to turn negative experiences into positive ones."""

    async def handle_complaint(
        self,
        complaint: str,
        customer_info: Dict[str, Any],
        booking_details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Handle customer complaint"""
        prompt = f"""Handle this customer complaint:

Complaint: {complaint}
Customer Info: {customer_info}
Booking Details: {booking_details or 'Not applicable'}

Provide:
1. Empathetic acknowledgment
2. Investigation steps
3. Resolution options
4. Compensation if appropriate
5. Follow-up plan"""
        
        return await self.generate(prompt, context)

    async def generate_feedback_request(
        self,
        service_details: Dict[str, Any],
        customer_name: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Generate feedback request message"""
        prompt = f"""Create a feedback request:

Service Details: {service_details}
Customer Name: {customer_name}

Generate a friendly message asking for feedback.
Include specific questions about their experience."""
        
        return await self.generate(prompt, context)


# Agent registry
AGENTS = {
    "booking": BookingAgent,
    "marketing": MarketingAgent,
    "analytics": AnalyticsAgent,
    "support": CustomerSupportAgent,
}


def get_agent(agent_type: str) -> BaseAgent:
    """Get agent instance by type"""
    agent_class = AGENTS.get(agent_type)
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_type}")
    return agent_class()
