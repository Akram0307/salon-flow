# AI Agent Development Skill

## Overview
Build intelligent AI agents for salon automation using Google Agent Development Kit and Model Context Protocol.

## Agent Types

| Agent | Purpose | Model |
|-------|---------|-------|
| Booking Agent | Handle appointments | Gemini 3 Flash |
| Support Agent | Customer queries | Gemini 3 Flash |
| Marketing Agent | Campaigns, offers | Gemini 3 Pro |
| Analytics Agent | Insights, reports | Gemini 3 Flash |

## Agent Architecture
```python
from google.adk import Agent, Tool

class BookingAgent(Agent):
    name = "booking_agent"
    description = "Handles appointment booking and management"

    tools = [
        Tool(name="check_availability", func=check_availability),
        Tool(name="create_booking", func=create_booking),
        Tool(name="cancel_booking", func=cancel_booking),
    ]
```

## MCP Tool Definitions
```json
{
  "tools": [
    {
      "name": "check_availability",
      "description": "Check available slots for a service",
      "parameters": {
        "salon_id": "string",
        "service_id": "string",
        "date": "string"
      }
    }
  ]
}
```
