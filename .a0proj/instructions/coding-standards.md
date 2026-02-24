# Coding Standards - Salon_Flow

## Project Overview
Salon_Flow is a cloud-native, multi-tenant salon management SaaS with AI-first architecture. Built on Google Cloud Platform with 25 specialized AI agents.

## Technology Stack

### Frontend (React/TypeScript)
- **Framework**: React 18+ with TypeScript (strict mode)
- **Build Tool**: Vite with PWA plugin
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: Zustand
- **Routing**: React Router v6
- **Testing**: Playwright CLI 1.58.2 (E2E), Vitest (unit)

### Backend (FastAPI/Python)
- **Framework**: FastAPI with async support
- **Python**: 3.11+ with type hints
- **Authentication**: Firebase Auth + Custom JWT (bcrypt)
- **Database**: Firestore (NoSQL document store)
- **Cache**: Upstash Redis
- **Vector DB**: Upstash Vector (for RAG)
- **Messaging**: GCP Pub/Sub
- **AI**: OpenRouter (Gemini models)
- **Testing**: pytest, pytest-asyncio

## Architecture Principles

1. **Multi-tenancy**: All data isolated by `salon_id` in Firestore paths
2. **Event-driven**: Async communication via Pub/Sub
3. **Serverless**: Cloud Run with scale-to-zero
4. **AI-first**: 25 specialized agents for automation
5. **Mobile-first**: PWAs designed for on-the-go usage

## File Structure

### Frontend (apps/owner/)
```
src/
├── components/
│   ├── ai/              # AI-specific components
│   ├── layout/          # Layout wrappers
│   ├── dashboard/       # Dashboard views
│   └── ui/              # shadcn/ui components
├── hooks/               # Custom React hooks
├── services/            # API clients
├── stores/              # Zustand stores
└── types/               # TypeScript definitions
```

### Backend (services/)
```
api/          # Core business logic
├── routers/   # API route handlers
├── models/    # Pydantic models
├── services/  # Business logic
└── repositories/  # Firestore operations

ai/           # AI service with 25 agents
├── agents/    # Specialized AI agents
├── pipeline/  # Request processing
├── adapters/  # Multi-channel input
└── plugins/   # Agent plugins

notification/ # Twilio WhatsApp/SMS service
```

## Naming Conventions

### TypeScript/React
- Components: PascalCase (e.g., `AIInsightsBar`)
- Hooks: camelCase with 'use' prefix (e.g., `useAIInsights`)
- Stores: camelCase with 'Store' suffix (e.g., `authStore`)
- Types: PascalCase with descriptive names (e.g., `BookingStatus`)
- Constants: UPPER_SNAKE_CASE

### Python
- Modules: snake_case
- Classes: PascalCase
- Functions: snake_case
- Constants: UPPER_SNAKE_CASE
- Type hints: Required for all functions

## Code Quality

### TypeScript
- Enable strict mode
- No `any` types without justification
- Use discriminated unions for complex states
- Prefer interfaces over types for objects

### Python
- Use Pydantic v2 for all models
- Async/await for all I/O operations
- Type hints on all function signatures
- Docstrings for all public APIs

## Testing Requirements

### E2E (Playwright)
- All user flows must have E2E tests
- Use ARIA selectors over data-testid
- Test mobile viewport (375x812)
- Test offline functionality
- Test PWA installability

### Unit Tests
- Components: 80% coverage minimum
- Services: 90% coverage minimum
- Utils: 100% coverage

## Git Workflow
- Branch: `feature/description`, `bugfix/description`, `hotfix/description`
- Commits: Conventional Commits format
- PRs: Require 1 review, all tests passing
- Merge: Squash merge to main
