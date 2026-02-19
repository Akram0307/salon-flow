# Salon Flow - Project Overview

## Project Structure

This project is a cost-optimized salon management SaaS architecture targeting a budget of ₹15,000/month per salon (~$180/month).

The project is organized into the following key components:

- **Client Layer**: React PWAs (Owner, Manager, Staff, Client)
- **API Gateway Layer**: Cloud Run API Gateway (FastAPI)
- **Consolidated Services Layer**:
  - Core Service (Auth, Booking, Customer, Billing modules)
  - AI Service (Chat, Marketing, Analytics agents)
  - Communication Service (WhatsApp, Voice modules)
- **Data Layer**: Firestore-only (No Cloud SQL)
- **External Services**: Twilio, OpenRouter, Firebase Auth

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for builds
- **shadcn/ui** for components
- **Workbox** for PWA offline support
- **Zustand** for state management
- **React Query** for server state

### Backend
- **FastAPI** with Python 3.11
- **Pydantic** for data validation
- **Firebase Admin SDK** for Firestore integration
- **httpx** for async HTTP client
- **uvicorn** as ASGI server

### AI Stack
- **OpenRouter** unified API
- **Gemini 3 Flash** model
- **LangChain** for agent orchestration
- **Response Caching** for cost optimization

### Infrastructure
- **Cloud Run** (scale to zero)
- **Firestore** (primary database)
- **Cloud Storage** (static assets, backups)
- **Cloud CDN** (global distribution)
- **Firebase Auth** (authentication)
- **Terraform** (IaC)
- **GitHub Actions** (CI/CD)

## Coding Patterns

### Frontend Patterns
- PWA offline-first design
- React Query for data fetching and caching
- Component-based architecture with shadcn/ui
- Small bundle sizes for performance

### Backend Patterns
- Async handling with FastAPI
- Firestore for data storage with denormalization
- Consolidated services to reduce cold starts
- AI response caching for cost optimization

### Data Patterns
- Firestore document-based structure
- Multi-tenant isolation
- Denormalized data for efficient reads
- Batch operations for performance

### DevOps Patterns
- Infrastructure as Code with Terraform
- CI/CD with GitHub Actions
- Scale-to-zero serverless architecture
- Free tier maximization across GCP services

## Agent Roles

This project requires the following roles:

1. **Solutions Architect** - System design, cost optimization, architecture decisions
2. **Frontend Developer** - React PWAs, UI/UX, offline support
3. **Backend Developer** - FastAPI services, API design, database schema
4. **AI/ML Engineer** - AI agents, LLM integration, prompt engineering
5. **DevOps Engineer** - CI/CD, Terraform, monitoring, deployment
6. **QA Engineer** - Testing, performance testing, security testing

## Implementation Strategy

The implementation follows a phased approach:
1. **Foundation** (Weeks 1-4)
2. **AI Integration** (Weeks 5-8)
3. **PWAs Completion** (Weeks 9-12)
4. **Communication** (Weeks 13-16)
5. **Launch** (Weeks 17-20)

## Cost Optimization Focus

Primary cost optimization strategies:
- Firestore-only database (no Cloud SQL)
- Cloud Run scale-to-zero
- In-memory caching
- AI response caching
- Consolidated services
- Free tier maximization