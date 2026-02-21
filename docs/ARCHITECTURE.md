# Salon Flow Architecture

## System Overview

Salon Flow is a cloud-native, multi-tenant salon management SaaS built on Google Cloud Platform with a hybrid AI architecture.

## Design Principles

1. **Multi-tenancy**: Complete data isolation per salon
2. **Event-driven**: Asynchronous communication via Pub/Sub
3. **Serverless**: Scale-to-zero for cost efficiency
4. **AI-first**: 25 specialized agents for automation
5. **Cost-optimized**: 72% under budget at ₹4,150/month

## Architecture Layers

### 1. Presentation Layer

Four Progressive Web Apps (PWAs):

| App | Users | Key Features |
|-----|-------|-------------|
| Client PWA | Customers | Booking, loyalty, feedback |
| Staff PWA | Stylists | Schedules, service delivery |
| Manager PWA | Managers | Operations, staff management |
| Owner PWA | Owners | Analytics, business insights |

### 2. API Gateway Layer

- **FastAPI Backend**: REST API with OpenAPI documentation
- **Firebase Auth**: JWT-based authentication
- **Rate Limiting**: Redis-backed request throttling

### 3. Service Layer

| Service | Technology | Purpose |
|---------|------------|---------|
| API Service | FastAPI + Cloud Run | Core business logic |
| AI Service | FastAPI + Cloud Run | 25 AI agents |
| Notification Service | FastAPI + Cloud Run | WhatsApp/SMS via Twilio |

### 4. Data Layer

| Store | Technology | Use Case |
|-------|------------|----------|
| Primary DB | Firestore | All business data |
| Cache | Upstash Redis | Session, response cache |
| Vector DB | Upstash Vector | Semantic search, RAG |

### 5. Integration Layer

- **GCP Pub/Sub**: Event messaging between services
- **Twilio**: WhatsApp Business API
- **OpenRouter**: LLM gateway (Gemini models)

## Hybrid AI Architecture

### Hexagonal Layer (Adapters)

Multi-channel input handling:
- WhatsApp Adapter (Twilio)
- Voice Adapter (TwiML)
- Web Chat Adapter (SSE)

### Pipeline Layer

Request processing chain:
```
Request → Guardrails → Cache → Model Router → Response
```

### Microkernel Layer (Plugins)

25 specialized agents as plugins:
- Auto-discovery on startup
- Hot-reload capability
- Independent scaling

### CQRS Layer

- **Command Handler**: Write operations to Firestore
- **Query Handler**: Read from cache/database

## Data Model

### Multi-tenant Isolation

All collections include `salon_id` for tenant isolation:

```
/salons/{salon_id}
/salons/{salon_id}/customers/{customer_id}
/salons/{salon_id}/bookings/{booking_id}
```

### Core Collections

| Collection | Documents | Subcollections |
|------------|-----------|----------------|
| salons | Salon config | customers, bookings, staff |
| users | User profiles | - |
| conversations | AI chat history | messages |

## Security

### Authentication Flow

1. Firebase Auth issues JWT
2. API validates token
3. Extract `salon_id` from claims
4. Enforce RBAC

### Role-Based Access Control

| Role | Permissions |
|------|-------------|
| Owner | Full access |
| Manager | Operations, staff |
| Receptionist | Bookings, customers |
| Stylist | Own schedule, services |

## Scalability

### Cloud Run Configuration

- **Min instances**: 0 (scale-to-zero)
- **Max instances**: 10
- **Memory**: 512MB - 1GB
- **CPU**: 1-2 vCPU
- **Concurrency**: 80 requests/instance

### Cost Optimization

| Strategy | Savings |
|----------|---------|
| Scale-to-zero | 60% compute |
| AI response caching | 70% LLM calls |
| Firestore native mode | 50% database |
| Regional deployment | 20% network |

## Monitoring

- **Health Checks**: `/health` endpoint
- **Logging**: Cloud Logging
- **Metrics**: Cloud Monitoring
- **Alerts**: Budget thresholds
