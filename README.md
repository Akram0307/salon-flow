# 💇 Salon Flow

**AI-powered, event-driven, multi-tenant Salon Management SaaS Platform**

## 🚀 Quick Start (Local Development)

### Prerequisites

- Docker Desktop installed on Windows host
- Docker socket mounted (already configured)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/Akram0307/salon-flow.git
cd salon-flow
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Start Local Development

```bash
docker-compose up -d
```

### 4. Access Services

| Service | URL | Description |
|---------|-----|-------------|
| **Firebase Emulator UI** | http://localhost:4000 | Auth, Firestore, Storage |
| **API Service** | http://localhost:8000 | FastAPI backend |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **AI Service** | http://localhost:8001 | AI agents |
| **Notification Service** | http://localhost:8002 | WhatsApp/SMS |
| **Client PWA** | http://localhost:3000 | Customer booking app |
| **Staff PWA** | http://localhost:3001 | Staff management app |
| **Manager PWA** | http://localhost:3002 | Salon manager app |
| **Owner PWA** | http://localhost:3003 | Salon owner dashboard |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer (React PWAs)                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ Client  │ │  Staff  │ │ Manager │ │  Owner  │           │
│  │   PWA   │ │   PWA   │ │   PWA   │ │   PWA   │           │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘           │
└───────┼──────────┼──────────┼──────────┼───────────────────┘
        │          │          │          │
        └──────────┴──────────┴──────────┘
                       │
┌──────────────────────┼──────────────────────────────────────┐
│              API Gateway (FastAPI)                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Auth │ Tenants │ Bookings │ Customers │ Services   │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────┴───────┐ ┌────┴────┐ ┌───────┴───────┐
│  AI Service   │ │  Redis  │ │ Notification  │
│ (Chat/Agents) │ │ (Cache) │ │ (WhatsApp/SMS)│
└───────────────┘ └─────────┘ └───────────────┘
        │
┌───────┴────────────────────────────────────────────────────┐
│              Firebase Emulator (Local)                      │  ┌──────────┐ ┌───────────┐ ┌──────────┐                  │
│  │   Auth   │ │ Firestore │ │ Storage  │                  │
│  └──────────┘ └───────────┘ └──────────┘                  │
└────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Frontend
- **React 18** + TypeScript
- **Vite** for builds
- **Tailwind CSS** for styling
- **React Query** for server state
- **Zustand** for client state
- **Workbox** for PWA

### Backend
- **FastAPI** (Python 3.11)
- **Firebase Admin SDK**
- **Redis** for caching
- **OpenRouter** for AI

### Infrastructure
- **Docker Compose** (local)
- **Cloud Run** (production)
- **Firestore** (database)
- **Firebase Auth** (authentication)

## 📁 Project Structure

```
salon-flow/
├── apps/                    # React PWA applications
│   ├── client/              # Customer booking app
│   ├── staff/               # Staff management app
│   ├── manager/             # Salon manager app
│   └── owner/               # Owner dashboard
├── services/                # Backend microservices
│   ├── api/                 # Core API service
│   ├── ai/                  # AI agent service
│   └── notification/        # WhatsApp/SMS service
├── infrastructure/          # Infrastructure configs
│   └── local/               # Local development
│       └── firebase/        # Firebase emulator config
├── .a0proj/                 # Agent Zero project config
├── docker-compose.yml       # Local development setup
└── README.md
```

## 🧪 Testing

```bash
# Run all tests
docker-compose run api-service pytest

# Run with coverage
docker-compose run api-service pytest --cov=app
```

## 🚢 Deployment to GCP

After successful local testing:

1. Set up GCP project and Firebase
2. Configure GitHub Actions secrets
3. Push to `main` branch
4. CI/CD pipeline deploys to Cloud Run

## 📝 License

MIT License
