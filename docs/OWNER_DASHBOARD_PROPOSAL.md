# Salon Flow Owner Dashboard - Production Build Proposal

## 📋 Executive Summary

This proposal outlines the complete design and implementation plan for the **Owner Dashboard** - a production-ready React PWA for salon owners to manage their business, powered by AI agents and real-time analytics.

---

## 🎯 Key Features

### Core Dashboard
- **Real-time KPIs**: Today's bookings, revenue, new customers, occupancy rate
- **Quick Actions**: New booking, send campaign, view reports, AI assistant
- **Upcoming Bookings**: Live list with status indicators and staff assignments
- **Activity Feed**: Real-time updates via WebSocket

### Management Modules
| Module | Features |
|--------|----------|
| **Bookings** | Calendar view, list view, status management, walk-in booking |
| **Staff** | Roster management, performance metrics, availability calendar |
| **Customers** | Search, loyalty tracking, membership status, history |
| **Analytics** | Revenue trends, service popularity, peak hours, staff performance |
| **Revenue** | Daily/monthly reports, payment methods, GST invoices |
| **AI Assistant** | 25 specialized agents, streaming chat, business insights |
| **Settings** | Salon config, Twilio integration, team management |

---

## 🏗️ Architecture

### Tech Stack
```
Frontend:    React 18 + TypeScript + Vite
Styling:     Tailwind CSS + Custom Design System
State:       Zustand (global) + React Query (server)
Routing:     React Router v6
Icons:       Lucide React
Charts:      Recharts
Auth:        Firebase JWT + Role-based access
Real-time:   WebSocket (Notification Service)
```

### Component Architecture
```
apps/owner/src/
├── components/
│   ├── ui/              # 8 base components (Button, Card, Badge, etc.)
│   ├── layout/          # Sidebar, Header, DashboardLayout
│   ├── dashboard/       # StatCard, BookingCard, ActivityFeed, AIWidget
│   └── features/        # Page-specific feature components
├── pages/
│   ├── Dashboard.tsx    # Main overview
│   ├── Bookings.tsx     # Booking management
│   ├── Staff.tsx        # Staff management
│   ├── Customers.tsx    # Customer insights
│   ├── Analytics.tsx    # Reports & trends
│   ├── Revenue.tsx      # Financial reports
│   ├── AIAssistant.tsx  # Full AI chat interface
│   └── Settings/        # Configuration pages
├── services/
│   ├── api.ts           # Axios instance with interceptors
│   ├── authService.ts   # Authentication logic
│   ├── analyticsService.ts
│   └── aiService.ts     # SSE streaming support
├── hooks/
│   ├── useAuth.ts       # Auth context & token management
│   ├── useWebSocket.ts  # Real-time updates
│   └── useAI.ts         # AI chat with streaming
└── stores/
    └── appStore.ts      # Global Zustand store
```

---

## 🎨 Design System

### Color Palette
| Color | Hex | Usage |
|-------|-----|-------|
| Primary | `#2563eb` | Actions, links, focus states |
| Secondary | `#9333ea` | AI features, highlights |
| Accent | `#db2777` | Salon branding, CTAs |
| Success | `#16a34a` | Completed, positive trends |
| Warning | `#d97706` | Alerts, pending states |
| Error | `#dc2626` | Errors, negative trends |

### Typography
- **Font**: Inter (system fallbacks)
- **Scale**: 12px → 36px (8 steps)
- **Weights**: 400, 500, 600, 700

### Responsive Breakpoints
```
sm:  640px  (Small tablets)
md:  768px  (Tablets)
lg:  1024px (Laptops)
xl:  1280px (Desktops)
2xl: 1536px (Large screens)
```

---

## 🤖 AI Integration

### Available Agents (25 Total)

| Priority | Agents | Dashboard Location |
|----------|--------|-------------------|
| **P0** | Booking, Marketing, Analytics, Support | Global AI Widget + Page Panels |
| **P1** | Upsell Engine, Dynamic Pricing, Slot Optimizer, Waitlist Manager | Revenue & Schedule Pages |
| **P2** | Inventory, Staff Scheduling, Customer Retention, Bundle Creator | Respective Management Pages |
| **P3** | Demand Predictor, WhatsApp Concierge (monitor) | Analytics & Integrations |

### AI Features
1. **Global AI Widget** - Floating chat accessible from any page
2. **Contextual Panels** - Page-specific insights and actions
3. **Quick Actions** - One-click AI operations ("Optimize Schedule", "Generate Campaign")
4. **Streaming Responses** - SSE for real-time token display
5. **Multi-language** - English, Hindi, Telugu support

---

## 🔐 Security & Auth

### Authentication Flow
1. Firebase Auth (Email/Password or OTP)
2. JWT token exchange via `/auth/firebase`
3. Tokens stored: Access in `localStorage`, Refresh in `sessionStorage`
4. Auto-refresh on 401 via Axios interceptor

### Role-Based Access
| Role | Access Level |
|------|-------------|
| Owner | Full access to all features |
| Manager | Operations, staff, analytics (no billing) |
| Receptionist | Bookings, customers, check-in/out |
| Stylist | Own schedule, service delivery |

### Multi-Tenant Isolation
- All API requests include `salon_id` from JWT claims
- Backend enforces data isolation automatically
- Frontend never manually sets `salon_id`

---

## 📊 Data Flow

### Real-time Updates
| Data Type | Update Method | Frequency |
|-----------|---------------|-----------|
| Dashboard metrics | Polling (React Query) | 30-60 seconds |
| Today's bookings | WebSocket | Real-time |
| Staff availability | Optimistic + refetch | On change |
| Revenue updates | Polling | 5 minutes |
| AI chat | SSE | Streaming |

### Caching Strategy
```typescript
// React Query Configuration
staleTime: {
  dashboard: 30 seconds,
  bookings: 1 minute,
  staff: 5 minutes,
  services: 10 minutes,
  analytics: 5 minutes
}
```

---

## 📱 Page Designs

### 1. Dashboard Overview
```
┌─────────────────────────────────────────────────────────────┐
│  Good morning, Owner!                    🔔  👤 Profile     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ Bookings │ │ Revenue │ │Customers│ │Occupancy│           │
│  │   24     │ │  ₹12.4K │ │   5     │ │   85%   │           │
│  │  +12% ↑  │ │  +8% ↑  │ │  +2     │ │  +5% ↑  │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
├─────────────────────────────────────────────────────────────┤
│  Quick Actions                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │➕ Booking │ │📢 Campaign│ │📊 Reports│ │🤖 AI Help│       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
├─────────────────────────────────────────────────────────────┤
│  Upcoming Bookings          │  Recent Activity              │
│  ┌─────────────────────┐   │  • New booking by Rahul       │
│  │ 10:00 - Rahul M.    │   │  • Payment received ₹2,500   │
│  │ Haircut + Beard     │   │  • Campaign sent to 150      │
│  │ Status: Confirmed   │   │  • Staff Priya checked in    │
│  └─────────────────────┘   │                               │
│  ┌─────────────────────┐   │                               │
│  │ 11:30 - Priya S.    │   │                               │
│  │ Bridal Makeup       │   │                               │
│  └─────────────────────┘   │                               │
└─────────────────────────────────────────────────────────────┘
│  🤖 AI Assistant (floating widget - bottom right)          │
└─────────────────────────────────────────────────────────────┘
```

### 2. Bookings Management
- Calendar view with date picker
- List view with filters (status, staff, service)
- Booking cards with quick actions
- Walk-in quick booking modal

### 3. Staff Management
- Staff cards with performance metrics
- Availability calendar
- Skill assignment matrix
- Shift scheduling

### 4. Analytics Dashboard
- Revenue trends (daily/monthly charts)
- Service popularity breakdown
- Peak hours heatmap
- Staff performance comparison
- Customer acquisition trends

### 5. AI Assistant Page
- Full-page chat interface
- Agent selector dropdown
- Quick action suggestions
- Conversation history
- Context-aware responses

---

## 🚀 Implementation Plan

### Phase 1: Foundation (Week 1-2)
| Task | Description |
|------|-------------|
| Project Setup | Configure Vite, Tailwind, TypeScript |
| Design System | Implement base UI components |
| Layout | Sidebar, Header, DashboardLayout |
| Auth Flow | Login, token management, protected routes |

### Phase 2: Core Pages (Week 3-4)
| Task | Description |
|------|-------------|
| Dashboard | Connect to `/analytics/dashboard` API |
| Bookings | List view, filters, status management |
| Staff | Roster, availability, performance |
| Real-time | WebSocket integration for live updates |

### Phase 3: Advanced Features (Week 5-6)
| Task | Description |
|------|-------------|
| Analytics | Charts, trends, reports |
| Revenue | Financial reports, GST invoices |
| AI Widget | Floating chat with streaming |
| Settings | Salon config, Twilio integration |

### Phase 4: Polish & Deploy (Week 7-8)
| Task | Description |
|------|-------------|
| Testing | Jest unit tests, Playwright E2E |
| Performance | Lazy loading, code splitting |
| PWA | Service worker, offline support |
| Deployment | Cloud Run, CDN, domain |

---

## 💰 Cost Estimate

| Component | Monthly Cost (₹) |
|-----------|------------------|
| Cloud Run (Frontend) | 0-500 |
| CDN + Storage | 100 |
| **Total Additional** | **100-600** |

*Note: Backend and AI costs already accounted in existing budget (₹6,660/month)*

---

## ✅ Approval Required

Please review and approve the following:

1. **Design System** - Color palette, typography, component library
2. **Page Structure** - Navigation, page hierarchy, feature grouping
3. **AI Integration** - Agent accessibility, chat interface, quick actions
4. **Implementation Timeline** - 8-week phased approach

### Questions for Clarification

1. **Branding**: Should we use Jawed Habib brand colors or custom salon branding?
2. **Multi-location**: Do you need support for managing multiple salon locations?
3. **Offline Mode**: Is offline functionality required for areas with poor connectivity?
4. **Mobile App**: Should we prioritize mobile-responsive web or native app?

---

**Please approve this proposal to begin implementation.**
