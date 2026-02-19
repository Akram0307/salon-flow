# AI Response Caching Skill

## Overview
Implement multi-layer caching to reduce AI API costs by 70%.

## Cache Architecture
```
Request → L1 Cache (Memory) → L2 Cache (Firestore) → AI API
            ↓ Hit               ↓ Hit                ↓ Miss
         Response           Response            Response → Cache
```

## L1: In-Memory Cache
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def get_cached_response(cache_key: str):
    return None

def generate_cache_key(messages: list) -> str:
    content = "|".join([m["content"] for m in messages])
    return hashlib.md5(content.encode()).hexdigest()
```

## L2: Firestore Cache
```python
async def get_firestore_cache(cache_key: str):
    doc = await db.collection('ai_cache').document(cache_key).get()
    if doc.exists:
        data = doc.to_dict()
        if data['expires_at'] > datetime.now():
            return data['response']
    return None
```

## Cache Strategy

| Query Type | Cache Duration | Strategy |
|------------|----------------|----------|
| Service info | 24 hours | L1 + L2 |
| Availability | 5 minutes | L1 only |
| Booking flow | No cache | Direct API |
| FAQs | 7 days | L1 + L2 |
