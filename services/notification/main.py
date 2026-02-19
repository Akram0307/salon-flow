"""
Salon Flow - Notification Service
WhatsApp, SMS, Voice notifications
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

logger = structlog.get_logger()

app = FastAPI(
    title="Salon Flow Notification Service",
    description="Notification Service for Salon Management",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "notification-service"}

@app.post("/whatsapp/send")
async def send_whatsapp(to: str, message: str):
    """Send WhatsApp message"""
    return {"status": "sent", "to": to, "message": message}

@app.post("/sms/send")
async def send_sms(to: str, message: str):
    """Send SMS message"""
    return {"status": "sent", "to": to, "message": message}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
