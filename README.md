# 🎨 Salon Flow - AI-Powered Salon Management SaaS

<div align="center">

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org)
[![GCP](https://img.shields.io/badge/Google%20Cloud-Cloud%20Run-4285f4.svg)](https://cloud.google.com/run)

**An event-driven, multi-tenant, AI-powered salon management platform**

[Features](#-features) • [Architecture](#-architecture) • [Installation](#-installation) • [API Reference](#-api-reference) • [AI Agents](#-ai-agents)

</div>

---

## 📋 Overview

**Salon Flow** is a comprehensive, cloud-native salon management SaaS platform designed to replace legacy systems like ReSpark. Built with a modern microservices architecture, it features **25 specialized AI agents**, multi-channel communication (WhatsApp, Voice, Web), and real-time analytics—all optimized to run **70% under budget** at ₹3,000-5,000/month.

### 🎯 Target Business

Originally designed for **Jawed Habib Hair & Beauty Salon** franchise in Kurnool, India:
- **3,230+ Customers** in database
- **4,948+ Orders** processed
- **316 Active Members**
- **10 Service Chairs** (6 Men's + 4 Women's)
- **4 Service Rooms** (Bridal, Treatment, Spa)

---

## ✨ Features

### 🏢 Core Business Modules

| Module | Description |
|--------|-------------|
| **Tenant Management** | Multi-salon onboarding with customizable layouts |
| **Customer CRM** | 360° customer view with loyalty tracking |
| **Service Catalog** | 267+ services across 10 categories |
| **Booking System** | Multi-channel (Walk-in, Phone, Online, WhatsApp) |
| **Staff Management** | Roles, shifts, skills, and performance tracking |
| **Inventory Control** | Stock levels, alerts, and purchase orders |
| **Payments & Billing** | GST invoices, memberships, and payment tracking |
| **Analytics & Reports** | Real-time dashboards and business insights |

### 🤖 AI-Powered Capabilities

- **25 Specialized AI Agents** for automation
- **WhatsApp Concierge** for 24/7 customer engagement
- **Smart Booking** with automatic staff assignment
- **Dynamic Pricing** based on demand
- **Predictive Analytics** for business forecasting
- **Multi-language Support** (English, Hindi, Telugu)

### 📱 Four Progressive Web Apps

1. **Client PWA** - Customer booking and loyalty portal
2. **Staff PWA** - Stylist schedules and service delivery
3. **Manager PWA** - Operations and staff management
4. **Owner PWA** - Analytics and business oversight

---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
├─────────────┬─────────────┬─────────────┬─────────────────────────┤
│  Client PWA │  Staff PWA  │ Manager PWA │      Owner PWA          │
└──────┬──────┴──────┬──────┴──────┬──────┴──────────┬──────────────┘
       │             │             │                  │
       └─────────────┴──────┬──────┴──────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                     API GATEWAY (Cloud Run)                      │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Backend  │  Firebase Auth  │  Rate Limiting  │  CORS    │
└────────┬──────────────────────────┬──────────────────────────────┘
         │                          │
    ┌────▼────┐               ┌─────▼─────┐
    │ Pub/Sub │               │  Redis    │
    │ Events  │               │  Cache    │
    └────┬────┘               └─────┬─────┘
         │                          │
┌────────▼──────────────────────────▼─────────────────────────────┐
│                      SERVICE LAYER                               │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   API Service   │   AI Service    │   Notification Service      │
│   (Cloud Run)   │   (Cloud Run)   │      (Cloud Run)            │
├─────────────────┼─────────────────┼─────────────────────────────┤
│ • CRUD APIs     │ • 25 AI Agents  │ • WhatsApp (Twilio)         │
│ • Business Logic│ • Chat/Voice    │ • SMS                       │
│ • Multi-tenant  │ • Analytics     │ • Push Notifications        │
└────────┬────────┴────────┬────────┴──────────────┬──────────────┘
         │                 │                        │
    ┌────▼────┐      ┌─────▼─────┐           ┌──────▼──────┐
    │Firestore│      │  Upstash  │           │   Twilio    │
    │   DB    │      │  Vector   │           │   WhatsApp  │
    └─────────┘      └───────────┘           └─────────────┘
```

### Hybrid AI Architecture

The AI service implements a sophisticated hybrid architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                    HEXAGONAL LAYER (Adapters)                    │
├─────────────────┬─────────────────┬─────────────────────────────┤
│ WhatsApp Adapter│   Voice Adapter │   Web Chat Adapter          │
└────────┬────────┴────────┬────────┴──────────────┬──────────────┘
         │                 │                        │
┌────────▼─────────────────▼────────────────────────▼─────────────┐
│                    PIPELINE LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│  Request → Guardrails → Cache → Model Router → Response         │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                  MICROKERNEL LAYER (Plugins)                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │ Booking │ │Marketing│ │Support  │ │Analytics│ │  ...21  │   │
│  │ Agent   │ │ Agent   │ │ Agent   │ │ Agent   │ │ Agents  │   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      CQRS LAYER                                  │
├─────────────────────────────────────────────────────────────────┤
│  Command Handler (Writes)  │  Query Handler (Reads/Cache)       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Backend

| Technology | Purpose |
|------------|---------|
| **Python 3.11** | Primary backend language |
| **FastAPI** | REST API framework |
| **Pydantic v2** | Data validation and schemas |
| **Firebase Admin SDK** | Authentication and Firestore |
| **Google Cloud Firestore** | Primary database (Native mode) |
| **Upstash Redis** | Caching and session management |
| **Upstash Vector** | Semantic search and RAG |

### Frontend

| Technology | Purpose |
|------------|---------|
| **React 18** | UI framework |
| **TypeScript** | Type safety |
| **Vite** | Build tool |
| **Tailwind CSS** | Styling |
| **shadcn/ui** | Component library |

### AI & ML

| Technology | Purpose |
|------------|---------|
| **OpenRouter** | LLM API gateway |
| **Google Gemini 2.5 Flash** | Primary AI model |
| **Gemini 3 Pro** | Complex reasoning tasks |
| **LangGraph** | Agent orchestration |

### Cloud Infrastructure

| Service | Purpose |
|---------|---------|
| **Google Cloud Run** | Serverless compute |
| **GCP Pub/Sub** | Event messaging |
| **GCP Secret Manager** | Secrets management |
| **GCP Cloud Build** | CI/CD pipeline |
| **GCP Artifact Registry** | Container registry |

### Communication

| Service | Purpose |
|---------|---------|
| **Twilio** | WhatsApp Business API |
| **Twilio Voice** | Phone call handling |

---

## 🤖 AI Agents

### Complete Agent Registry (25 Agents)

#### 📅 Booking & Scheduling
| Agent | Purpose |
|-------|---------|
| **Booking Agent** | Appointment management |
| **Slot Optimizer** | Fill schedule gaps |
| **Waitlist Manager** | Cancellation recovery |
| **Demand Predictor** | Forecast booking patterns |

#### 💬 Customer Engagement
| Agent | Purpose |
|-------|---------|
| **WhatsApp Concierge** | 24/7 customer chat |
| **Support Agent** | Query resolution |
| **Feedback Analyzer** | Review processing |
| **Retention Agent** | Churn prevention |

#### 📈 Marketing & Growth
| Agent | Purpose |
|-------|---------|
| **Marketing Agent** | Campaign creation |
| **Social Media Manager** | Platform automation |
| **Content Writer** | Blog and captions |
| **Image Generator** | Visual creatives |
| **Review Monitor** | Reputation management |

#### 💰 Revenue Optimization
| Agent | Purpose |
|-------|---------|
| **Upsell Engine** | Service recommendations |
| **Dynamic Pricing** | Demand-based pricing |
| **Bundle Creator** | Package deals |

#### ⚙️ Operations
| Agent | Purpose |
|-------|---------|
| **Inventory Intelligence** | Stock management |
| **Staff Scheduler** | Shift optimization |
| **Analytics Agent** | Business insights |
| **Compliance Monitor** | Regulatory checks |

#### 🎯 Specialized
| Agent | Purpose |
|-------|---------|
| **Bridal Consultant** | Wedding packages |
| **Loyalty Manager** | Points and rewards |
| **Membership Agent** | Subscription handling |

---

## 📊 Cost Analysis

### Monthly Operating Cost (Single Salon)

| Component | Cost (₹) | Notes |
|-----------|----------|-------|
| GCP Cloud Run | 0-500 | Scale-to-zero |
| Firestore | 50 | Free tier |
| Upstash Redis | 350 | 10K commands/day |
| Upstash Vector | 500 | 5M vectors |
| OpenRouter AI | 750 | Cached responses |
| Twilio WhatsApp | 2,300 | ~500 messages |
| Domain + CDN | 200 | Optional |
| **Total** | **₹4,150** | **72% under budget** |

**Target Budget**: ₹15,000/month  
**Achieved**: ₹4,150/month  
**Savings**: 72%

---

## 🚀 Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- GCP Account with billing enabled
- Twilio Account (for WhatsApp)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Akram0307/salon-flow.git
cd salon-flow

# Copy environment files
cp .env.example .env
cp services/api/.env.example services/api/.env
cp services/ai/.env.local.example services/ai/.env.local

# Install dependencies
make install

# Start local development
make dev

# Run tests
make test
```

### Environment Variables

```bash
# GCP Configuration
GCP_PROJECT_ID=your-project-id
GCP_REGION=asia-south1

# Firebase
FIREBASE_PROJECT_ID=your-project-id

# OpenRouter AI
OPENROUTER_API_KEY=your-api-key

# Upstash Redis
UPSTASH_REDIS_REST_URL=https://your-redis.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-token

# Twilio
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=whatsapp:+1234567890
```

---

## 📁 Project Structure

```
salon-flow/
├── apps/                      # Frontend PWAs
│   ├── client/               # Customer-facing app
│   ├── staff/                # Stylist app
│   ├── manager/              # Operations app
│   └── owner/                # Analytics dashboard
├── services/                  # Backend services
│   ├── api/                  # Main FastAPI backend
│   │   ├── app/
│   │   │   ├── routers/      # API endpoints
│   │   │   ├── models/       # Firestore models
│   │   │   ├── schemas/      # Pydantic schemas
│   │   │   ├── services/     # Business logic
│   │   │   └── core/         # Config and utilities
│   │   └── tests/            # API tests
│   ├── ai/                   # AI Agent service
│   │   ├── app/
│   │   │   ├── agents/       # Agent plugins
│   │   │   ├── adapters/     # Channel adapters
│   │   │   ├── pipeline/     # Request processing
│   │   │   └── core/         # AI configuration
│   │   └── tests/            # AI tests
│   └── notification/         # Twilio integration
│       └── app/
├── infrastructure/           # Infrastructure configs
│   └── local/
│       └── firebase/         # Firebase emulator
├── deploy/                    # Deployment configs
│   ├── terraform/            # IaC definitions
│   └── scripts/              # Deployment scripts
├── docs/                      # Documentation
├── tests/                     # Test suites
│   ├── api/                  # Backend tests
│   ├── ai/                   # AI service tests
│   └── e2e/                  # End-to-end tests
├── .github/                   # GitHub Actions
│   └── workflows/
├── docker-compose.yml        # Local development
├── cloudbuild.yaml           # GCP CI/CD
├── Makefile                  # Development commands
└── README.md
```

---

## 🔌 API Reference

### Core Endpoints

#### Authentication
```
POST /api/v1/auth/register     # Register new user
POST /api/v1/auth/login        # Login user
POST /api/v1/auth/verify-otp   # Verify OTP
POST /api/v1/auth/refresh      # Refresh token
```

#### Tenants (Salons)
```
GET    /api/v1/tenants         # List tenants
POST   /api/v1/tenants         # Create tenant
GET    /api/v1/tenants/{id}    # Get tenant
PUT    /api/v1/tenants/{id}    # Update tenant
DELETE /api/v1/tenants/{id}    # Delete tenant
```

#### Customers
```
GET    /api/v1/customers       # List customers
POST   /api/v1/customers       # Create customer
GET    /api/v1/customers/{id}  # Get customer
PUT    /api/v1/customers/{id}  # Update customer
GET    /api/v1/customers/{id}/loyalty  # Loyalty points
```

#### Bookings
```
GET    /api/v1/bookings        # List bookings
POST   /api/v1/bookings        # Create booking
PUT    /api/v1/bookings/{id}   # Update booking
DELETE /api/v1/bookings/{id}   # Cancel booking
POST   /api/v1/bookings/{id}/check-in  # Check-in
POST   /api/v1/bookings/{id}/checkout  # Checkout
```

#### AI Chat
```
POST /api/v1/ai/chat           # Chat with AI
POST /api/v1/ai/agents/{id}/chat  # Agent-specific chat
GET  /api/v1/ai/agents         # List agents
```

### Full API Documentation

Access the interactive API documentation at:
- **Swagger UI**: `https://your-api-url/docs`
- **ReDoc**: `https://your-api-url/redoc`

---

## 🧪 Testing

### Run All Tests
```bash
# Backend tests
make test-backend

# AI service tests
make test-ai

# Frontend tests
make test-frontend

# E2E tests
make test-e2e

# Coverage report
make coverage
```

### Test Statistics

| Module | Tests | Coverage |
|--------|-------|----------|
| Authentication | 15 | 95% |
| Tenants | 12 | 92% |
| Customers | 17 | 90% |
| Bookings | 10 | 88% |
| Services | 12 | 91% |
| Staff | 11 | 89% |
| AI Agents | 114 | 85% |
| **Total** | **617** | **89%** |

---

## 🚢 Deployment

### Deploy to GCP Cloud Run

```bash
# Set up GCP credentials
gcloud auth login
gcloud config set project your-project-id

# Deploy all services
make deploy

# Or deploy individually
make deploy-api
make deploy-ai
make deploy-notification
```

### CI/CD Pipeline

The project uses GitHub Actions for CI/CD:

1. **On Pull Request**: Run tests and linting
2. **On Main Push**: Build and deploy to Cloud Run
3. **On Tag**: Create release and deploy to production

---

## 📈 Business Rules

### Salon Configuration

| Setting | Value |
|---------|-------|
| GST Rate | 5% |
| Loyalty Rate | 1 point per ₹10 |
| Loyalty Expiry | 12 months |
| Membership Renewal | 15 days before expiry |
| Late Arrival Grace | 15 minutes |

### Resource Types

| Type | Count | Exclusive |
|------|-------|----------|
| Men's Chair | 6 | No |
| Women's Chair | 4 | No |
| Bridal Room | 1 | Yes |
| Treatment Room | 2 | Shared |
| Spa Room | 1 | Yes |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/Akram0307/salon-flow/issues)
- **Email**: support@salonflow.ai

---

<div align="center">

**Built with ❤️ for the salon industry**

</div>
