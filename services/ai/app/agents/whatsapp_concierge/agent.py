"""WhatsApp Concierge Agent

Main agent for handling WhatsApp conversations with salon customers.
Supports booking, service inquiries, and customer support.
"""
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import structlog

from ..base import BaseAgent, AgentConfig, AgentResponse
from .tools import WHATSAPP_CONCIERGE_TOOLS

logger = structlog.get_logger()


@dataclass
class ConversationContext:
    """Context for a WhatsApp conversation"""
    salon_id: str
    customer_phone: str
    customer_name: Optional[str] = None
    customer_id: Optional[str] = None
    is_new_customer: bool = False
    conversation_state: str = "greeting"  # greeting, booking, service_inquiry, support
    booking_data: Dict[str, Any] = field(default_factory=dict)
    last_intent: Optional[str] = None
    language: str = "en"  # en, hi, te


class WhatsAppConciergeAgent(BaseAgent):
    """WhatsApp Concierge Agent for customer interactions"""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        if config is None:
            config = AgentConfig(
                name="whatsapp_concierge",
                description="WhatsApp Concierge Agent for customer booking and support",
                model="gemini-2.5-flash-preview-05-20",
                temperature=0.7,
                max_tokens=2048,
                system_prompt=self._get_system_prompt(),
                tools=WHATSAPP_CONCIERGE_TOOLS
            )
        super().__init__(config)
        self.conversations: Dict[str, ConversationContext] = {}
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent"""
        return """You are the WhatsApp Concierge for a salon. You help customers with:

1. **Booking Appointments** - Help customers book, reschedule, or cancel appointments
2. **Service Information** - Answer questions about services, prices, and duration
3. **Staff Information** - Provide information about stylists and their expertise
4. **Availability** - Check available time slots for services
5. **Customer Support** - Handle general inquiries and feedback

## Communication Style
- Be friendly, professional, and helpful
- Use emojis appropriately to make conversations engaging
- Keep responses concise but informative
- Always confirm booking details before finalizing

## Multi-Language Support
- Respond in the same language the customer uses
- Support: English (en), Hindi (hi), Telugu (te)

## Booking Flow
1. Ask for service preference
2. Show available stylists (or auto-assign)
3. Show available time slots
4. Confirm all details
5. Create booking and send confirmation

## Guardrails
- Only discuss salon-related topics
- Politely redirect off-topic conversations
- Never share other customers' information
- Always verify customer identity for sensitive operations

## Available Tools
- send_whatsapp: Send messages to customers
- get_services: Get salon services
- get_staff: Get staff members
- check_availability: Check time slots
- create_booking: Create appointments
- get_customer: Get customer details

Always use tools to get real-time information. Never make up service prices or availability."""
    
    def get_or_create_context(
        self,
        salon_id: str,
        customer_phone: str
    ) -> ConversationContext:
        """Get or create conversation context"""
        key = f"{salon_id}:{customer_phone}"
        if key not in self.conversations:
            self.conversations[key] = ConversationContext(
                salon_id=salon_id,
                customer_phone=customer_phone
            )
        return self.conversations[key]
    
    
    async def process_message(
        self,
        salon_id: str,
        customer_phone: str,
        message: str,
        language: str = "en"
    ) -> AgentResponse:
        """Process an incoming WhatsApp message"""
        try:
            # Get or create conversation context
            ctx = self.get_or_create_context(salon_id, customer_phone)
            ctx.language = language
            
            # Get customer info if not already loaded
            if not ctx.customer_id:
                customer_result = await self._get_customer(salon_id, customer_phone)
                if customer_result.get("success"):
                    customer = customer_result.get("customer")
                    if customer:
                        ctx.customer_id = customer.get("id")
                        ctx.customer_name = customer.get("name")
                        ctx.is_new_customer = False
                    else:
                        ctx.is_new_customer = True
            
            
            # Process the message with the LLM
            response = await self.generate_response(
                message=message,
                context={
                    "salon_id": salon_id,
                    "customer_phone": customer_phone,
                    "customer_name": ctx.customer_name,
                    "is_new_customer": ctx.is_new_customer,
                    "conversation_state": ctx.conversation_state,
                    "language": language
                }
            )
            
            return response
            
        except Exception as e:
            logger.error("Error processing WhatsApp message", error=str(e))
            return AgentResponse(
                success=False,
                message="I apologize, but I encountered an error. Please try again or contact the salon directly.",
                error=str(e)
            )
    
    
    async def handle_booking_intent(
        self,
        ctx: ConversationContext,
        message: str
    ) -> AgentResponse:
        """Handle booking-related intent"""
        # This would be handled by the LLM with tool calls
        return await self.generate_response(
            message=message,
            context={
                "salon_id": ctx.salon_id,
                "customer_phone": ctx.customer_phone,
                "intent": "booking"
            }
        )
    
    
    async def handle_service_inquiry(
        self,
        ctx: ConversationContext,
        message: str
    ) -> AgentResponse:
        """Handle service inquiry intent"""
        return await self.generate_response(
            message=message,
            context={
                "salon_id": ctx.salon_id,
                "intent": "service_inquiry"
            }
        )
    
    
    async def send_welcome(
        self,
        salon_id: str,
        customer_phone: str,
        salon_name: str
    ) -> AgentResponse:
        """Send welcome message to new customer"""
        message = f"""👋 Welcome to {salon_name}!

Thank you for reaching out. I'm your personal salon assistant.

Here's what I can help you with:
💇 Book appointments
📋 View our services & prices
👨‍🎨 Meet our stylists
⏰ Check availability

Reply with 'BOOK' to schedule an appointment, or 'MENU' to see our services."""
        
        return AgentResponse(
            success=True,
            message=message
        )
    
    
    async def _get_customer(
        self,
        salon_id: str,
        phone: str
    ) -> Dict[str, Any]:
        """Get customer by phone number"""
        for tool in self.tools:
            if tool.name == "get_customer":
                return await tool.execute(salon_id=salon_id, phone=phone)
        return {"success": False, "error": "Tool not found"}


# Agent configuration for plugin system
AGENT_CONFIG = {
    "name": "whatsapp_concierge",
    "description": "WhatsApp Concierge Agent for customer booking and support",
    "model": "gemini-2.5-flash-preview-05-20",
    "temperature": 0.7,
    "max_tokens": 2048,
    "enabled": True,
    "priority": 1,
    "languages": ["en", "hi", "te"]
}
