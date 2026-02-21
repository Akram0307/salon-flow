# Changelog

All notable changes to Salon Flow will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Frontend PWA development in progress
- Owner Dashboard with analytics and AI integration
- Staff PWA for service delivery
- Client PWA for customer booking

---

## [0.3.0] - 2025-02-21

### Added
- **Hybrid AI Architecture** implementation
  - Hexagonal layer for multi-channel adapters (WhatsApp, Voice, Web)
  - Pipeline layer for request processing with caching
  - Microkernel plugin system for agent management
  - CQRS pattern for optimized data access
- **25 Specialized AI Agents**
  - Booking & Scheduling: Booking, Slot Optimizer, Waitlist Manager, Demand Predictor
  - Customer Engagement: WhatsApp Concierge, Support, Feedback Analyzer, Retention
  - Marketing & Growth: Marketing, Social Media, Content Writer, Image Generator, Review Monitor
  - Revenue Optimization: Upsell Engine, Dynamic Pricing, Bundle Creator
  - Operations: Inventory Intelligence, Staff Scheduler, Analytics, Compliance Monitor
  - Specialized: Bridal Consultant, Loyalty Manager, Membership Agent
- **Multi-language Guardrails** (English, Hindi, Telugu)
- **Semantic Caching** with Upstash Vector
- **GCP Pub/Sub Integration** for event-driven communication
- **AI Proxy Router** in backend API

### Changed
- Refactored AI service to hybrid architecture
- Improved model routing with cost optimization
- Enhanced caching with 70% LLM call reduction

### Fixed
- Case-sensitivity issues in Settings configuration
- Firebase emulator initialization in test environment
- Trailing slash redirect issues in FastAPI

---

## [0.2.0] - 2025-02-20

### Added
- **Notification Service** with Twilio integration
  - WhatsApp Business API support
  - SMS notifications
  - Multi-tenant credential management
- **AI Service** deployed to Cloud Run
  - OpenRouter integration with Gemini models
  - Redis-based response caching
  - 12 initial AI agents
- **Backend API** fully deployed
  - 146+ API tests passing
  - Complete CRUD operations for all modules

### Changed
- Migrated to Upstash Redis REST API
- Optimized Cloud Run configuration for cost efficiency

### Fixed
- Authentication middleware issues
- Firestore model ID handling
- Booking router validation errors

---

## [0.1.0] - 2025-02-19

### Added
- **Project Initialization**
  - Monorepo structure with apps/ and services/
  - Docker Compose for local development
  - CI/CD pipeline with GitHub Actions
- **Backend API Service**
  - FastAPI framework with Pydantic v2 schemas
  - Firebase Authentication with JWT
  - Firestore database integration
  - Role-based access control (Owner, Manager, Receptionist, Stylist)
- **Core Modules**
  - Authentication (BE-001): Registration, Login, OTP verification
  - Tenant Management (BE-002): Multi-salon onboarding
  - Customer Management (BE-003): CRM with loyalty tracking
  - Service Catalog (BE-004): 267+ services management
  - Staff Management (BE-005): Roles, shifts, skills
  - Booking System (BE-006): Multi-channel appointments
  - Inventory (BE-007): Stock management
  - Payments (BE-008): GST invoicing, memberships
  - Feedback (BE-009): Reviews and ratings
  - Analytics (BE-010): Business reporting
- **Frontend PWA Scaffolds**
  - Client PWA (React + TypeScript + Vite)
  - Staff PWA
  - Manager PWA
  - Owner PWA
- **Development Infrastructure**
  - Makefile for common commands
  - Pytest configuration with 89% coverage
  - ESLint and Prettier for frontend
  - Pre-commit hooks

### Infrastructure
- GCP Cloud Run deployment configuration
- Cloud Build CI/CD pipeline
- Secret Manager integration
- Artifact Registry setup

---

## Version History Summary

| Version | Date | Key Features |
|---------|------|--------------|
| 0.3.0 | 2025-02-21 | 25 AI Agents, Hybrid Architecture |
| 0.2.0 | 2025-02-20 | Notification Service, AI Deployment |
| 0.1.0 | 2025-02-19 | Initial MVP, Backend API |

---

## Upcoming Milestones

### [0.4.0] - Planned
- Complete Owner Dashboard PWA
- WhatsApp Concierge production testing
- Real-time booking notifications

### [0.5.0] - Planned
- Staff PWA completion
- Client PWA with booking flow
- Payment gateway integration

### [1.0.0] - Planned
- Production-ready release
- Full multi-tenant support
- Complete documentation
- Performance optimization

---

[Unreleased]: https://github.com/Akram0307/salon-flow/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/Akram0307/salon-flow/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Akram0307/salon-flow/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Akram0307/salon-flow/releases/tag/v0.1.0
