"""WhatsApp Concierge Agent Tools

Tools for the WhatsApp Concierge Agent to interact with salon services.
"""
import os
import httpx
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger()


# Configuration
API_BASE_URL = os.getenv("API_SERVICE_URL", "https://salon-flow-api-687369167038.asia-south1.run.app")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8002")


class SendWhatsAppInput(BaseModel):
    """Input for sending WhatsApp message"""
    to: str = Field(..., description="Phone number in E.164 format (+91XXXXXXXXXX)")
    message: str = Field(..., description="Message content to send")


class GetServicesInput(BaseModel):
    """Input for getting salon services"""
    salon_id: str = Field(..., description="Salon ID")
    category: Optional[str] = Field(None, description="Optional category filter")


class GetStaffInput(BaseModel):
    """Input for getting salon staff"""
    salon_id: str = Field(..., description="Salon ID")
    service_id: Optional[str] = Field(None, description="Optional service ID filter")


class CheckAvailabilityInput(BaseModel):
    """Input for checking availability"""
    salon_id: str = Field(..., description="Salon ID")
    service_id: str = Field(..., description="Service ID")
    staff_id: Optional[str] = Field(None, description="Preferred staff ID")
    date: str = Field(..., description="Date in YYYY-MM-DD format")


class CreateBookingInput(BaseModel):
    """Input for creating a booking"""
    salon_id: str = Field(..., description="Salon ID")
    customer_phone: str = Field(..., description="Customer phone number")
    service_id: str = Field(..., description="Service ID")
    staff_id: Optional[str] = Field(None, description="Staff ID")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    time: str = Field(..., description="Time in HH:MM format")
    customer_name: Optional[str] = Field(None, description="Customer name")


class GetCustomerInput(BaseModel):
    """Input for getting customer by phone"""
    salon_id: str = Field(..., description="Salon ID")
    phone: str = Field(..., description="Customer phone number")


class SendWhatsAppTool:
    """Tool to send WhatsApp messages"""
    
    name = "send_whatsapp"
    description = "Send a WhatsApp message to a phone number"
    input_schema = SendWhatsAppInput
    
    async def execute(self, to: str, message: str) -> Dict[str, Any]:
        """Send WhatsApp message via notification service"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{NOTIFICATION_SERVICE_URL}/api/v1/whatsapp/send",
                    json={"to": to, "message": message}
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "success": data.get("success", False),
                    "message_sid": data.get("message_sid"),
                    "status": data.get("status")
                }
        except Exception as e:
            logger.error("Error sending WhatsApp", error=str(e))
            return {"success": False, "error": str(e)}


class GetServicesTool:
    """Tool to get salon services"""
    
    name = "get_services"
    description = "Get list of services offered by the salon"
    input_schema = GetServicesInput
    
    async def execute(self, salon_id: str, category: Optional[str] = None) -> Dict[str, Any]:
        """Get services from API"""
        try:
            params = {"salon_id": salon_id}
            if category:
                params["category"] = category
                
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{API_BASE_URL}/api/v1/services/",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "success": True,
                    "services": data.get("items", []),
                    "total": data.get("total", 0)
                }
        except Exception as e:
            logger.error("Error getting services", error=str(e))
            return {"success": False, "error": str(e)}


class GetStaffTool:
    """Tool to get salon staff"""
    
    name = "get_staff"
    description = "Get list of staff members at the salon"
    input_schema = GetStaffInput
    
    async def execute(self, salon_id: str, service_id: Optional[str] = None) -> Dict[str, Any]:
        """Get staff from API"""
        try:
            params = {"salon_id": salon_id}
            if service_id:
                params["service_id"] = service_id
                
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{API_BASE_URL}/api/v1/staff/",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "success": True,
                    "staff": data.get("items", []),
                    "total": data.get("total", 0)
                }
        except Exception as e:
            logger.error("Error getting staff", error=str(e))
            return {"success": False, "error": str(e)}


class CheckAvailabilityTool:
    """Tool to check slot availability"""
    
    name = "check_availability"
    description = "Check available time slots for a service"
    input_schema = CheckAvailabilityInput
    
    async def execute(
        self,
        salon_id: str,
        service_id: str,
        date: str,
        staff_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check availability from API"""
        try:
            params = {
                "salon_id": salon_id,
                "service_id": service_id,
                "date": date
            }
            if staff_id:
                params["staff_id"] = staff_id
                
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{API_BASE_URL}/api/v1/bookings/availability",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "success": True,
                    "slots": data.get("slots", []),
                    "date": date
                }
        except Exception as e:
            logger.error("Error checking availability", error=str(e))
            return {"success": False, "error": str(e)}


class CreateBookingTool:
    """Tool to create a booking"""
    
    name = "create_booking"
    description = "Create a new booking for a customer"
    input_schema = CreateBookingInput
    
    async def execute(
        self,
        salon_id: str,
        customer_phone: str,
        service_id: str,
        date: str,
        time: str,
        staff_id: Optional[str] = None,
        customer_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create booking via API"""
        try:
            payload = {
                "salon_id": salon_id,
                "customer_phone": customer_phone,
                "service_id": service_id,
                "date": date,
                "start_time": time,
                "status": "confirmed"
            }
            if staff_id:
                payload["staff_id"] = staff_id
            if customer_name:
                payload["customer_name"] = customer_name
                
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{API_BASE_URL}/api/v1/bookings/",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "success": True,
                    "booking_id": data.get("id"),
                    "booking": data
                }
        except Exception as e:
            logger.error("Error creating booking", error=str(e))
            return {"success": False, "error": str(e)}


class GetCustomerTool:
    """Tool to get customer by phone"""
    
    name = "get_customer"
    description = "Get customer details by phone number"
    input_schema = GetCustomerInput
    
    async def execute(self, salon_id: str, phone: str) -> Dict[str, Any]:
        """Get customer from API"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{API_BASE_URL}/api/v1/customers/by-phone",
                    params={"salon_id": salon_id, "phone": phone}
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "success": True,
                    "customer": data
                }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"success": True, "customer": None, "is_new_customer": True}
            logger.error("Error getting customer", error=str(e))
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error("Error getting customer", error=str(e))
            return {"success": False, "error": str(e)}


# Export all tools
WHATSAPP_CONCIERGE_TOOLS = [
    SendWhatsAppTool(),
    GetServicesTool(),
    GetStaffTool(),
    CheckAvailabilityTool(),
    CreateBookingTool(),
    GetCustomerTool(),
]
