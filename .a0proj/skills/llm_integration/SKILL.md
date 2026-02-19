# LLM Integration Skill

## Overview
Integrate OpenRouter API for accessing Gemini models for chat, voice, and marketing.

## Model Configuration

| Use Case | Model | Cost/1K tokens |
|----------|-------|----------------|
| Chat/Voice | google/gemini-3-flash | $0.0001 |
| Marketing | google/gemini-3-pro-image-preview | $0.001 |

## API Integration
```python
import httpx

OPENROUTER_API_KEY = "your-api-key"

class OpenRouterClient:
    def __init__(self):
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

    async def chat(self, messages: list, model: str = "google/gemini-3-flash"):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={"model": model, "messages": messages}
            )
            return response.json()
```

## Cost Optimization
- Cache common responses
- Use smaller model when possible
- Batch requests when feasible
