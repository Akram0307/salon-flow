# FastAPI Development Skill

## Overview
Build high-performance REST APIs using FastAPI for the Salon SaaS backend.

## Project Structure
```
api/
├── main.py
├── routers/
│   ├── appointments.py
│   ├── customers.py
│   ├── staff.py
│   └── services.py
├── models/
├── services/
├── middleware/
│   └── auth.py
└── utils/
```

## Main Application
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Salon SaaS API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

## Router Example
```python
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.get("/{salon_id}")
async def list_appointments(
    salon_id: str,
    user = Depends(get_current_user)
):
    return await booking_service.get_appointments(salon_id)
```
