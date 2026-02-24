# Salon Flow Frontend Development Roadmap

## Current State (v0.3.0)

### Owner PWA (~30% Complete)
- ✅ Project setup (Vite, TypeScript, Tailwind CSS)
- ✅ Layout components (Sidebar, Header, DashboardLayout)
- ✅ Core UI components (Button, Card, Badge, Input, Modal, Avatar, Skeleton)
- ✅ Dashboard widgets (StatCard, BookingCard, ActivityFeed, QuickActions, AIWidget)
- ✅ Dashboard page
- ✅ Settings/Integrations page
- ❌ Bookings module
- ❌ Customers module
- ❌ Staff module
- ❌ Analytics module
- ❌ Payments module
- ❌ AI Assistant chat interface
- ❌ Authentication flow

### Manager PWA (0% - Scaffold only)
- ✅ Project scaffold
- ❌ All features

### Staff PWA (0% - Scaffold only)
- ✅ Project scaffold
- ❌ All features

### Client PWA (0% - Scaffold only)
- ✅ Project scaffold
- ❌ All features

---

## Phase 1: Shared Infrastructure (Week 1)

### FE-001: Shared Component Library
**Priority: P0**
- Create `/packages/ui` with shared components
- Extract common components from Owner PWA
- Set up Storybook for component documentation

### FE-002: Shared Utilities & Hooks
**Priority: P0**
- Create `/packages/shared` with:
  - API client (axios wrapper with auth)
  - Firebase hooks
  - Common utilities (formatters, validators)
  - Custom hooks (useAuth, useSalon, useBookings)

### FE-003: Authentication System
**Priority: P0**
- Firebase Auth integration
- Login/Register pages
- Password reset flow
- Role-based routing
- Token refresh handling

---

## Phase 2: Owner PWA Completion (Weeks 2-3)

### FE-004: Bookings Module
**Priority: P0**
- Calendar view (full-calendar integration)
- List view with filters
- Booking CRUD operations
- Walk-in management
- Resource assignment

### FE-005: Customers Module
**Priority: P1**
- Customer list with search/filter
- Customer profile page
- Booking history
- Loyalty points display
- Membership status

### FE-006: Staff Module
**Priority: P1**
- Staff list with roles
- Staff profile page
- Schedule management
- Performance metrics
- Commission tracking

### FE-007: Analytics Module
**Priority: P1**
- Revenue charts (Recharts)
- Booking trends
- Customer insights
- Staff performance
- Export functionality

### FE-008: Payments Module
**Priority: P1**
- Transaction history
- Payment methods
- Refund processing
- GST invoices

### FE-009: AI Assistant Interface
**Priority: P2**
- Chat interface with streaming
- Agent selection
- Context-aware suggestions
- Marketing generator
- Schedule optimizer

---

## Phase 3: Manager PWA (Week 4)

### FE-010: Manager Dashboard
**Priority: P0**
- Today's overview
- Staff attendance
- Booking alerts
- Quick actions

### FE-011: Manager Bookings
**Priority: P0**
- Calendar view
- Booking management
- Walk-in handling

### FE-012: Manager Staff
**Priority: P1**
- Staff schedules
- Leave approvals
- Performance overview

---

## Phase 4: Staff PWA (Week 5)

### FE-013: Staff Dashboard
**Priority: P0**
- Today's appointments
- Service queue
- Quick status updates

### FE-014: Staff Schedule
**Priority: P0**
- Weekly schedule view
- Shift management
- Leave requests

### FE-015: Staff Services
**Priority: P1**
- Service completion
- Upsell suggestions
- Customer notes

---

## Phase 5: Client PWA (Week 6)

### FE-016: Client Booking Flow
**Priority: P0**
- Service selection
- Stylist selection
- Time slot picker
- Confirmation

### FE-017: Client Profile
**Priority: P1**
- Booking history
- Loyalty points
- Membership status
- Preferences

### FE-018: Client Chat
**Priority: P2**
- WhatsApp-style interface
- AI Concierge integration
- Booking via chat

---

## Tech Stack

- **Framework:** React 18 + TypeScript
- **Build:** Vite
- **Styling:** Tailwind CSS
- **State:** Zustand + React Query
- **Charts:** Recharts
- **Calendar:** FullCalendar
- **Forms:** React Hook Form + Zod
- **Icons:** Lucide React
- **Auth:** Firebase Auth
- **API:** REST with axios

---

## Development Commands

```bash
# Install all dependencies
npm install

# Run Owner PWA
cd apps/owner && npm run dev

# Run Manager PWA
cd apps/manager && npm run dev

# Run Staff PWA
cd apps/staff && npm run dev

# Run Client PWA
cd apps/client && npm run dev

# Run all tests
npm run test

# Build all apps
npm run build:all
```

---

## Success Metrics

- [ ] All 4 PWAs deployed and functional
- [ ] Lighthouse score > 90 for all apps
- [ ] Mobile-first responsive design
- [ ] Offline capability (PWA)
- [ ] < 3s initial load time
- [ ] Role-based access control working
- [ ] Real-time updates via WebSocket
