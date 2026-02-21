"""AI Agents for Salon Management

Specialized agents for booking, marketing, analytics, customer support,
waitlist management, slot optimization, upselling, dynamic pricing,
bundle creation, inventory management, staff scheduling, and retention.
"""
from typing import Optional, List, Dict, Any, Tuple
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
import structlog

from app.services.openrouter_client import OpenRouterClient, ChatMessage, get_openrouter_client
from app.services.cache_service import get_cache_service
from app.services.guardrails import SalonGuardrail, get_guardrail, SALON_ONLY_INSTRUCTION

logger = structlog.get_logger()


class AgentResponse(BaseModel):
    """Standard agent response"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    blocked: bool = Field(default=False, description="Whether query was blocked by guardrail")


class BaseAgent(ABC):
    """Base class for all AI agents with salon-only guardrails"""
    
    name: str = "base_agent"
    description: str = "Base agent class"
    system_prompt: str = "You are a helpful AI assistant."
    
    def __init__(self, client: Optional[OpenRouterClient] = None):
        self._client = client
        self._cache = None
        self._guardrail: Optional[SalonGuardrail] = None
    
    async def _get_client(self) -> OpenRouterClient:
        if self._client is None:
            self._client = await get_openrouter_client()
        return self._client
    
    async def _get_cache(self):
        if self._cache is None:
            self._cache = await get_cache_service()
        return self._cache
    
    def _get_guardrail(self) -> SalonGuardrail:
        """Get guardrail instance"""
        if self._guardrail is None:
            self._guardrail = get_guardrail()
        return self._guardrail
    
    def _check_guardrail(self, query: str) -> Tuple[bool, str]:
        """Check if query passes salon-only guardrail
        
        Returns:
            Tuple[bool, str]: (is_valid, rejection_message_or_empty)
        """
        guardrail = self._get_guardrail()
        is_valid, reason = guardrail.validate_query(query)
        
        if not is_valid:
            logger.warning(
                "guardrail_blocked_query",
                agent=self.name,
                query_preview=query[:100],
                reason=reason
            )
            rejection = guardrail.get_rejection_response(query)
            return False, rejection
        
        return True, ""
    
    async def generate(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        history: Optional[List[ChatMessage]] = None,
        use_cache: bool = True,
        skip_guardrail: bool = False,
    ) -> AgentResponse:
        """Generate AI response with guardrail check and optional caching"""
        
        # Check guardrail unless explicitly skipped
        if not skip_guardrail:
            is_valid, rejection_message = self._check_guardrail(prompt)
            if not is_valid:
                return AgentResponse(
                    success=False,
                    message=rejection_message,
                    confidence=1.0,
                    blocked=True
                )
        
        client = await self._get_client()
        
        # Build enhanced system prompt with context and salon-only instruction
        system_prompt = f"{SALON_ONLY_INSTRUCTION}\n\n{self.system_prompt}"
        if context:
            context_str = self._format_context(context)
            system_prompt = f"{system_prompt}\n\nCurrent Context:\n{context_str}"
        
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


class WaitlistManagerAgent(BaseAgent):
    """AI agent for smart waitlist management"""
    
    name = "waitlist_agent"
    description = "Auto-fills cancellations and no-shows with prioritized waitlist customers"
    system_prompt = """You are an intelligent waitlist manager for a salon.
Your role is to maximize booking utilization by efficiently filling cancelled and no-show slots.

Guidelines:
- Prioritize waitlist by loyalty tier (Platinum > Gold > Silver > Bronze) and booking time
- Act quickly when slots open - time is critical
- Send personalized notifications via WhatsApp/SMS
- Include one-tap confirmation links for quick booking
- Implement escalation logic: notify next person if no response in 15 minutes

Priority Factors:
1. Customer loyalty tier (highest weight)
2. Time on waitlist (first come, first served within tier)
3. Service match compatibility
4. Customer history and preferences

Notification Best Practices:
- Be urgent but professional
- Include clear slot details (date, time, stylist, service)
- Provide one-tap confirmation link
- Set clear response deadline (15 minutes)
- Mention it's first-come-first-served after tier priority

Always aim to fill slots within 30 minutes of cancellation."""

    async def process_cancellation(
        self,
        cancelled_booking: Dict[str, Any],
        waitlist_entries: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Process a cancellation and identify best waitlist candidates"""
        prompt = f"""Process this cancelled booking and identify the best waitlist candidates:

Cancelled Booking:
- Booking ID: {cancelled_booking.get('id')}
- Service: {cancelled_booking.get('service_name')}
- Date: {cancelled_booking.get('date')}
- Time: {cancelled_booking.get('time')}
- Stylist: {cancelled_booking.get('staff_name')}
- Duration: {cancelled_booking.get('duration')} minutes

Waitlist Entries:
{self._format_waitlist(waitlist_entries)}

Analyze and provide:
1. Top 3 candidates ranked by priority (explain reasoning)
2. Notification message for each candidate
3. Escalation timeline (who to contact if no response)
4. Alternative suggestions if no perfect matches"""
        
        return await self.generate(prompt, context)

    async def prioritize_waitlist(
        self,
        service_id: str,
        preferred_date: str,
        waitlist_entries: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Prioritize waitlist for a specific service and date"""
        prompt = f"""Prioritize this waitlist for an opening:

Service ID: {service_id}
Preferred Date: {preferred_date}

Waitlist Entries:
{self._format_waitlist(waitlist_entries)}

Provide:
1. Ordered priority list with scores
2. Priority reasoning for each entry
3. Recommended notification sequence
4. Estimated fill probability"""
        
        return await self.generate(prompt, context)

    async def generate_notification(
        self,
        customer_info: Dict[str, Any],
        slot_details: Dict[str, Any],
        response_deadline_minutes: int = 15,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Generate personalized waitlist notification"""
        prompt = f"""Create a waitlist notification message:

Customer: {customer_info.get('name')}
Loyalty Tier: {customer_info.get('loyalty_tier', 'Standard')}
Preferred Services: {customer_info.get('preferred_services', [])}

Available Slot:
- Service: {slot_details.get('service_name')}
- Date: {slot_details.get('date')}
- Time: {slot_details.get('time')}
- Stylist: {slot_details.get('staff_name')}

Response Deadline: {response_deadline_minutes} minutes

Generate:
1. WhatsApp message (under 200 chars, include emoji)
2. SMS fallback message
3. One-tap confirmation link text
4. Urgency indicators without pressure"""
        
        return await self.generate(prompt, context)

    async def handle_escalation(
        self,
        original_customer: Dict[str, Any],
        next_candidates: List[Dict[str, Any]],
        slot_details: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Handle escalation when customer doesn't respond"""
        prompt = f"""Handle waitlist escalation:

Original Customer (no response):
- Name: {original_customer.get('name')}
- Tier: {original_customer.get('loyalty_tier')}

Next Candidates:
{self._format_waitlist(next_candidates)}

Slot Details: {slot_details}

Provide:
1. Escalation decision (move to next or extend time)
2. Notification for next candidate
3. Follow-up message for original customer
4. Updated timeline"""
        
        return await self.generate(prompt, context)

    def _format_waitlist(self, entries: List[Dict[str, Any]]) -> str:
        """Format waitlist entries for prompt"""
        if not entries:
            return "No waitlist entries"
        lines = []
        for i, entry in enumerate(entries, 1):
            lines.append(
                f"{i}. {entry.get('customer_name', 'Unknown')} "
                f"(Tier: {entry.get('loyalty_tier', 'Standard')}, "
                f"Waitlisted: {entry.get('created_at', 'N/A')}, "
                f"Service: {entry.get('service_name', 'Any')})"
            )
        return "\n".join(lines)


class SlotOptimizerAgent(BaseAgent):
    """AI agent for real-time slot optimization"""
    
    name = "slot_optimizer"
    description = "Detects and fills schedule gaps with targeted offers and dynamic adjustments"
    system_prompt = """You are a slot optimization specialist for a salon.
Your role is to maximize schedule utilization by detecting and filling gaps.

Guidelines:
- Monitor live booking data for empty slots
- Identify gaps of 30+ minutes as optimization opportunities
- Target nearby customers with personalized offers
- Suggest service combinations to fill gaps
- Consider dynamic service duration adjustments

Gap Detection Rules:
- Flag gaps >= 30 minutes
- Prioritize gaps during peak hours (10am-7pm)
- Consider stylist expertise and service compatibility
- Account for buffer time between services

Filling Strategies:
1. Target customers with appointments later that day (come early offer)
2. Notify nearby loyalty customers with flash deals
3. Suggest add-on services to adjacent bookings
4. Offer discounted combo services
5. Dynamic pricing for hard-to-fill slots

Always balance revenue optimization with customer experience."""

    async def detect_gaps(
        self,
        schedule_data: Dict[str, Any],
        staff_id: str,
        date: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Detect schedule gaps for optimization"""
        import json
        prompt = f"""Analyze this schedule for optimization opportunities:

Staff ID: {staff_id}
Date: {date}

Schedule Data:
{json.dumps(schedule_data, indent=2)}

Identify:
1. All gaps >= 30 minutes with times
2. Gap priority score (based on time of day, duration)
3. Potential revenue loss per gap
4. Recommended filling strategy for each gap
5. Adjacent booking opportunities"""
        
        return await self.generate(prompt, context)

    async def generate_gap_offer(
        self,
        gap_details: Dict[str, Any],
        target_customers: List[Dict[str, Any]],
        nearby_services: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Generate targeted offer for a schedule gap"""
        prompt = f"""Create a targeted offer for this schedule gap:

Gap Details:
- Start Time: {gap_details.get('start_time')}
- End Time: {gap_details.get('end_time')}
- Duration: {gap_details.get('duration_minutes')} minutes
- Staff: {gap_details.get('staff_name')}

Target Customers:
{self._format_target_customers(target_customers)}

Compatible Services:
{self._format_services(nearby_services)}

Generate:
1. Best filling strategy (early arrival, add-on, flash deal)
2. Personalized offer message for top 3 customers
3. Discount recommendation (if needed)
4. Service combination suggestions
5. Expected fill probability"""
        
        return await self.generate(prompt, context)

    async def suggest_service_combo(
        self,
        gap_duration: int,
        available_services: List[Dict[str, Any]],
        customer_preferences: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Suggest service combinations to fill a gap"""
        prompt = f"""Suggest service combinations to fill a {gap_duration} minute gap:

Available Services:
{self._format_services(available_services)}

Customer Preferences: {customer_preferences or 'General'}

Provide:
1. Top 3 service combinations that fit the duration
2. Revenue potential for each combination
3. Customer appeal score
4. Staff expertise match
5. Recommended pricing (regular vs promotional)"""
        
        return await self.generate(prompt, context)

    async def optimize_staff_schedule(
        self,
        staff_schedules: Dict[str, Any],
        date: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Optimize multiple staff schedules for the day"""
        import json
        prompt = f"""Optimize staff schedules for maximum utilization:

Date: {date}

Staff Schedules:
{json.dumps(staff_schedules, indent=2)}

Provide:
1. Overall utilization analysis
2. Gap summary across all staff
3. Reallocation suggestions (move bookings between staff)
4. Cross-staff filling opportunities
5. Priority actions ranked by impact"""
        
        return await self.generate(prompt, context)

    def _format_target_customers(self, customers: List[Dict[str, Any]]) -> str:
        """Format target customer list"""
        if not customers:
            return "No target customers identified"
        lines = []
        for c in customers[:5]:
            lines.append(
                f"- {c.get('name')} (Tier: {c.get('loyalty_tier')}, "
                f"Last Visit: {c.get('last_visit', 'N/A')})"
            )
        return "\n".join(lines)

    def _format_services(self, services) -> str:
        if not services:
            return "No services"
        lines = []
        if isinstance(services, dict):
            for name, price in services.items():
                lines.append(f"- {name}: Rs.{price}")
        elif isinstance(services, list):
            for s in services:
                if isinstance(s, dict):
                    lines.append(f"- {s.get('name', 'Unknown')}: Rs.{s.get('price', 'N/A')}")
                else:
                    lines.append(f"- {s}")
        return "\n".join(lines)

class UpsellEngineAgent(BaseAgent):
    """AI agent for intelligent upselling"""
    
    name = "upsell_agent"
    description = "Maximizes booking value through intelligent suggestions and personalized offers"
    system_prompt = """You are an upsell specialist for a salon.
Your role is to maximize booking value while enhancing customer experience.

Guidelines:
- Analyze customer history and preferences before suggesting
- Focus on value, not just price increase
- Personalize recommendations based on past services
- Suggest add-ons that complement booked services
- Create attractive combo offers
- Track and learn from upsell success rates

Upsell Strategies:
1. Service Add-ons: Suggest complementary services during booking
2. Service Upgrades: Recommend premium versions of booked services
3. Combo Offers: Create attractive bundles with discounts
4. Membership Upsell: Promote loyalty programs
5. Product Recommendations: Suggest aftercare products

Personalization Factors:
- Customer service history
- Loyalty tier and points
- Previous upsell responses
- Seasonal trends
- Special occasions (birthdays, anniversaries)

Always be helpful, not pushy. Focus on customer benefit."""

    async def analyze_upsell_potential(
        self,
        customer_id: str,
        current_booking: Dict[str, Any],
        customer_history: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Analyze upsell potential for a booking"""
        prompt = f"""Analyze upsell potential for this booking:

Customer ID: {customer_id}

Current Booking:
- Services: {current_booking.get('services')}
- Total: Rs.{current_booking.get('total', 0)}
- Date: {current_booking.get('date')}
- Stylist: {current_booking.get('staff_name')}

Customer History:
{self._format_history(customer_history)}

Provide:
1. Upsell potential score (0-100)
2. Top 3 upsell opportunities ranked by probability
3. Recommended approach for each opportunity
4. Expected value increase
5. Risk assessment (avoid over-upselling)"""
        
        return await self.generate(prompt, context)

    async def suggest_addons(
        self,
        booked_services: List[Dict[str, Any]],
        available_addons: List[Dict[str, Any]],
        customer_preferences: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Suggest add-on services for a booking"""
        prompt = f"""Suggest add-on services:

Booked Services:
{self._format_services(booked_services)}

Available Add-ons:
{self._format_services(available_addons)}

Customer Preferences: {customer_preferences or 'General'}

Provide:
1. Top 5 add-on suggestions with reasoning
2. Compatibility score for each (how well it complements)
3. Suggested pricing (bundle discount if applicable)
4. Message to present the add-on
5. Expected acceptance rate"""
        
        return await self.generate(prompt, context)

    async def recommend_upgrade(
        self,
        current_service: Dict[str, Any],
        upgrade_options: List[Dict[str, Any]],
        customer_profile: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Recommend service upgrade"""
        prompt = f"""Recommend a service upgrade:

Current Service:
- Name: {current_service.get('name')}
- Price: Rs.{current_service.get('price')}
- Duration: {current_service.get('duration')}min

Upgrade Options:
{self._format_services(upgrade_options)}

Customer Profile:
- Tier: {customer_profile.get('loyalty_tier', 'Standard')}
- Total Visits: {customer_profile.get('total_visits', 0)}
- Average Spend: Rs.{customer_profile.get('avg_spend', 0)}

Provide:
1. Best upgrade recommendation with reasoning
2. Value proposition for customer
3. Price difference justification
4. Personalized upgrade message
5. Success probability"""
        
        return await self.generate(prompt, context)

    async def create_combo_offer(
        self,
        base_services: List[Dict[str, Any]],
        customer_segment: str,
        occasion: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Create personalized combo offer"""
        prompt = f"""Create a combo offer:

Base Services:
{self._format_services(base_services)}

Customer Segment: {customer_segment}
Occasion: {occasion or 'General'}

Generate:
1. Combo name and description
2. Included services with individual prices
3. Combo price with discount percentage
4. Value proposition message
5. Validity period recommendation
6. Target customer profile
7. Expected conversion rate"""
        
        return await self.generate(prompt, context)

    async def track_upsell_success(
        self,
        upsell_data: List[Dict[str, Any]],
        period: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Analyze upsell success rates and provide insights"""
        import json
        prompt = f"""Analyze upsell performance:

Period: {period}
Upsell Data:
{json.dumps(upsell_data[:10], indent=2)}

Provide:
1. Overall success rate
2. Success by upsell type (addon, upgrade, combo)
3. Revenue impact analysis
4. Top performing upsells
5. Underperforming areas
6. Recommendations for improvement
7. A/B testing suggestions"""
        
        return await self.generate(prompt, context)

    def _format_history(self, history: List[Dict[str, Any]]) -> str:
        """Format customer history"""
        if not history:
            return "New customer - no history"
        lines = []
        for h in history[:5]:
            lines.append(
                f"- {h.get('date')}: {h.get('service')} (Rs.{h.get('price')})"
            )
        return "\n".join(lines)

    def _format_services(self, services) -> str:
        if not services:
            return "No services"
        lines = []
        if isinstance(services, dict):
            for name, price in services.items():
                lines.append(f"- {name}: Rs.{price}")
        elif isinstance(services, list):
            for s in services:
                if isinstance(s, dict):
                    lines.append(f"- {s.get('name', 'Unknown')}: Rs.{s.get('price', 'N/A')}")
                else:
                    lines.append(f"- {s}")
        return "\n".join(lines)

class DynamicPricingAgent(BaseAgent):
    """AI agent for dynamic pricing optimization"""
    
    name = "dynamic_pricing"
    description = "Analyzes demand patterns and suggests optimal pricing strategies"
    system_prompt = """You are a dynamic pricing specialist for a salon business.
Your role is to optimize pricing based on demand, competition, and market conditions.

Guidelines:
- Analyze historical booking patterns to identify demand trends
- Consider time-of-day, day-of-week, and seasonal variations
- Monitor competitor pricing in the local market
- Balance revenue optimization with customer satisfaction
- Avoid excessive price fluctuations

Pricing Strategies:
1. Peak Pricing: Increase prices during high-demand periods
2. Off-Peak Discounts: Offer discounts during slow periods
3. Festival Pricing: Special rates during festivals and holidays
4. Loyalty Pricing: Preferential rates for loyal customers
5. Last-Minute Deals: Dynamic pricing for unfilled slots

Factors to Consider:
- Historical demand data
- Staff utilization rates
- Local events and holidays
- Weather impact on appointments
- Competitor pricing analysis

Always provide data-driven recommendations with clear reasoning."""

    async def analyze_demand_patterns(
        self,
        historical_data: Dict[str, Any],
        service_category: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Analyze demand patterns for pricing optimization"""
        import json
        prompt = f"""Analyze demand patterns for dynamic pricing:

Service Category: {service_category or 'All services'}

Historical Data:
{json.dumps(historical_data, indent=2)}

Provide:
1. Peak hours/days identification
2. Low-demand periods
3. Seasonal trends
4. Demand elasticity analysis
5. Pricing opportunity recommendations"""
        
        return await self.generate(prompt, context)

    async def suggest_peak_pricing(
        self,
        peak_periods: List[Dict[str, Any]],
        current_prices: Dict[str, float],
        demand_forecast: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Suggest peak period pricing"""
        prompt = f"""Suggest peak pricing strategy:

Peak Periods:
{self._format_periods(peak_periods)}

Current Prices:
{self._format_prices(current_prices)}

Demand Forecast: {demand_forecast}

Provide:
1. Recommended price adjustments per period
2. Expected revenue impact
3. Customer acceptance probability
4. Implementation timeline
5. Monitoring metrics"""
        
        return await self.generate(prompt, context)

    async def suggest_offpeak_discounts(
        self,
        slow_periods: List[Dict[str, Any]],
        current_prices: Dict[str, float],
        utilization_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Suggest off-peak discount strategies"""
        prompt = f"""Suggest off-peak discount strategy:

Slow Periods:
{self._format_periods(slow_periods)}

Current Prices:
{self._format_prices(current_prices)}

Utilization Data: {utilization_data}

Provide:
1. Recommended discount percentages
2. Target services for discounts
3. Expected increase in bookings
4. Revenue impact analysis
5. Promotional messaging suggestions"""
        
        return await self.generate(prompt, context)

    async def analyze_competitor_pricing(
        self,
        competitor_data: List[Dict[str, Any]],
        our_services: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Analyze competitor pricing and suggest adjustments"""
        prompt = f"""Analyze competitor pricing:

Competitor Data:
{self._format_competitor_data(competitor_data)}

Our Services:
{self._format_services(our_services)}

Provide:
1. Price comparison analysis
2. Competitive positioning recommendations
3. Services to reprice
4. Value proposition improvements
5. Market positioning strategy"""
        
        return await self.generate(prompt, context)

    async def suggest_festival_pricing(
        self,
        festival: str,
        festival_dates: str,
        historical_festival_data: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Suggest festival-specific pricing"""
        prompt = f"""Create festival pricing strategy:

Festival: {festival}
Dates: {festival_dates}
Historical Data: {historical_festival_data or 'No historical data'}

Provide:
1. Special package recommendations
2. Price adjustments for festival period
3. Early bird offers
4. Group booking discounts
5. Marketing messaging
6. Expected demand surge"""
        
        return await self.generate(prompt, context)

    def _format_periods(self, periods: List[Dict[str, Any]]) -> str:
        if not periods:
            return "No periods specified"
        lines = []
        for p in periods:
            lines.append(f"- {p.get('day', 'N/A')} {p.get('time', 'N/A')}: Demand {p.get('demand_level', 'N/A')}")
        return "\n".join(lines)

    def _format_prices(self, prices: Dict[str, float]) -> str:
        if not prices:
            return "No prices specified"
        return "\n".join([f"- {k}: Rs.{v}" for k, v in prices.items()])

    def _format_competitor_data(self, data: List[Dict[str, Any]]) -> str:
        if not data:
            return "No competitor data"
        lines = []
        for c in data:
            lines.append(f"- {c.get('name')}: {c.get('service')} at Rs.{c.get('price')}")
        return "\n".join(lines)

    def _format_services(self, services) -> str:
        if not services:
            return "No services"
        lines = []
        if isinstance(services, dict):
            for name, price in services.items():
                lines.append(f"- {name}: Rs.{price}")
        elif isinstance(services, list):
            for s in services:
                if isinstance(s, dict):
                    lines.append(f"- {s.get('name', 'Unknown')}: Rs.{s.get('price', 'N/A')}")
                else:
                    lines.append(f"- {s}")
        return "\n".join(lines)

class BundleCreatorAgent(BaseAgent):
    """AI agent for creating attractive service bundles"""
    
    name = "bundle_creator"
    description = "Creates attractive service packages for various occasions and segments"
    system_prompt = """You are a bundle creation specialist for a salon.
Your role is to design attractive service packages that maximize value for customers and revenue for the salon.

Guidelines:
- Create bundles that offer genuine value
- Consider customer segments and occasions
- Ensure services in bundles are complementary
- Price bundles attractively while maintaining profitability
- Create clear, appealing bundle names and descriptions

Bundle Types:
1. Bridal Packages: Complete wedding beauty services
2. Groom Packages: Men's wedding grooming
3. Seasonal Packages: Festival and season-specific
4. Wellness Packages: Spa and relaxation focused
5. Quick Packages: Express services for busy customers
6. Premium Packages: Luxury service combinations

Pricing Strategy:
- Bundle discount: 10-20% off individual service total
- Clear value communication
- Tiered options (Basic, Premium, Luxury)
- Add-on options for customization

Always focus on customer benefit and experience."""

    async def create_bridal_bundle(
        self,
        budget_range: Dict[str, float],
        services_count: int = 5,
        preferences: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Create a bridal package"""
        prompt = f"""Create a bridal package:

Budget Range: Rs.{budget_range.get('min', 0)} - Rs.{budget_range.get('max', 50000)}
Number of Services: {services_count}
Preferences: {preferences or 'General bridal'}

Provide:
1. Package name
2. Included services with individual prices
3. Package price with discount
4. Timeline (pre-wedding, wedding day)
5. Trial session recommendations
6. Customization options
7. Marketing description"""
        
        return await self.generate(prompt, context)

    async def create_groom_bundle(
        self,
        budget_range: Dict[str, float],
        services_count: int = 3,
        preferences: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Create a groom package"""
        prompt = f"""Create a groom package:

Budget Range: Rs.{budget_range.get('min', 0)} - Rs.{budget_range.get('max', 20000)}
Number of Services: {services_count}
Preferences: {preferences or 'General groom'}

Provide:
1. Package name
2. Included services with individual prices
3. Package price with discount
4. Timeline recommendations
5. Add-on options
6. Marketing description"""
        
        return await self.generate(prompt, context)

    async def create_seasonal_bundle(
        self,
        season: str,
        occasion: Optional[str] = None,
        target_segment: str = "general",
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Create a seasonal package"""
        prompt = f"""Create a seasonal package:

Season: {season}
Occasion: {occasion or 'General seasonal'}
Target Segment: {target_segment}

Provide:
1. Package name
2. Included services
3. Seasonal benefits
4. Package price with discount
5. Validity period
6. Marketing messaging
7. Target customer profile"""
        
        return await self.generate(prompt, context)

    async def create_wellness_bundle(
        self,
        focus_area: str,
        duration_minutes: int = 120,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Create a wellness/spa package"""
        prompt = f"""Create a wellness package:

Focus Area: {focus_area}
Total Duration: {duration_minutes} minutes

Provide:
1. Package name
2. Included treatments
3. Duration breakdown
4. Benefits description
5. Package price
6. Add-on recommendations
7. Aftercare advice"""
        
        return await self.generate(prompt, context)

    def _format_booked_services(self, services) -> str:
        """Format booked services for display"""
        if not services:
            return "None"
        if isinstance(services, list):
            formatted = []
            for s in services:
                if isinstance(s, dict):
                    formatted.append(s.get('name', s.get('service', str(s))))
                else:
                    formatted.append(str(s))
            return ', '.join(formatted)
        return str(services)


    async def suggest_custom_combo(
        self,
        booked_services: List[str],
        customer_profile: Dict[str, Any],
        available_services: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Suggest custom combo based on booking"""
        prompt = f"""Suggest a custom combo:

Already Booked: {self._format_booked_services(booked_services)}
Customer Profile: {customer_profile}
Available Services: {len(available_services)} services

Provide:
1. Recommended combo name
2. Additional services to include
3. Combo price vs individual prices
4. Value proposition
5. Personalized message"""
        
        return await self.generate(prompt, context)


class InventoryIntelligenceAgent(BaseAgent):
    """AI agent for inventory management and optimization"""
    
    name = "inventory"
    description = "Monitors stock levels, predicts reorders, and optimizes inventory"
    system_prompt = """You are an inventory management specialist for a salon.
Your role is to ensure optimal stock levels, minimize waste, and predict inventory needs.

Guidelines:
- Monitor stock levels in real-time
- Predict reorder needs based on usage patterns
- Track expiry dates and minimize waste
- Optimize inventory costs
- Maintain service quality standards

Key Metrics:
- Stock turnover rate
- Days of inventory remaining
- Expiry alerts
- Usage variance
- Reorder point accuracy

Inventory Categories:
1. Hair products (shampoos, conditioners, colors)
2. Skin care products
3. Beauty tools and consumables
4. Spa and wellness products
5. Retail products

Always balance cost optimization with service quality."""

    async def monitor_stock_levels(
        self,
        inventory_data: List[Dict[str, Any]],
        threshold_config: Dict[str, int],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Monitor stock levels and identify alerts"""
        import json
        prompt = f"""Analyze inventory stock levels:

Inventory Data:
{json.dumps(inventory_data[:20], indent=2)}

Threshold Config: {threshold_config}

Provide:
1. Low stock alerts
2. Critical stock alerts
3. Overstocked items
4. Reorder recommendations
5. Estimated days of stock remaining"""
        
        return await self.generate(prompt, context)

    async def predict_reorder_needs(
        self,
        usage_history: List[Dict[str, Any]],
        current_stock: Dict[str, Any],
        lead_times: Dict[str, int],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Predict when items need reordering"""
        prompt = f"""Predict reorder needs:

Usage History (last 30 days):
{self._format_usage(usage_history[:10])}

Current Stock: {current_stock}
Lead Times (days): {lead_times}

Provide:
1. Items to reorder now
2. Items to reorder in next 7 days
3. Recommended order quantities
4. Safety stock recommendations
5. Cost optimization suggestions"""
        
        return await self.generate(prompt, context)

    async def check_expiry_alerts(
        self,
        inventory_data: List[Dict[str, Any]],
        days_threshold: int = 30,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Check for expiring products"""
        prompt = f"""Check expiry alerts:

Inventory Data:
{self._format_inventory(inventory_data)}

Days Threshold: {days_threshold} days

Provide:
1. Items expiring within threshold
2. Items already expired
3. Recommended actions (discount, use first, dispose)
4. Waste prevention strategies
5. Supplier notification needs"""
        
        return await self.generate(prompt, context)

    async def analyze_usage_patterns(
        self,
        usage_data: List[Dict[str, Any]],
        service_data: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Analyze product usage patterns"""
        import json
        prompt = f"""Analyze usage patterns:

Usage Data:
{json.dumps(usage_data[:15], indent=2)}

Service Data:
{json.dumps(list(service_data.items())[:10] if isinstance(service_data, dict) else service_data[:10], indent=2)}

Provide:
1. Most used products
2. Usage by service type
3. Usage trends (increasing/decreasing)
4. Seasonal patterns
5. Optimization recommendations"""
        
        return await self.generate(prompt, context)

    async def suggest_order_quantities(
        self,
        product_id: str,
        product_name: str,
        usage_rate: float,
        current_stock: int,
        lead_time: int,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Suggest optimal order quantity"""
        prompt = f"""Suggest order quantity:

Product: {product_name} (ID: {product_id})
Usage Rate: {usage_rate} units/day
Current Stock: {current_stock} units
Lead Time: {lead_time} days

Provide:
1. Recommended order quantity
2. Safety stock level
3. Reorder point
4. Expected stockout date if not ordered
5. Cost considerations"""
        
        return await self.generate(prompt, context)

    def _format_usage(self, usage: List[Dict[str, Any]]) -> str:
        if not usage:
            return "No usage data"
        lines = []
        for u in usage:
            lines.append(f"- {u.get('product')}: {u.get('quantity')} units on {u.get('date')}")
        return "\n".join(lines)

    def _format_inventory(self, inventory: List[Dict[str, Any]]) -> str:
        if not inventory:
            return "No inventory data"
        lines = []
        for i in inventory:
            lines.append(f"- {i.get('name')}: {i.get('quantity')} units, expires {i.get('expiry_date', 'N/A')}")
        return "\n".join(lines)


class StaffSchedulingAgent(BaseAgent):
    """AI agent for intelligent staff scheduling"""
    
    name = "scheduling"
    description = "Optimizes staff schedules based on demand and skills"
    system_prompt = """You are a staff scheduling specialist for a salon.
Your role is to create optimal schedules that balance business needs with staff satisfaction.

Guidelines:
- Match staff skills to service demand
- Consider staff preferences and availability
- Prevent overtime and burnout
- Ensure adequate coverage during peak hours
- Balance workload across team

Scheduling Factors:
1. Service demand by time/day
2. Staff expertise and certifications
3. Staff availability and preferences
4. Labor laws and break requirements
5. Customer preferences for specific stylists

Optimization Goals:
- Maximize utilization during peak hours
- Minimize idle time during slow periods
- Fair distribution of shifts
- Customer satisfaction with stylist availability

Always consider both business efficiency and staff wellbeing."""

    async def create_weekly_schedule(
        self,
        staff_list: List[Dict[str, Any]],
        demand_forecast: Dict[str, Any],
        constraints: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Create optimized weekly schedule"""
        import json
        prompt = f"""Create a weekly staff schedule:

Staff List:
{self._format_staff(staff_list)}

Demand Forecast:
{json.dumps(demand_forecast, indent=2)}

Constraints: {constraints}

Provide:
1. Day-by-day schedule for each staff
2. Shift assignments with times
3. Coverage analysis
4. Skill-demand matching
5. Recommendations for adjustments"""
        
        return await self.generate(prompt, context)

    async def optimize_shifts(
        self,
        current_schedule: Dict[str, Any],
        demand_patterns: Dict[str, Any],
        staff_preferences: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Optimize existing shift assignments"""
        prompt = f"""Optimize shift assignments:

Current Schedule:
{self._format_schedule(current_schedule)}

Demand Patterns: {demand_patterns}

Staff Preferences:
{self._format_preferences(staff_preferences)}

Provide:
1. Optimization recommendations
2. Shift swap suggestions
3. Coverage improvements
4. Staff satisfaction considerations
5. Expected utilization improvement"""
        
        return await self.generate(prompt, context)

    async def match_skills_to_demand(
        self,
        service_demand: List[Dict[str, Any]],
        staff_skills: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Match staff skills to service demand"""
        prompt = f"""Match staff skills to demand:

Service Demand:
{self._format_demand(service_demand)}

Staff Skills:
{self._format_skills(staff_skills)}

Provide:
1. Skill-demand gap analysis
2. Best staff for each service type
3. Cross-training recommendations
4. Hiring suggestions if gaps exist
5. Schedule optimization based on skills"""
        
        return await self.generate(prompt, context)

    async def handle_time_off_request(
        self,
        request: Dict[str, Any],
        current_schedule: Dict[str, Any],
        available_staff: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Handle time-off request and suggest coverage"""
        prompt = f"""Handle time-off request:

Request:
- Staff: {request.get('staff_name')}
- Date: {request.get('date')}
- Reason: {request.get('reason', 'Not specified')}

Current Schedule: {current_schedule}

Available Staff:
{self._format_staff(available_staff)}

Provide:
1. Approval recommendation
2. Coverage options
3. Schedule adjustments needed
4. Impact on appointments
5. Communication suggestions"""
        
        return await self.generate(prompt, context)

    async def prevent_overtime(
        self,
        timesheet_data: List[Dict[str, Any]],
        max_hours_per_week: int = 48,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Analyze timesheets and prevent overtime"""
        prompt = f"""Analyze timesheets for overtime prevention:

Timesheet Data:
{self._format_timesheet(timesheet_data)}

Max Hours/Week: {max_hours_per_week}

Provide:
1. Overtime risk alerts
2. Staff approaching overtime
3. Schedule adjustment recommendations
4. Alternative staffing options
5. Compliance considerations"""
        
        return await self.generate(prompt, context)

    def _format_staff(self, staff) -> str:
        if not staff:
            return "No staff available"
        lines = []
        if isinstance(staff, list):
            for s in staff:
                if isinstance(s, dict):
                    skills = s.get('skills', [])
                    skills_str = ', '.join(skills) if isinstance(skills, list) else str(skills)
                    lines.append(f"- {s.get('name', 'Unknown')} ({s.get('role', 'N/A')}): Skills: {skills_str}")
                else:
                    lines.append(f"- {s}")
        return "\n".join(lines)

    def _format_schedule(self, schedule: Dict[str, Any]) -> str:
        import json
        return json.dumps(schedule, indent=2)

    def _format_preferences(self, prefs) -> str:
        if not prefs:
            return "No preferences"
        lines = []
        if isinstance(prefs, dict):
            for staff_id, pref in prefs.items():
                lines.append(f"- {staff_id}: Prefers {pref}")
        elif isinstance(prefs, list):
            for p in prefs:
                if isinstance(p, dict):
                    lines.append(f"- {p.get('staff_name', 'Unknown')}: Prefers {p.get('preference', 'N/A')}")
                else:
                    lines.append(f"- {p}")
        return "\n".join(lines)

    def _format_demand(self, demand: List[Dict[str, Any]]) -> str:
        if not demand:
            return "No demand data"
        lines = []
        for d in demand:
            lines.append(f"- {d.get('service')}: {d.get('bookings')} bookings")
        return "\n".join(lines)

    def _format_skills(self, skills: List[Dict[str, Any]]) -> str:
        if not skills:
            return "No skills data"
        lines = []
        for s in skills:
            lines.append(f"- {s.get('staff_name')}: {', '.join(s.get('skills', []))}")
        return "\n".join(lines)

    def _format_timesheet(self, timesheet: List[Dict[str, Any]]) -> str:
        if not timesheet:
            return "No timesheet data"
        lines = []
        for t in timesheet:
            lines.append(f"- {t.get('staff_name')}: {t.get('hours_worked')}h this week")
        return "\n".join(lines)


class CustomerRetentionAgent(BaseAgent):
    """AI agent for customer retention and loyalty optimization"""
    
    name = "retention"
    description = "Identifies at-risk customers and creates retention strategies"
    system_prompt = """You are a customer retention specialist for a salon.
Your role is to identify at-risk customers and create strategies to keep them engaged.

Guidelines:
- Monitor customer visit frequency
- Identify declining engagement patterns
- Create personalized win-back campaigns
- Optimize loyalty program effectiveness
- Track customer satisfaction trends

Retention Indicators:
1. Decreasing visit frequency
2. Lower average spend
3. No response to promotions
4. Negative feedback
5. Competitor switching signals

Retention Strategies:
1. Personalized offers based on history
2. Loyalty tier upgrades
3. Exclusive previews and early access
4. Birthday and anniversary rewards
5. Re-engagement campaigns

Always focus on genuine customer value and relationship building."""

    async def identify_at_risk_customers(
        self,
        customer_data: List[Dict[str, Any]],
        visit_threshold_days: int = 45,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Identify customers at risk of churning"""
        import json
        prompt = f"""Identify at-risk customers:

Customer Data:
{json.dumps(customer_data[:15], indent=2)}

Visit Threshold: {visit_threshold_days} days

Provide:
1. High-risk customers (urgent attention)
2. Medium-risk customers (monitoring needed)
3. Risk factors for each
4. Recommended actions
5. Estimated churn probability"""
        
        return await self.generate(prompt, context)

    async def create_winback_campaign(
        self,
        customer_segment: str,
        last_visit_range: str,
        offer_budget: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Create win-back campaign for lapsed customers"""
        prompt = f"""Create a win-back campaign:

Customer Segment: {customer_segment}
Last Visit Range: {last_visit_range}
Offer Budget: Rs.{offer_budget}

Provide:
1. Campaign name and theme
2. Offer structure
3. Messaging (WhatsApp, SMS)
4. Timing recommendations
5. Expected response rate
6. Follow-up sequence"""
        
        return await self.generate(prompt, context)

    async def optimize_loyalty_program(
        self,
        loyalty_data: Dict[str, Any],
        customer_feedback: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Optimize loyalty program effectiveness"""
        prompt = f"""Optimize loyalty program:

Loyalty Data:
- Total Members: {loyalty_data.get('total_members')}
- Active Members: {loyalty_data.get('active_members')}
- Points Redeemed: {loyalty_data.get('points_redeemed')}

Customer Feedback:
{self._format_feedback(customer_feedback[:5])}

Provide:
1. Program health assessment
2. Engagement improvement suggestions
3. Reward structure recommendations
4. Tier benefits optimization
5. Communication strategy"""
        
        return await self.generate(prompt, context)

    async def create_reengagement_trigger(
        self,
        customer_profile: Dict[str, Any],
        trigger_event: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Create personalized re-engagement trigger"""
        prompt = f"""Create re-engagement trigger:

Customer Profile:
- Name: {customer_profile.get('name')}
- Last Visit: {customer_profile.get('last_visit')}
- Total Visits: {customer_profile.get('total_visits')}
- Loyalty Tier: {customer_profile.get('loyalty_tier')}
- Preferred Services: {customer_profile.get('preferred_services')}

Trigger Event: {trigger_event}

Provide:
1. Personalized message
2. Recommended offer
3. Channel (WhatsApp/SMS/Email)
4. Timing
5. Follow-up plan"""
        
        return await self.generate(prompt, context)

    async def analyze_churn_factors(
        self,
        churned_customers: List[Dict[str, Any]],
        active_customers: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Analyze factors contributing to customer churn"""
        import json
        prompt = f"""Analyze churn factors:

Churned Customers Sample:
{json.dumps(churned_customers[:5], indent=2)}

Active Customers Sample:
{json.dumps(active_customers[:5], indent=2)}

Provide:
1. Key churn indicators
2. Common churn reasons
3. Differences between churned and active
4. Prevention strategies
5. Early warning system recommendations"""
        
        return await self.generate(prompt, context)

    def _format_feedback(self, feedback) -> str:
        if not feedback:
            return "No feedback"
        lines = []
        if isinstance(feedback, list):
            for f in feedback:
                if isinstance(f, dict):
                    fb_text = f.get('feedback', '')
                    preview = str(fb_text)[:50] + "..." if len(str(fb_text)) > 50 else str(fb_text)
                    lines.append(f"- {f.get('customer', 'Anonymous')}: {preview}")
                else:
                    preview = str(f)[:50] + "..." if len(str(f)) > 50 else str(f)
                    lines.append(f"- {preview}")
        return "\n".join(lines)

# =============================================================================
# PHASE 2 AGENTS (HIGH PRIORITY)
# =============================================================================

class DemandPredictorAgent(BaseAgent):
    """AI agent for demand forecasting and staffing optimization.
    
    Analyzes historical booking data, seasonal patterns, and external factors
    to predict service demand and recommend optimal staffing levels.
    """
    
    name = "demand_predictor"
    description = "Forecasts service demand and predicts busy periods for staffing optimization"
    system_prompt = """You are a demand forecasting specialist for a salon business.
Your role is to analyze patterns and predict future demand to optimize operations.

Guidelines:
- Base predictions on historical data and trends
- Consider seasonal patterns, festivals, and local events
- Account for weather impact on appointments
- Factor in marketing campaigns and promotions
- Provide actionable staffing recommendations

Forecasting Factors:
1. Historical booking patterns by day/hour
2. Seasonal trends (wedding season, festivals, holidays)
3. Weather forecasts (rainy days affect walk-ins)
4. Local events (college events, exhibitions)
5. Marketing campaign impact
6. Customer loyalty patterns

Output Format:
- Confidence levels for predictions
- Specific time-based recommendations
- Staffing requirements with skills needed
- Revenue projections

Always provide data-driven insights with clear reasoning."""

    async def predict_weekly_demand(
        self,
        historical_data: Dict[str, Any],
        service_category: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Predict demand for the upcoming week.
        
        Args:
            historical_data: Past booking data, trends, and patterns
            service_category: Optional filter for specific service type
            context: Additional context (events, weather, promotions)
            
        Returns:
            7-day demand forecast with confidence levels
        """
        import json
        prompt = f"""Generate a 7-day demand forecast:

Historical Data:
{json.dumps(historical_data, indent=2)}

Service Category: {service_category or 'All services'}
Context: {context or 'None'}

Provide:
1. Day-by-day demand prediction (Low/Medium/High/Very High)
2. Expected booking volume per day
3. Peak hours for each day
4. Service-specific demand breakdown
5. Confidence level for each prediction
6. Key factors influencing the forecast"""
        
        return await self.generate(prompt, context)

    async def predict_peak_hours(
        self,
        date: str,
        historical_patterns: Dict[str, Any],
        special_events: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Identify peak hours for a specific date.
        
        Args:
            date: Target date for prediction
            historical_patterns: Past booking time distributions
            special_events: Any events affecting demand
            context: Additional context
            
        Returns:
            Peak hours identification with staffing recommendations
        """
        prompt = f"""Identify peak hours for {date}:

Historical Patterns:
{self._format_patterns(historical_patterns)}

Special Events: {special_events or 'None'}

Provide:
1. Predicted peak hours (with expected booking volume)
2. Moderate hours
3. Low-demand hours
4. Staffing recommendations per time slot
5. Break time suggestions for staff
6. Preparation activities during low hours"""
        
        return await self.generate(prompt, context)

    async def suggest_staffing(
        self,
        demand_forecast: Dict[str, Any],
        staff_availability: List[Dict[str, Any]],
        skill_requirements: Dict[str, int],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Recommend optimal staffing based on demand forecast.
        
        Args:
            demand_forecast: Predicted demand by time slot
            staff_availability: Available staff with their skills
            skill_requirements: Required skills per service type
            context: Additional context
            
        Returns:
            Staffing recommendations with cost optimization
        """
        import json
        prompt = f"""Create optimal staffing plan:

Demand Forecast:
{json.dumps(demand_forecast, indent=2)}

Staff Availability:
{self._format_staff_list(staff_availability)}

Skill Requirements: {skill_requirements}

Provide:
1. Recommended staff count per time slot
2. Skill mix requirements
3. Cost-effective scheduling options
4. Overtime risk assessment
5. Cross-training recommendations
6. Backup staff suggestions"""
        
        return await self.generate(prompt, context)

    async def analyze_seasonal_trends(
        self,
        yearly_data: Dict[str, Any],
        upcoming_events: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Analyze seasonal patterns and predict trends.
        
        Args:
            yearly_data: Historical data across seasons
            upcoming_events: Festivals, holidays, local events
            context: Additional context
            
        Returns:
            Seasonal trend analysis with preparation recommendations
        """
        prompt = f"""Analyze seasonal trends:

Yearly Data:
{self._format_yearly_data(yearly_data)}

Upcoming Events:
{self._format_events(upcoming_events)}

Provide:
1. Seasonal demand patterns
2. Festival impact analysis
3. Peak season predictions
4. Slow period identification
5. Preparation recommendations
6. Inventory and staffing adjustments"""
        
        return await self.generate(prompt, context)

    def _format_patterns(self, patterns: Dict[str, Any]) -> str:
        if not patterns:
            return "No pattern data"
        lines = []
        for key, value in patterns.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)

    def _format_staff_list(self, staff: List[Dict[str, Any]]) -> str:
        if not staff:
            return "No staff available"
        lines = []
        for s in staff:
            lines.append(f"- {s.get('name')}: {s.get('role')}, Skills: {', '.join(s.get('skills', []))}")
        return "\n".join(lines)

    def _format_yearly_data(self, data: Dict[str, Any]) -> str:
        import json
        return json.dumps(data, indent=2)

    def _format_events(self, events: List[Dict[str, Any]]) -> str:
        if not events:
            return "No upcoming events"
        lines = []
        for e in events:
            lines.append(f"- {e.get('date')}: {e.get('name')} ({e.get('type', 'event')})")
        return "\n".join(lines)


class WhatsAppConciergeAgent(BaseAgent):
    """AI agent for WhatsApp-based customer interaction.
    
    PLACEHOLDER: Full implementation requires Twilio WhatsApp credentials.
    Handles booking, rescheduling, and customer queries via WhatsApp.
    """
    
    name = "whatsapp_concierge"
    description = "Handles customer interactions via WhatsApp (Placeholder - requires Twilio credentials)"
    system_prompt = """You are a WhatsApp concierge for a salon.
Your role is to provide excellent customer service through WhatsApp messaging.

Guidelines:
- Keep messages concise and friendly
- Use emojis appropriately for warmth
- Provide quick, actionable responses
- Support multi-language (English, Hindi, Telugu)
- Handle booking, rescheduling, and queries
- Escalate complex issues to human support

Message Types:
1. Booking confirmations
2. Appointment reminders
3. Promotional offers
4. Service inquiries
5. Feedback collection

Response Format:
- Clear and concise
- Include relevant details
- Add call-to-action when needed
- Use WhatsApp buttons for quick replies

NOTE: This is a placeholder implementation. Full functionality requires Twilio WhatsApp API credentials."""

    _is_placeholder = True
    _placeholder_note = "Full implementation requires TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and WhatsApp-enabled phone number"

    async def handle_message(
        self,
        message: str,
        sender: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Process incoming WhatsApp message and generate response.
        
        Args:
            message: Incoming message text
            sender: Phone number of sender
            conversation_history: Previous messages in conversation
            context: Customer and salon context
            
        Returns:
            Response message and suggested actions
        """
        prompt = f"""Process this WhatsApp message:

From: {sender}
Message: {message}

Conversation History:
{self._format_history(conversation_history)}

Provide:
1. Intent classification (booking, query, reschedule, feedback, other)
2. Response message (under 200 chars, include emoji)
3. Suggested quick reply buttons
4. Action to take (if any)
5. Escalation needed (yes/no)

Note: This is a placeholder - full Twilio integration pending."""
        
        return await self.generate(prompt, context)

    async def send_booking_confirmation(
        self,
        booking_details: Dict[str, Any],
        customer_info: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Generate booking confirmation message for WhatsApp.
        
        Args:
            booking_details: Service, date, time, stylist info
            customer_info: Customer name and preferences
            context: Additional context
            
        Returns:
            Formatted confirmation message
        """
        prompt = f"""Create a WhatsApp booking confirmation:

Customer: {customer_info.get('name')}
Service: {booking_details.get('service_name')}
Date: {booking_details.get('date')}
Time: {booking_details.get('time')}
Stylist: {booking_details.get('staff_name')}
Price: Rs.{booking_details.get('price')}

Generate:
1. Confirmation message (friendly, include emoji)
2. Quick actions (Reschedule, Cancel, Add to Calendar)
3. Reminder schedule suggestion
4. Pre-appointment tips

Note: Placeholder - Twilio integration pending."""
        
        return await self.generate(prompt, context)

    async def send_reminder(
        self,
        booking_details: Dict[str, Any],
        hours_before: int = 24,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Generate appointment reminder message.
        
        Args:
            booking_details: Appointment information
            hours_before: Hours before appointment
            context: Additional context
            
        Returns:
            Reminder message with confirmation request
        """
        prompt = f"""Create an appointment reminder:

Booking: {booking_details.get('service_name')}
Date: {booking_details.get('date')}
Time: {booking_details.get('time')}
Stylist: {booking_details.get('staff_name')}
Hours Before: {hours_before}h

Generate:
1. Friendly reminder message
2. Confirmation request (Confirm/Reschedule/Cancel buttons)
3. Salon location reminder
4. Preparation tips if relevant

Note: Placeholder - Twilio integration pending."""
        
        return await self.generate(prompt, context)

    async def handle_language_switch(
        self,
        current_language: str,
        requested_language: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Handle language switching for multi-language support.
        
        Args:
            current_language: Current conversation language
            requested_language: Requested language (en/hi/te)
            context: Additional context
            
        Returns:
            Language switch confirmation
        """
        prompt = f"""Handle language switch:

Current: {current_language}
Requested: {requested_language}

Generate:
1. Confirmation in requested language
2. Brief help message in that language
3. Available commands list

Supported: English (en), Hindi (hi), Telugu (te)"""
        
        return await self.generate(prompt, context)

    def _format_history(self, history: Optional[List[Dict[str, Any]]]) -> str:
        if not history:
            return "No previous messages"
        lines = []
        for h in history[-5:]:
            lines.append(f"- {h.get('sender', 'Customer')}: {h.get('message', '')}")
        return "\n".join(lines)


# =============================================================================
# PHASE 3 AGENTS (MEDIUM PRIORITY)
# =============================================================================

class QualityAssuranceAgent(BaseAgent):
    """AI agent for service quality monitoring and compliance.
    
    Tracks quality metrics, monitors service standards, and generates
    audit reports for continuous improvement.
    """
    
    name = "quality_assurance"
    description = "Monitors service quality, tracks standards compliance, and generates audit reports"
    system_prompt = """You are a quality assurance specialist for a salon.
Your role is to maintain and improve service quality standards.

Guidelines:
- Monitor service delivery metrics
- Track customer satisfaction scores
- Identify quality improvement opportunities
- Ensure compliance with standards
- Generate actionable audit reports

Quality Metrics:
1. Customer satisfaction ratings
2. Service completion time accuracy
3. Rework/correction rates
4. Product usage consistency
5. Hygiene compliance

Standards to Monitor:
- Service delivery protocols
- Hygiene and safety standards
- Customer interaction quality
- Product application standards
- Equipment maintenance

Always provide specific, actionable recommendations for improvement."""

    async def monitor_service_quality(
        self,
        service_records: List[Dict[str, Any]],
        quality_metrics: Dict[str, Any],
        period: str = "weekly",
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Monitor and assess service quality metrics.
        
        Args:
            service_records: Recent service delivery records
            quality_metrics: Aggregated quality metrics
            period: Analysis period
            context: Additional context
            
        Returns:
            Quality assessment with improvement recommendations
        """
        import json
        prompt = f"""Analyze service quality for {period} review:

Service Records:
{json.dumps(service_records[:10], indent=2)}

Quality Metrics:
{json.dumps(quality_metrics, indent=2)}

Provide:
1. Overall quality score (0-100)
2. Top performing areas
3. Areas needing improvement
4. Staff performance comparison
5. Customer satisfaction trends
6. Specific improvement recommendations"""
        
        return await self.generate(prompt, context)

    async def check_compliance(
        self,
        compliance_checklist: Dict[str, Any],
        recent_incidents: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Verify compliance with salon standards.
        
        Args:
            compliance_checklist: Standards to verify
            recent_incidents: Any compliance incidents
            context: Additional context
            
        Returns:
            Compliance status with gaps and recommendations
        """
        prompt = f"""Check compliance status:

Compliance Checklist:
{self._format_checklist(compliance_checklist)}

Recent Incidents:
{self._format_incidents(recent_incidents)}

Provide:
1. Compliance score by category
2. Non-compliant items with severity
3. Immediate action items
4. Training recommendations
5. Process improvement suggestions"""
        
        return await self.generate(prompt, context)

    async def generate_audit_report(
        self,
        period: str,
        quality_data: Dict[str, Any],
        compliance_data: Dict[str, Any],
        staff_performance: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Generate comprehensive audit report.
        
        Args:
            period: Report period
            quality_data: Quality metrics and trends
            compliance_data: Compliance check results
            staff_performance: Individual staff metrics
            context: Additional context
            
        Returns:
            Formatted audit report with findings and recommendations
        """
        import json
        prompt = f"""Generate a comprehensive audit report for {period}:

Quality Data:
{json.dumps(quality_data, indent=2)}

Compliance Data:
{json.dumps(compliance_data, indent=2)}

Staff Performance:
{json.dumps(staff_performance[:5], indent=2)}

Provide:
1. Executive Summary
2. Quality Score Trend
3. Compliance Status
4. Top Performers
5. Areas of Concern
6. Improvement Recommendations
7. Action Items with Owners and Deadlines"""
        
        return await self.generate(prompt, context)

    async def track_customer_satisfaction(
        self,
        feedback_data: List[Dict[str, Any]],
        rating_trends: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Track and analyze customer satisfaction trends.
        
        Args:
            feedback_data: Recent customer feedback
            rating_trends: Historical rating trends
            context: Additional context
            
        Returns:
            Satisfaction analysis with insights
        """
        prompt = f"""Analyze customer satisfaction:

Recent Feedback:
{self._format_feedback(feedback_data[:10])}

Rating Trends:
{self._format_trends(rating_trends)}

Provide:
1. Average satisfaction score
2. Trend direction (improving/declining)
3. Common positive themes
4. Common complaints
5. Service-specific satisfaction
6. Actionable improvements"""
        
        return await self.generate(prompt, context)

    def _format_checklist(self, checklist: Dict[str, Any]) -> str:
        if not checklist:
            return "No checklist provided"
        lines = []
        for item, status in checklist.items():
            lines.append(f"- {item}: {'✓' if status else '✗'}")
        return "\n".join(lines)

    def _format_incidents(self, incidents: Optional[List[Dict[str, Any]]]) -> str:
        if not incidents:
            return "No recent incidents"
        lines = []
        for i in incidents:
            lines.append(f"- {i.get('date')}: {i.get('description')} ({i.get('severity', 'low')})")
        return "\n".join(lines)

    def _format_feedback(self, feedback: List[Dict[str, Any]]) -> str:
        if not feedback:
            return "No feedback data"
        lines = []
        for f in feedback:
            lines.append(f"- {f.get('customer', 'Anonymous')}: {f.get('rating', 'N/A')}/5 - {f.get('comment', '')[:50]}")
        return "\n".join(lines)

    def _format_trends(self, trends: Dict[str, Any]) -> str:
        import json
        return json.dumps(trends, indent=2)


class ResourceAllocatorAgent(BaseAgent):
    """AI agent for intelligent resource allocation.
    
    Manages chair/room assignments, resolves booking conflicts,
    and optimizes resource utilization across the salon.
    """
    
    name = "resource_allocator"
    description = "Allocates chairs, rooms, and equipment optimally while resolving conflicts"
    system_prompt = """You are a resource allocation specialist for a salon.
Your role is to optimize the use of physical resources and resolve conflicts.

Guidelines:
- Maximize resource utilization
- Minimize customer wait times
- Balance workload across resources
- Handle conflicts fairly
- Consider staff preferences

Resource Types:
1. Styling chairs (main service area)
2. Treatment rooms (facials, spa)
3. Washing stations
4. Waiting area
5. Equipment (dryers, steamers)

Allocation Factors:
- Service type and duration
- Staff assignment
- Equipment requirements
- Customer preferences
- Accessibility needs

Conflict Resolution:
- Prioritize by booking time
- Consider VIP status
- Offer alternatives
- Minimize disruption

Always aim for efficient, fair resource distribution."""

    async def allocate_chair(
        self,
        booking_request: Dict[str, Any],
        available_chairs: List[Dict[str, Any]],
        current_assignments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Assign optimal chair for a booking.
        
        Args:
            booking_request: Service, time, staff, customer info
            available_chairs: List of available chairs with features
            current_assignments: Current chair assignments
            context: Additional context
            
        Returns:
            Chair assignment with reasoning
        """
        prompt = f"""Allocate a chair for this booking:

Booking Request:
- Service: {booking_request.get('service_name')}
- Time: {booking_request.get('time')}
- Duration: {booking_request.get('duration')} min
- Staff: {booking_request.get('staff_name')}
- Customer: {booking_request.get('customer_name')}
- VIP: {booking_request.get('is_vip', False)}

Available Chairs:
{self._format_chairs(available_chairs)}

Current Assignments:
{self._format_assignments(current_assignments)}

Provide:
1. Recommended chair assignment
2. Reasoning for selection
3. Alternative options
4. Setup requirements
5. Next available time for this chair"""
        
        return await self.generate(prompt, context)

    async def allocate_room(
        self,
        service_requirements: Dict[str, Any],
        available_rooms: List[Dict[str, Any]],
        schedule: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Assign treatment room for a service.
        
        Args:
            service_requirements: Service type, duration, equipment needs
            available_rooms: List of rooms with features
            schedule: Current room schedule
            context: Additional context
            
        Returns:
            Room assignment with timing
        """
        prompt = f"""Allocate a treatment room:

Service Requirements:
- Type: {service_requirements.get('type')}
- Duration: {service_requirements.get('duration')} min
- Equipment: {service_requirements.get('equipment', [])}
- Privacy: {service_requirements.get('privacy', 'standard')}

Available Rooms:
{self._format_rooms(available_rooms)}

Current Schedule:
{self._format_schedule(schedule)}

Provide:
1. Recommended room
2. Time slot allocation
3. Setup/cleanup time needed
4. Equipment check
5. Alternative rooms if preferred is unavailable"""
        
        return await self.generate(prompt, context)

    async def resolve_conflicts(
        self,
        conflict_details: Dict[str, Any],
        involved_bookings: List[Dict[str, Any]],
        available_alternatives: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Resolve resource allocation conflicts.
        
        Args:
            conflict_details: Nature of the conflict
            involved_bookings: Bookings in conflict
            available_alternatives: Alternative resources/times
            context: Additional context
            
        Returns:
            Conflict resolution with communication suggestions
        """
        prompt = f"""Resolve this resource conflict:

Conflict: {conflict_details.get('description')}
Type: {conflict_details.get('type', 'double_booking')}

Involved Bookings:
{self._format_bookings(involved_bookings)}

Available Alternatives:
{self._format_alternatives(available_alternatives)}

Provide:
1. Recommended resolution
2. Priority reasoning
3. Affected customers and how to handle
4. Staff communication suggestions
5. Prevention measures for future"""
        
        return await self.generate(prompt, context)

    async def optimize_utilization(
        self,
        resource_usage_data: Dict[str, Any],
        demand_forecast: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Optimize overall resource utilization.
        
        Args:
            resource_usage_data: Current utilization metrics
            demand_forecast: Expected demand patterns
            context: Additional context
            
        Returns:
            Optimization recommendations
        """
        import json
        prompt = f"""Optimize resource utilization:

Current Utilization:
{json.dumps(resource_usage_data, indent=2)}

Demand Forecast:
{json.dumps(demand_forecast, indent=2)}

Provide:
1. Utilization analysis by resource
2. Underutilized resources
3. Overbooked resources
4. Reallocation recommendations
5. Efficiency improvement suggestions
6. ROI optimization strategies"""
        
        return await self.generate(prompt, context)

    def _format_chairs(self, chairs: List[Dict[str, Any]]) -> str:
        if not chairs:
            return "No chairs available"
        lines = []
        for c in chairs:
            lines.append(f"- Chair {c.get('id')}: {c.get('location')}, Features: {', '.join(c.get('features', []))}")
        return "\n".join(lines)

    def _format_assignments(self, assignments: Dict[str, Any]) -> str:
        if not assignments:
            return "No current assignments"
        lines = []
        for chair, booking in assignments.items():
            lines.append(f"- {chair}: {booking.get('staff')} ({booking.get('time')})")
        return "\n".join(lines)

    def _format_rooms(self, rooms: List[Dict[str, Any]]) -> str:
        if not rooms:
            return "No rooms available"
        lines = []
        for r in rooms:
            lines.append(f"- Room {r.get('id')}: {r.get('type')}, Equipment: {', '.join(r.get('equipment', []))}")
        return "\n".join(lines)

    def _format_schedule(self, schedule: Dict[str, Any]) -> str:
        import json
        return json.dumps(schedule, indent=2)

    def _format_bookings(self, bookings: List[Dict[str, Any]]) -> str:
        if not bookings:
            return "No bookings"
        lines = []
        for b in bookings:
            lines.append(f"- {b.get('customer_name')}: {b.get('service')} at {b.get('time')} (VIP: {b.get('is_vip', False)})")
        return "\n".join(lines)

    def _format_alternatives(self, alternatives: Dict[str, Any]) -> str:
        import json
        return json.dumps(alternatives, indent=2)


class ComplianceMonitorAgent(BaseAgent):
    """AI agent for regulatory compliance and safety monitoring.
    
    Monitors hygiene standards, safety protocols, and regulatory
    requirements for salon operations.
    """
    
    name = "compliance_monitor"
    description = "Monitors hygiene standards, safety protocols, and regulatory compliance"
    system_prompt = """You are a compliance and safety monitor for a salon.
Your role is to ensure adherence to hygiene, safety, and regulatory standards.

Guidelines:
- Monitor hygiene protocols continuously
- Track safety compliance
- Ensure regulatory requirements are met
- Generate compliance reports
- Alert on violations immediately

Compliance Areas:
1. Hygiene Standards
   - Tool sterilization
   - Surface sanitization
   - Hand hygiene
   - Product safety

2. Safety Protocols
   - Chemical handling
   - Electrical equipment safety
   - Fire safety
   - Emergency procedures

3. Regulatory Requirements
   - Licenses and permits
   - Staff certifications
   - Health department norms
   - Product compliance

Always prioritize customer and staff safety."""

    async def check_hygiene_standards(
        self,
        hygiene_checklist: Dict[str, Any],
        recent_audits: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Verify hygiene standards compliance.
        
        Args:
            hygiene_checklist: Hygiene items to verify
            recent_audits: Recent audit results
            context: Additional context
            
        Returns:
            Hygiene compliance status with recommendations
        """
        prompt = f"""Check hygiene standards compliance:

Hygiene Checklist:
{self._format_checklist(hygiene_checklist)}

Recent Audits:
{self._format_audits(recent_audits)}

Provide:
1. Overall hygiene score (0-100)
2. Compliant items
3. Non-compliant items with severity
4. Immediate action items
5. Training recommendations
6. Best practices to implement"""
        
        return await self.generate(prompt, context)

    async def track_safety_protocols(
        self,
        safety_incidents: List[Dict[str, Any]],
        protocol_adherence: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Monitor safety protocol adherence.
        
        Args:
            safety_incidents: Recent safety incidents
            protocol_adherence: Adherence metrics by protocol
            context: Additional context
            
        Returns:
            Safety status with improvement recommendations
        """
        prompt = f"""Track safety protocol adherence:

Safety Incidents:
{self._format_incidents(safety_incidents)}

Protocol Adherence:
{self._format_adherence(protocol_adherence)}

Provide:
1. Safety score by category
2. Incident analysis
3. High-risk areas
4. Protocol violations
5. Corrective actions
6. Prevention recommendations"""
        
        return await self.generate(prompt, context)

    async def generate_compliance_report(
        self,
        period: str,
        compliance_data: Dict[str, Any],
        violations: List[Dict[str, Any]],
        corrective_actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Generate comprehensive compliance report.
        
        Args:
            period: Report period
            compliance_data: Compliance metrics
            violations: Recorded violations
            corrective_actions: Actions taken
            context: Additional context
            
        Returns:
            Formatted compliance report
        """
        import json
        prompt = f"""Generate compliance report for {period}:

Compliance Data:
{json.dumps(compliance_data, indent=2)}

Violations:
{self._format_violations(violations)}

Corrective Actions:
{self._format_actions(corrective_actions)}

Provide:
1. Executive Summary
2. Compliance Score Trend
3. Hygiene Compliance Status
4. Safety Compliance Status
5. Regulatory Compliance Status
6. Violations Summary
7. Corrective Actions Status
8. Recommendations
9. Next Audit Schedule"""
        
        return await self.generate(prompt, context)

    async def check_certifications(
        self,
        staff_certifications: List[Dict[str, Any]],
        required_certifications: Dict[str, List[str]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Verify staff certifications are current.
        
        Args:
            staff_certifications: Current staff certifications
            required_certifications: Required certs by role
            context: Additional context
            
        Returns:
            Certification status with renewal reminders
        """
        prompt = f"""Check staff certifications:

Staff Certifications:
{self._format_certs(staff_certifications)}

Required by Role:
{self._format_required_certs(required_certifications)}

Provide:
1. Certification compliance status
2. Expired certifications
3. Expiring soon (30 days)
4. Missing certifications
5. Renewal schedule
6. Training recommendations"""
        
        return await self.generate(prompt, context)

    def _format_checklist(self, checklist: Dict[str, Any]) -> str:
        if not checklist:
            return "No checklist"
        lines = []
        for item, status in checklist.items():
            status_icon = "✓" if status else "✗"
            lines.append(f"- {item}: {status_icon}")
        return "\n".join(lines)

    def _format_audits(self, audits: List[Dict[str, Any]]) -> str:
        if not audits:
            return "No recent audits"
        lines = []
        for a in audits:
            lines.append(f"- {a.get('date')}: Score {a.get('score', 'N/A')}/100")
        return "\n".join(lines)

    def _format_incidents(self, incidents: List[Dict[str, Any]]) -> str:
        if not incidents:
            return "No incidents recorded"
        lines = []
        for i in incidents:
            lines.append(f"- {i.get('date')}: {i.get('type')} - {i.get('severity')}")
        return "\n".join(lines)

    def _format_adherence(self, adherence: Dict[str, Any]) -> str:
        if not adherence:
            return "No adherence data"
        lines = []
        for protocol, score in adherence.items():
            lines.append(f"- {protocol}: {score}%")
        return "\n".join(lines)

    def _format_violations(self, violations: List[Dict[str, Any]]) -> str:
        if not violations:
            return "No violations"
        lines = []
        for v in violations:
            lines.append(f"- {v.get('date')}: {v.get('category')} - {v.get('description')}")
        return "\n".join(lines)

    def _format_actions(self, actions: List[Dict[str, Any]]) -> str:
        if not actions:
            return "No actions recorded"
        lines = []
        for a in actions:
            lines.append(f"- {a.get('action')}: {a.get('status')} ({a.get('owner', 'Unassigned')})")
        return "\n".join(lines)

    def _format_certs(self, certs: List[Dict[str, Any]]) -> str:
        if not certs:
            return "No certifications on file"
        lines = []
        for c in certs:
            lines.append(f"- {c.get('staff_name')}: {c.get('certification')} (Expires: {c.get('expiry_date', 'N/A')})")
        return "\n".join(lines)

    def _format_required_certs(self, reqs: Dict[str, List[str]]) -> str:
        if not reqs:
            return "No requirements specified"
        lines = []
        for role, certs in reqs.items():
            lines.append(f"- {role}: {', '.join(certs)}")
        return "\n".join(lines)


# =============================================================================
# PHASE 4 AGENTS (STANDARD PRIORITY)
# =============================================================================

class VoiceReceptionistAgent(BaseAgent):
    """AI agent for voice call handling.
    
    PLACEHOLDER: Full implementation requires Twilio Voice credentials.
    Handles incoming calls, IVR, and voice-based booking.
    """
    
    name = "voice_receptionist"
    description = "Handles voice calls and IVR (Placeholder - requires Twilio Voice credentials)"
    system_prompt = """You are a voice receptionist for a salon.
Your role is to handle phone calls professionally and efficiently.

Guidelines:
- Speak clearly and warmly
- Keep responses concise for voice
- Use natural language patterns
- Handle multiple intents
- Escalate complex issues

Call Types:
1. Booking requests
2. Appointment confirmations
3. Rescheduling/cancellations
4. Service inquiries
5. Price inquiries
6. Complaints

IVR Flow:
- Greeting and language selection
- Intent detection
- Service routing
- Booking flow
- Confirmation

Response Format:
- Conversational and natural
- Clear confirmation numbers
- Repeat important details
- Offer SMS confirmation

NOTE: This is a placeholder implementation. Full functionality requires Twilio Voice API credentials."""

    _is_placeholder = True
    _placeholder_note = "Full implementation requires TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and Voice-enabled phone number"

    async def handle_call(
        self,
        call_details: Dict[str, Any],
        conversation_transcript: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Process incoming voice call.
        
        Args:
            call_details: Caller ID, time, previous calls
            conversation_transcript: Speech-to-text transcript
            context: Salon context
            
        Returns:
            Response text and action to take
        """
        prompt = f"""Handle this voice call:

Caller: {call_details.get('caller_id', 'Unknown')}
Time: {call_details.get('time')}
Previous Calls: {call_details.get('previous_calls', 'None')}

Transcript:
{conversation_transcript or 'Call just started'}

Provide:
1. Greeting/Response (natural, conversational)
2. Detected intent
3. Information needed
4. Next action (ask question, confirm, transfer)
5. TwiML suggestion

Note: Placeholder - Twilio Voice integration pending."""
        
        return await self.generate(prompt, context)

    async def generate_twiml(
        self,
        intent: str,
        response_text: str,
        options: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Generate TwiML response for voice call.
        
        Args:
            intent: Detected caller intent
            response_text: Text to speak
            options: Menu options if applicable
            context: Additional context
            
        Returns:
            TwiML markup for the response
        """
        prompt = f"""Generate TwiML response:

Intent: {intent}
Response Text: {response_text}
Options: {options or 'None'}

Provide:
1. TwiML markup (using <Say>, <Gather>, <Redirect> as needed)
2. Voice settings (language, voice type)
3. Gather options for input
4. Fallback handling

Note: Placeholder - Twilio integration pending."""
        
        return await self.generate(prompt, context)

    async def handle_booking_flow(
        self,
        booking_state: Dict[str, Any],
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Handle voice-based booking flow.
        
        Args:
            booking_state: Current state of booking conversation
            user_input: Latest user speech
            context: Additional context
            
        Returns:
            Next response and state update
        """
        prompt = f"""Continue voice booking flow:

Current State:
- Step: {booking_state.get('step', 'service_selection')}
- Service: {booking_state.get('service', 'Not selected')}
- Date: {booking_state.get('date', 'Not selected')}
- Time: {booking_state.get('time', 'Not selected')}

User Input: {user_input}

Provide:
1. Response to user
2. Next step in flow
3. Information to collect
4. Confirmation if complete

Note: Placeholder - Twilio integration pending."""
        
        return await self.generate(prompt, context)

    async def transfer_to_human(
        self,
        call_details: Dict[str, Any],
        reason: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Handle transfer to human receptionist.
        
        Args:
            call_details: Call information
            reason: Reason for transfer
            context: Additional context
            
        Returns:
            Transfer message and TwiML
        """
        prompt = f"""Generate transfer message:

Call Details: {call_details}
Transfer Reason: {reason}

Provide:
1. Hold message
2. Transfer TwiML
3. Fallback if no answer
4. Callback offer

Note: Placeholder - Twilio integration pending."""
        
        return await self.generate(prompt, context)


class FeedbackAnalyzerAgent(BaseAgent):
    """AI agent for customer feedback analysis.
    
    Analyzes sentiment, extracts insights, and tracks feedback trends
    to improve service quality.
    """
    
    name = "feedback_analyzer"
    description = "Analyzes customer feedback sentiment, extracts insights, and tracks trends"
    system_prompt = """You are a customer feedback analyst for a salon.
Your role is to extract actionable insights from customer feedback.

Guidelines:
- Analyze sentiment accurately
- Identify recurring themes
- Extract specific improvement suggestions
- Track trends over time
- Prioritize actionable feedback

Analysis Dimensions:
1. Sentiment (positive/negative/neutral)
2. Service quality
3. Staff performance
4. Facility/ambiance
5. Value for money
6. Overall experience

Output Format:
- Clear sentiment classification
- Key themes identified
- Specific quotes supporting analysis
- Actionable recommendations
- Priority ranking

Always provide specific, actionable insights."""

    async def analyze_sentiment(
        self,
        feedback_text: str,
        feedback_source: str = "review",
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Analyze sentiment of feedback text.
        
        Args:
            feedback_text: The feedback content
            feedback_source: Source (review, survey, whatsapp)
            context: Additional context
            
        Returns:
            Sentiment analysis with breakdown
        """
        prompt = f"""Analyze sentiment of this feedback:

Source: {feedback_source}
Feedback: "{feedback_text}"

Provide:
1. Overall sentiment (positive/negative/neutral/mixed)
2. Sentiment score (-1 to +1)
3. Emotion detected (happy, frustrated, disappointed, etc.)
4. Key phrases indicating sentiment
5. Service aspects mentioned
6. Staff mentioned (if any)
7. Urgency level (for negative feedback)"""
        
        return await self.generate(prompt, context)

    async def extract_insights(
        self,
        feedback_list: List[Dict[str, Any]],
        category: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Extract key insights from multiple feedback entries.
        
        Args:
            feedback_list: List of feedback with sentiment
            category: Optional category filter
            context: Additional context
            
        Returns:
            Aggregated insights and themes
        """
        prompt = f"""Extract insights from {len(feedback_list)} feedback entries:

Feedback Summary:
{self._format_feedback_list(feedback_list[:15])}

Category Focus: {category or 'All categories'}

Provide:
1. Top 5 positive themes
2. Top 5 negative themes
3. Most praised aspects
4. Most criticized aspects
5. Staff performance insights
6. Service-specific insights
7. Actionable recommendations"""
        
        return await self.generate(prompt, context)

    async def track_trends(
        self,
        historical_feedback: Dict[str, Any],
        current_period: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Track feedback trends over time.
        
        Args:
            historical_feedback: Feedback data by period
            current_period: Current analysis period
            context: Additional context
            
        Returns:
            Trend analysis with predictions
        """
        import json
        prompt = f"""Analyze feedback trends:

Historical Data:
{json.dumps(historical_feedback, indent=2)}

Current Period: {current_period}

Provide:
1. Sentiment trend (improving/declining/stable)
2. Period-over-period comparison
3. Emerging issues
4. Improving areas
5. Seasonal patterns
6. Predictions for next period
7. Recommended focus areas"""
        
        return await self.generate(prompt, context)

    async def generate_action_report(
        self,
        feedback_analysis: Dict[str, Any],
        priority_threshold: float = 0.7,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Generate action report from feedback analysis.
        
        Args:
            feedback_analysis: Analyzed feedback data
            priority_threshold: Threshold for high priority
            context: Additional context
            
        Returns:
            Actionable report with priorities
        """
        prompt = f"""Generate action report:

Feedback Analysis:
{self._format_analysis(feedback_analysis)}

Priority Threshold: {priority_threshold}

Provide:
1. High Priority Actions (immediate)
2. Medium Priority Actions (this week)
3. Low Priority Actions (this month)
4. Quick wins
5. Long-term improvements
6. Owner assignments
7. Expected impact of each action"""
        
        return await self.generate(prompt, context)

    def _format_feedback_list(self, feedback: List[Dict[str, Any]]) -> str:
        if not feedback:
            return "No feedback"
        lines = []
        for f in feedback:
            sentiment = f.get('sentiment', 'unknown')
            text = f.get('text', '')[:80]
            lines.append(f"- [{sentiment}] {text}...")
        return "\n".join(lines)

    def _format_analysis(self, analysis: Dict[str, Any]) -> str:
        import json
        return json.dumps(analysis, indent=2)


class VIPPriorityAgent(BaseAgent):
    """AI agent for VIP customer management.
    
    Handles priority booking, personalized perks, and VIP satisfaction
    tracking for high-value customers.
    """
    
    name = "vip_priority"
    description = "Manages VIP customer priority booking, perks, and satisfaction"
    system_prompt = """You are a VIP customer relations specialist for a salon.
Your role is to ensure premium experience for high-value customers.

Guidelines:
- Prioritize VIP bookings and requests
- Personalize service based on history
- Offer exclusive perks and benefits
- Track VIP satisfaction closely
- Anticipate VIP needs

VIP Tiers:
1. Platinum (highest)
2. Gold
3. Silver

VIP Benefits:
- Priority booking
- Preferred stylist guarantee
- Complimentary add-ons
- Exclusive offers
- Birthday/anniversary specials
- Flexible rescheduling

Personalization:
- Remember preferences
- Anticipate needs
- Surprise delights
- Dedicated point of contact

Always make VIPs feel valued and special."""

    async def handle_vip_booking(
        self,
        customer_profile: Dict[str, Any],
        booking_request: Dict[str, Any],
        availability: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Handle VIP booking with priority.
        
        Args:
            customer_profile: VIP customer details and tier
            booking_request: Requested service and time
            availability: Current availability
            context: Additional context
            
        Returns:
            Priority booking confirmation
        """
        prompt = f"""Handle VIP booking request:

Customer Profile:
- Name: {customer_profile.get('name')}
- Tier: {customer_profile.get('vip_tier')}
- Total Visits: {customer_profile.get('total_visits')}
- Total Spend: Rs.{customer_profile.get('total_spend')}
- Preferred Stylist: {customer_profile.get('preferred_stylist', 'None')}

Booking Request:
- Service: {booking_request.get('service_name')}
- Preferred Date: {booking_request.get('date')}
- Preferred Time: {booking_request.get('time')}

Availability:
{self._format_availability(availability)}

Provide:
1. Best available slot (priority access)
2. Stylist assignment (preferred if available)
3. VIP perks to include
4. Personalized message
5. Confirmation details"""
        
        return await self.generate(prompt, context)

    async def suggest_perks(
        self,
        customer_profile: Dict[str, Any],
        current_booking: Dict[str, Any],
        occasion: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Suggest personalized VIP perks.
        
        Args:
            customer_profile: VIP customer details
            current_booking: Current booking details
            occasion: Special occasion if any
            context: Additional context
            
        Returns:
            Personalized perk suggestions
        """
        prompt = f"""Suggest VIP perks:

Customer:
- Name: {customer_profile.get('name')}
- Tier: {customer_profile.get('vip_tier')}
- Preferences: {customer_profile.get('preferences', [])}
- History: {customer_profile.get('service_history', [])[:3]}

Current Booking: {current_booking.get('service_name')}
Occasion: {occasion or 'Regular visit'}

Provide:
1. Complimentary add-ons to offer
2. Exclusive services to suggest
3. Discount applicable
4. Surprise delight ideas
5. Personalized touches
6. Expected delight factor"""
        
        return await self.generate(prompt, context)

    async def track_vip_satisfaction(
        self,
        vip_customers: List[Dict[str, Any]],
        recent_visits: List[Dict[str, Any]],
        feedback_data: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Track VIP customer satisfaction.
        
        Args:
            vip_customers: List of VIP customers
            recent_visits: Recent VIP visit data
            feedback_data: VIP feedback entries
            context: Additional context
            
        Returns:
            VIP satisfaction report
        """
        prompt = f"""Track VIP satisfaction:

VIP Customers:
{self._format_vip_list(vip_customers)}

Recent Visits:
{self._format_visits(recent_visits[:10])}

Feedback:
{self._format_vip_feedback(feedback_data)}

Provide:
1. Overall VIP satisfaction score
2. At-risk VIPs (declining engagement)
3. Highly satisfied VIPs
4. Common requests/complaints
5. Retention recommendations
6. Upgrade opportunities"""
        
        return await self.generate(prompt, context)

    async def create_vip_campaign(
        self,
        target_tier: str,
        campaign_purpose: str,
        offer_budget: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Create VIP-exclusive campaign.
        
        Args:
            target_tier: VIP tier to target
            campaign_purpose: Campaign objective
            offer_budget: Budget per customer
            context: Additional context
            
        Returns:
            VIP campaign details
        """
        prompt = f"""Create VIP-exclusive campaign:

Target Tier: {target_tier}
Purpose: {campaign_purpose}
Budget per Customer: Rs.{offer_budget}

Provide:
1. Campaign name
2. Exclusive offer details
3. Personalized message template
4. Channel (WhatsApp/Call/Both)
5. Timing recommendations
6. Expected response rate
7. Follow-up plan"""
        
        return await self.generate(prompt, context)

    def _format_availability(self, availability: Dict[str, Any]) -> str:
        import json
        return json.dumps(availability, indent=2)

    def _format_vip_list(self, vips: List[Dict[str, Any]]) -> str:
        if not vips:
            return "No VIP customers"
        lines = []
        for v in vips:
            lines.append(f"- {v.get('name')} ({v.get('tier')}): {v.get('total_visits')} visits, Rs.{v.get('total_spend')}")
        return "\n".join(lines)

    def _format_visits(self, visits: List[Dict[str, Any]]) -> str:
        if not visits:
            return "No recent visits"
        lines = []
        for v in visits:
            lines.append(f"- {v.get('customer')}: {v.get('service')} on {v.get('date')}")
        return "\n".join(lines)

    def _format_vip_feedback(self, feedback: List[Dict[str, Any]]) -> str:
        if not feedback:
            return "No VIP feedback"
        lines = []
        for f in feedback:
            lines.append(f"- {f.get('customer')}: {f.get('rating')}/5 - {f.get('comment', '')[:50]}")
        return "\n".join(lines)


# =============================================================================
# PHASE 5 AGENTS (ENHANCEMENT)
# =============================================================================

class SocialMediaManagerAgent(BaseAgent):
    """AI agent for social media management.
    
    Handles content scheduling, engagement tracking, and social media
    strategy for salon marketing.
    """
    
    name = "social_media"
    description = "Manages social media content, scheduling, and engagement tracking"
    system_prompt = """You are a social media manager for a salon.
Your role is to create engaging content and grow the salon's social presence.

Guidelines:
- Create platform-appropriate content
- Maintain brand voice consistency
- Engage with followers authentically
- Track and improve engagement
- Leverage trends and hashtags

Platforms:
1. Instagram (primary)
2. Facebook
3. WhatsApp Status
4. Google Business

Content Types:
- Before/After transformations
- Stylist spotlights
- Service showcases
- Customer testimonials
- Festival posts
- Tips and tutorials

Posting Strategy:
- Best times per platform
- Hashtag research
- Engagement hooks
- Call-to-actions

Always focus on authentic engagement and brand building."""

    async def schedule_post(
        self,
        content_type: str,
        platform: str,
        target_audience: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Schedule social media post.
        
        Args:
            content_type: Type of content to post
            platform: Target platform
            target_audience: Audience demographics
            context: Additional context
            
        Returns:
            Post content and scheduling recommendation
        """
        prompt = f"""Create a social media post:

Content Type: {content_type}
Platform: {platform}
Target Audience: {target_audience}

Provide:
1. Post caption (platform-optimized)
2. Hashtags (relevant and trending)
3. Best posting time
4. Image/video suggestion
5. Engagement hook
6. Call-to-action
7. Cross-posting recommendations"""
        
        return await self.generate(prompt, context)

    async def generate_content_calendar(
        self,
        month: str,
        key_events: List[Dict[str, Any]],
        content_goals: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Generate monthly content calendar.
        
        Args:
            month: Target month
            key_events: Festivals, events, promotions
            content_goals: Content objectives
            context: Additional context
            
        Returns:
            Content calendar with post schedule
        """
        prompt = f"""Create content calendar for {month}:

Key Events:
{self._format_events(key_events)}

Content Goals:
{self._format_goals(content_goals)}

Provide:
1. Weekly content themes
2. Post schedule (date, platform, type)
3. Festival/event posts
4. Engagement posts
5. Promotional posts
6. Content gaps to fill
7. Hashtag strategy"""
        
        return await self.generate(prompt, context)

    async def track_engagement(
        self,
        platform: str,
        engagement_data: Dict[str, Any],
        period: str = "weekly",
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Track and analyze social media engagement.
        
        Args:
            platform: Platform to analyze
            engagement_data: Metrics and interactions
            period: Analysis period
            context: Additional context
            
        Returns:
            Engagement analysis with recommendations
        """
        import json
        prompt = f"""Analyze {platform} engagement for {period}:

Engagement Data:
{json.dumps(engagement_data, indent=2)}

Provide:
1. Engagement rate trend
2. Top performing posts
3. Underperforming content
4. Follower growth
5. Best posting times identified
6. Content recommendations
7. Hashtag performance"""
        
        return await self.generate(prompt, context)

    async def respond_to_comment(
        self,
        comment: str,
        post_context: str,
        sentiment: str = "neutral",
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Generate response to social media comment.
        
        Args:
            comment: The comment to respond to
            post_context: What the post was about
            sentiment: Comment sentiment
            context: Additional context
            
        Returns:
            Appropriate response
        """
        prompt = f"""Respond to this social media comment:

Post Context: {post_context}
Comment: "{comment}"
Sentiment: {sentiment}

Provide:
1. Response (friendly, professional)
2. Tone adjustment if needed
3. Follow-up action (if any)
4. Emoji usage suggestion"""
        
        return await self.generate(prompt, context)

    def _format_events(self, events: List[Dict[str, Any]]) -> str:
        if not events:
            return "No key events"
        lines = []
        for e in events:
            lines.append(f"- {e.get('date')}: {e.get('name')} ({e.get('type', 'event')})")
        return "\n".join(lines)

    def _format_goals(self, goals: Dict[str, Any]) -> str:
        if not goals:
            return "No specific goals"
        lines = []
        for goal, target in goals.items():
            lines.append(f"- {goal}: {target}")
        return "\n".join(lines)


class ImageCreativesGeneratorAgent(BaseAgent):
    """AI agent for generating marketing images and creatives.
    
    Uses gemini-3-pro-image-preview model for generating marketing
    images, festival posters, and promotional creatives.
    """
    
    name = "image_creatives"
    description = "Generates marketing images and creatives using AI image generation"
    system_prompt = """You are a creative image generation specialist for a salon.
Your role is to create visually appealing marketing creatives.

Guidelines:
- Create on-brand visual content
- Optimize for social media formats
- Include salon branding elements
- Design for engagement
- Follow platform specifications

Creative Types:
1. Festival posters
2. Service showcases
3. Before/After templates
4. Promotional banners
5. Social media posts
6. Story templates

Design Principles:
- Clean, professional aesthetic
- Consistent brand colors
- Clear typography
- Eye-catching visuals
- Appropriate for platform

Always provide detailed image prompts for generation."""

    # Use specific model for image generation
    _preferred_model = "google/gemini-3-pro-image-preview"

    async def generate_marketing_image(
        self,
        content_type: str,
        brand_elements: Dict[str, Any],
        target_platform: str = "instagram",
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Generate marketing image prompt and specifications.
        
        Args:
            content_type: Type of marketing content
            brand_elements: Colors, logo, style guide
            target_platform: Target social platform
            context: Additional context
            
        Returns:
            Image generation prompt and specs
        """
        prompt = f"""Create a marketing image for:

Content Type: {content_type}
Target Platform: {target_platform}

Brand Elements:
- Colors: {brand_elements.get('colors', [])}
- Style: {brand_elements.get('style', 'modern')}
- Logo Placement: {brand_elements.get('logo_position', 'bottom-right')}

Provide:
1. Detailed image generation prompt
2. Image dimensions for platform
3. Text overlay suggestions
4. Color palette to use
5. Style notes
6. Variations to try

Model: {self._preferred_model}"""
        
        return await self.generate(prompt, context)

    async def create_festival_poster(
        self,
        festival: str,
        offer_details: Dict[str, Any],
        design_preferences: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Create festival promotional poster.
        
        Args:
            festival: Festival name
            offer_details: Promotion details
            design_preferences: Design style preferences
            context: Additional context
            
        Returns:
            Festival poster prompt and design
        """
        prompt = f"""Create a festival poster for {festival}:

Offer Details:
- Title: {offer_details.get('title')}
- Discount: {offer_details.get('discount')}
- Validity: {offer_details.get('validity')}
- Services: {offer_details.get('services', [])}

Design Preferences: {design_preferences or 'Festive, vibrant'}

Provide:
1. Image generation prompt (detailed)
2. Text elements to overlay
3. Color scheme
4. Layout suggestions
5. Multiple size variations
6. Caption for social media

Model: {self._preferred_model}"""
        
        return await self.generate(prompt, context)

    async def create_service_showcase(
        self,
        service_details: Dict[str, Any],
        showcase_type: str = "carousel",
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Create service showcase creative.
        
        Args:
            service_details: Service information
            showcase_type: Type of showcase
            context: Additional context
            
        Returns:
            Service showcase design
        """
        prompt = f"""Create a service showcase:

Service: {service_details.get('name')}
Description: {service_details.get('description')}
Price: Rs.{service_details.get('price')}
Duration: {service_details.get('duration')} minutes

Showcase Type: {showcase_type}

Provide:
1. Image generation prompt
2. Before/After concept (if applicable)
3. Text overlays
4. Carousel slides (if applicable)
5. Call-to-action element
6. Hashtag suggestions

Model: {self._preferred_model}"""
        
        return await self.generate(prompt, context)

    async def create_story_template(
        self,
        template_type: str,
        brand_colors: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Create Instagram/WhatsApp story template.
        
        Args:
            template_type: Type of story template
            brand_colors: Brand color palette
            context: Additional context
            
        Returns:
            Story template design
        """
        prompt = f"""Create a story template:

Template Type: {template_type}
Brand Colors: {brand_colors}

Provide:
1. Background image prompt
2. Text placeholder positions
3. Interactive elements (polls, questions)
4. Swipe-up link design
5. Animation suggestions
6. Multiple variations

Model: {self._preferred_model}"""
        
        return await self.generate(prompt, context)


class ContentWriterAgent(BaseAgent):
    """AI agent for content writing.
    
    Creates blog posts, social media captions, ad copy, and
    other marketing content for the salon.
    """
    
    name = "content_writer"
    description = "Creates blog posts, social captions, ad copy, and marketing content"
    system_prompt = """You are a content writer for a salon.
Your role is to create engaging, persuasive content for marketing.

Guidelines:
- Write in brand voice (friendly, professional)
- Optimize for platform and audience
- Include clear calls-to-action
- Use storytelling techniques
- Maintain consistency

Content Types:
1. Blog posts (hair care, beauty tips)
2. Social media captions
3. Ad copy (Facebook, Instagram)
4. Email newsletters
5. WhatsApp broadcasts
6. Website copy

Writing Style:
- Conversational yet professional
- Benefit-focused
- Local relevance (Kurnool context)
- Multi-language capable (EN/HI/TE)

Always create content that engages and converts."""

    async def write_blog_post(
        self,
        topic: str,
        target_audience: str,
        word_count: int = 800,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Write blog post content.
        
        Args:
            topic: Blog topic
            target_audience: Target reader segment
            word_count: Target word count
            context: Additional context
            
        Returns:
            Blog post content
        """
        prompt = f"""Write a blog post:

Topic: {topic}
Target Audience: {target_audience}
Word Count: ~{word_count} words

Provide:
1. Catchy headline
2. Meta description (for SEO)
3. Introduction hook
4. Main content with subheadings
5. Practical tips/advice
6. Call-to-action
7. Suggested images
8. Tags/categories"""
        
        return await self.generate(prompt, context)

    async def write_caption(
        self,
        post_type: str,
        platform: str,
        key_message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Write social media caption.
        
        Args:
            post_type: Type of post
            platform: Target platform
            key_message: Main message to convey
            context: Additional context
            
        Returns:
            Platform-optimized caption
        """
        prompt = f"""Write a social media caption:

Post Type: {post_type}
Platform: {platform}
Key Message: {key_message}

Provide:
1. Main caption (platform-optimized length)
2. Hook/first line
3. Hashtags (relevant, mix of popular and niche)
4. Emoji suggestions
5. Call-to-action
6. Alternative versions (short/long)"""
        
        return await self.generate(prompt, context)

    async def write_ad_copy(
        self,
        product_service: str,
        campaign_goal: str,
        target_audience: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Write advertisement copy.
        
        Args:
            product_service: What's being advertised
            campaign_goal: Campaign objective
            target_audience: Audience demographics
            context: Additional context
            
        Returns:
            Ad copy variations
        """
        prompt = f"""Write ad copy:

Product/Service: {product_service}
Campaign Goal: {campaign_goal}
Target Audience: {target_audience}

Provide:
1. Primary headline (attention-grabbing)
2. Primary ad copy
3. Short version (for stories/reels)
4. Long version (for feed)
5. Call-to-action options
6. A/B test variations
7. Key selling points to highlight"""
        
        return await self.generate(prompt, context)

    async def write_newsletter(
        self,
        newsletter_type: str,
        content_highlights: List[str],
        subscriber_segment: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Write email newsletter content.
        
        Args:
            newsletter_type: Type of newsletter
            content_highlights: Key content to include
            subscriber_segment: Target segment
            context: Additional context
            
        Returns:
            Newsletter content
        """
        prompt = f"""Write an email newsletter:

Type: {newsletter_type}
Content Highlights: {content_highlights}
Subscriber Segment: {subscriber_segment}

Provide:
1. Subject line options (3 variations)
2. Preview text
3. Newsletter body
4. Section breaks
5. Personalization tokens
6. Call-to-action
7. P.S. line"""
        
        return await self.generate(prompt, context)


class ReviewMonitorAgent(BaseAgent):
    """AI agent for online review monitoring and management.
    
    Tracks reviews across platforms, generates responses, and
    alerts on negative feedback requiring attention.
    """
    
    name = "review_monitor"
    description = "Monitors online reviews, generates responses, and alerts on negative feedback"
    system_prompt = """You are a review management specialist for a salon.
Your role is to monitor, respond to, and improve online reviews.

Guidelines:
- Monitor all review platforms
- Respond promptly to all reviews
- Handle negative reviews professionally
- Encourage positive reviews
- Track review trends

Review Platforms:
1. Google Business
2. Justdial
3. Facebook
4. Instagram (comments)
5. WhatsApp feedback

Response Strategy:
- Thank positive reviewers
- Address negative concerns
- Offer resolution offline
- Maintain professional tone
- Invite to return

Alert Triggers:
- Rating below 3 stars
- Specific complaints
- Staff mentions
- Safety concerns

Always protect brand reputation while being authentic."""

    async def track_reviews(
        self,
        platform: str,
        review_data: List[Dict[str, Any]],
        period: str = "weekly",
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Track and analyze reviews from a platform.
        
        Args:
            platform: Review platform
            review_data: Recent reviews
            period: Analysis period
            context: Additional context
            
        Returns:
            Review analysis and trends
        """
        prompt = f"""Analyze {platform} reviews for {period}:

Reviews:
{self._format_reviews(review_data)}

Provide:
1. Average rating
2. Rating distribution
3. Common positive themes
4. Common negative themes
5. Trend vs previous period
6. Response rate
7. Action items"""
        
        return await self.generate(prompt, context)

    async def generate_response(
        self,
        review: Dict[str, Any],
        response_tone: str = "professional",
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Generate response to a review.
        
        Args:
            review: Review details and content
            response_tone: Tone of response
            context: Additional context
            
        Returns:
            Appropriate response text
        """
        prompt = f"""Generate a review response:

Platform: {review.get('platform')}
Rating: {review.get('rating')}/5
Reviewer: {review.get('reviewer_name', 'Customer')}
Review: "{review.get('content')}"

Tone: {response_tone}

Provide:
1. Response text (appropriate length)
2. Key points addressed
3. Offer/action included (if applicable)
4. Alternative responses (formal/casual)
5. Follow-up action needed"""
        
        return await self.generate(prompt, context)

    async def alert_negative(
        self,
        review: Dict[str, Any],
        severity_threshold: int = 3,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Generate alert for negative review.
        
        Args:
            review: Negative review details
            severity_threshold: Rating threshold for alert
            context: Additional context
            
        Returns:
            Alert details and recommended actions
        """
        prompt = f"""Create alert for negative review:

Rating: {review.get('rating')}/5
Platform: {review.get('platform')}
Reviewer: {review.get('reviewer_name')}
Review: "{review.get('content')}"
Date: {review.get('date')}

Severity Threshold: {severity_threshold}

Provide:
1. Alert severity (critical/high/medium)
2. Key issues identified
3. Immediate response recommendation
4. Escalation needed (yes/no)
5. Resolution suggestions
6. Follow-up actions
7. Prevention measures"""
        
        return await self.generate(prompt, context)

    async def generate_review_request(
        self,
        customer_info: Dict[str, Any],
        service_details: Dict[str, Any],
        platform: str = "google",
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Generate review request message.
        
        Args:
            customer_info: Customer details
            service_details: Recent service info
            platform: Target platform for review
            context: Additional context
            
        Returns:
            Review request message
        """
        prompt = f"""Create a review request:

Customer: {customer_info.get('name')}
Service: {service_details.get('service_name')}
Date: {service_details.get('date')}
Stylist: {service_details.get('staff_name')}
Target Platform: {platform}

Provide:
1. Request message (friendly, not pushy)
2. Best channel (WhatsApp/SMS/Email)
3. Timing recommendation
4. Direct link suggestion
5. Incentive to mention (if any)"""
        
        return await self.generate(prompt, context)

    def _format_reviews(self, reviews: List[Dict[str, Any]]) -> str:
        if not reviews:
            return "No reviews"
        lines = []
        for r in reviews:
            lines.append(f"- {r.get('rating')}/5 by {r.get('reviewer_name', 'Anonymous')}: {r.get('content', '')[:60]}...")
        return "\n".join(lines)


class CampaignOrchestratorAgent(BaseAgent):
    """AI agent for marketing campaign orchestration.
    
    Creates, manages, tracks, and optimizes multi-channel
    marketing campaigns for the salon.
    """
    
    name = "campaign_orchestrator"
    description = "Creates, manages, tracks, and optimizes multi-channel marketing campaigns"
    system_prompt = """You are a campaign orchestration specialist for a salon.
Your role is to plan and execute effective marketing campaigns.

Guidelines:
- Plan campaigns with clear objectives
- Coordinate across channels
- Track performance metrics
- Optimize based on results
- Stay within budget

Campaign Types:
1. Promotional (discounts, offers)
2. Awareness (new services)
3. Retention (loyalty programs)
4. Acquisition (new customers)
5. Seasonal (festivals, events)

Channels:
- WhatsApp
- SMS
- Email
- Social Media
- In-salon

Metrics to Track:
- Reach
- Engagement
- Conversion
- ROI
- Customer acquisition cost

Always optimize for maximum ROI and customer engagement."""

    async def create_campaign(
        self,
        campaign_type: str,
        objective: str,
        target_audience: Dict[str, Any],
        budget: float,
        duration: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Create a new marketing campaign.
        
        Args:
            campaign_type: Type of campaign
            objective: Campaign objective
            target_audience: Target segment
            budget: Campaign budget
            duration: Campaign duration
            context: Additional context
            
        Returns:
            Campaign plan and execution details
        """
        prompt = f"""Create a marketing campaign:

Type: {campaign_type}
Objective: {objective}
Target Audience: {target_audience}
Budget: Rs.{budget}
Duration: {duration}

Provide:
1. Campaign name
2. Key message
3. Channel strategy (WhatsApp, SMS, Social)
4. Content for each channel
5. Timeline with milestones
6. Budget allocation
7. Success metrics
8. A/B test recommendations"""
        
        return await self.generate(prompt, context)

    async def track_performance(
        self,
        campaign_id: str,
        campaign_data: Dict[str, Any],
        metrics: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Track campaign performance.
        
        Args:
            campaign_id: Campaign identifier
            campaign_data: Campaign configuration
            metrics: Performance metrics
            context: Additional context
            
        Returns:
            Performance analysis
        """
        import json
        prompt = f"""Track campaign performance:

Campaign ID: {campaign_id}
Campaign Data:
{json.dumps(campaign_data, indent=2)}

Metrics:
{json.dumps(metrics, indent=2)}

Provide:
1. Performance summary
2. Channel-wise performance
3. Conversion analysis
4. ROI calculation
5. Comparison to benchmarks
6. Issues identified
7. Optimization opportunities"""
        
        return await self.generate(prompt, context)

    async def optimize_campaign(
        self,
        campaign_id: str,
        current_performance: Dict[str, Any],
        optimization_goals: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Optimize running campaign.
        
        Args:
            campaign_id: Campaign identifier
            current_performance: Current metrics
            optimization_goals: What to optimize
            context: Additional context
            
        Returns:
            Optimization recommendations
        """
        prompt = f"""Optimize campaign {campaign_id}:

Current Performance:
{self._format_performance(current_performance)}

Optimization Goals: {optimization_goals}

Provide:
1. Immediate optimizations
2. Channel adjustments
3. Budget reallocation
4. Content tweaks
5. Targeting refinements
6. A/B test results to implement
7. Expected improvement"""
        
        return await self.generate(prompt, context)

    async def create_multi_channel_plan(
        self,
        campaign_theme: str,
        channels: List[str],
        audience_segments: List[Dict[str, Any]],
        budget_allocation: Dict[str, float],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Create multi-channel campaign plan.
        
        Args:
            campaign_theme: Campaign theme/message
            channels: Channels to use
            audience_segments: Target segments
            budget_allocation: Budget per channel
            context: Additional context
            
        Returns:
            Multi-channel execution plan
        """
        prompt = f"""Create multi-channel campaign plan:

Theme: {campaign_theme}
Channels: {channels}

Audience Segments:
{self._format_segments(audience_segments)}

Budget Allocation:
{self._format_budget(budget_allocation)}

Provide:
1. Channel-specific content
2. Timing coordination
3. Cross-channel messaging
4. Segment targeting per channel
5. Integration points
6. Tracking setup
7. Success metrics per channel"""
        
        return await self.generate(prompt, context)

    def _format_performance(self, performance: Dict[str, Any]) -> str:
        import json
        return json.dumps(performance, indent=2)

    def _format_segments(self, segments: List[Dict[str, Any]]) -> str:
        if not segments:
            return "No segments defined"
        lines = []
        for s in segments:
            lines.append(f"- {s.get('name')}: {s.get('size')} customers ({s.get('criteria')})")
        return "\n".join(lines)

    def _format_budget(self, budget: Dict[str, float]) -> str:
        if not budget:
            return "No budget allocated"
        lines = []
        total = sum(budget.values())
        for channel, amount in budget.items():
            pct = (amount / total * 100) if total > 0 else 0
            lines.append(f"- {channel}: Rs.{amount} ({pct:.1f}%)")
        lines.append(f"Total: Rs.{total}")
        return "\n".join(lines)


# =============================================================================
# UPDATED AGENT REGISTRY
# =============================================================================

AGENTS = {
    # Phase 1 Agents (Original 12)
    "booking": BookingAgent,
    "marketing": MarketingAgent,
    "analytics": AnalyticsAgent,
    "support": CustomerSupportAgent,
    "waitlist": WaitlistManagerAgent,
    "slot_optimizer": SlotOptimizerAgent,
    "upsell": UpsellEngineAgent,
    "dynamic_pricing": DynamicPricingAgent,
    "bundle_creator": BundleCreatorAgent,
    "inventory": InventoryIntelligenceAgent,
    "scheduling": StaffSchedulingAgent,
    "retention": CustomerRetentionAgent,
    
    # Phase 2 Agents (New 13)
    "demand_predictor": DemandPredictorAgent,
    "whatsapp_concierge": WhatsAppConciergeAgent,
    "quality_assurance": QualityAssuranceAgent,
    "resource_allocator": ResourceAllocatorAgent,
    "compliance_monitor": ComplianceMonitorAgent,
    "voice_receptionist": VoiceReceptionistAgent,
    "feedback_analyzer": FeedbackAnalyzerAgent,
    "vip_priority": VIPPriorityAgent,
    "social_media_manager": SocialMediaManagerAgent,
    "image_creatives_generator": ImageCreativesGeneratorAgent,
    "content_writer": ContentWriterAgent,
    "review_monitor": ReviewMonitorAgent,
    "campaign_orchestrator": CampaignOrchestratorAgent,
}


def get_agent(agent_name: str, **kwargs) -> BaseAgent:
    """Get agent instance by name.
    
    Args:
        agent_name: Name of the agent to retrieve
        **kwargs: Arguments to pass to agent constructor
        
    Returns:
        Agent instance
        
    Raises:
        ValueError: If agent name is not found
    """
    agent_class = AGENTS.get(agent_name)
    if agent_class is None:
        raise ValueError(f"Unknown agent type: {agent_name}")
    return agent_class(**kwargs)


def get_all_agents() -> dict:
    """Get all registered agents.
    
    Returns:
        Dictionary of all agent names to agent classes
    """
    return AGENTS.copy()
