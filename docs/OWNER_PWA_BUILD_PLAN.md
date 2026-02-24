
# 🎯 SALON FLOW OWNER PWA - PRODUCTION BUILD PLAN
## AI-Native, Mobile-First, Production-Ready Implementation

**Reference Assets:** 27 UI Mockups in `/a0/usr/projects/salon_flow/docs/mockups/`  
**Target:** Production deployment with full AI integration  
**Timeline:** 8 weeks (4 phases)  
**Team:** 7 Expert Agents  

---

## 📋 EXECUTIVE SUMMARY

### Current System State
| Component | Status | Tests |
|-----------|--------|-------|
| Backend API | ✅ Production Ready | 166/166 passing |
| AI Service | ✅ Production Ready | 461/461 passing |
| Cloud Run Services | ✅ Deployed & Healthy | 5 services |
| Owner PWA | ⚠️ Needs Rebuild | Mockups ready |

### Build Objectives
1. Implement all 16 UI screens from mockups (27 PNG references)
2. Integrate 25+ AI agents via existing AI service
3. Achieve 90%+ test coverage with Playwright E2E
4. Deploy to production with CI/CD pipeline

---

## 🏗️ PHASE 1: FOUNDATION & SETUP (Week 1-2)
**Goal:** Project structure, design system, authentication

### Task 1.1: Project Architecture Setup
**Agent:** Solutions Architect  
**Priority:** P0  
**Dependencies:** None  
**Deliverables:**
- [ ] Audit existing `apps/owner/` structure
- [ ] Define component architecture (Atomic Design)
- [ ] Set up design token system (colors, typography, spacing)
- [ ] Configure Tailwind with custom theme matching mockups
- [ ] Set up folder structure: `components/`, `pages/`, `hooks/`, `services/`, `stores/`
- [ ] Create base layout components (MobileFrame, TabBar, Header)

**Reference:** Mockups 01-05 (Onboarding), 06 (Dashboard)  
**Files:** `apps/owner/src/styles/theme.ts`, `tailwind.config.js`

### Task 1.2: Design System Implementation
**Agent:** Frontend Developer  
**Priority:** P0  
**Dependencies:** Task 1.1  
**Deliverables:**
- [ ] Create shadcn/ui component library setup
- [ ] Implement color palette from mockups (indigo/purple gradients)
- [ ] Create typography scale (mobile-optimized)
- [ ] Build reusable components:
  - [ ] `StatCard` - Dashboard KPI cards
  - [ ] `BookingCard` - Appointment display
  - [ ] `CustomerCard` - Customer list items
  - [ ] `StaffCard` - Staff member display
  - [ ] `AIWidget` - AI assistant floating button
  - [ ] `InsightBar` - Global AI insights banner
  - [ ] `ActionButton` - Primary/secondary actions
  - [ ] `InputField` - Form inputs with validation
  - [ ] `Modal` - Dialogs and bottom sheets
  - [ ] `TabNavigation` - 5-tab mobile nav

**Reference:** All mockups for component extraction  
**Files:** `apps/owner/src/components/ui/`, `apps/owner/src/components/common/`

### Task 1.3: Authentication & State Management
**Agent:** Frontend Developer  
**Priority:** P0  
**Dependencies:** Task 1.1  
**Deliverables:**
- [ ] Set up Zustand store architecture
- [ ] Implement AuthStore (login, logout, token refresh)
- [ ] Create TenantStore (multi-tenant context)
- [ ] Implement ProtectedRoute wrapper
- [ ] Set up API client with interceptors
- [ ] Configure Firebase Auth integration
- [ ] Create auth hooks: `useAuth()`, `useTenant()`

**Reference:** Mockup 01 (Welcome screen with login)  
**Files:** `apps/owner/src/stores/`, `apps/owner/src/hooks/`, `apps/owner/src/services/api.ts`

### Task 1.4: PWA Configuration
**Agent:** Frontend Developer  
**Priority:** P1  
**Dependencies:** Task 1.1  
**Deliverables:**
- [ ] Configure Vite PWA plugin
- [ ] Create manifest.json with icons
- [ ] Set up service worker for offline support
- [ ] Configure caching strategies
- [ ] Add "Add to Home Screen" prompt
- [ ] Test PWA installability

**Files:** `apps/owner/vite.config.ts`, `apps/owner/public/manifest.json`

---

## 🎨 PHASE 2: ONBOARDING FLOW (Week 2-3)
**Goal:** Complete 5-step onboarding wizard

### Task 2.1: Onboarding Step 1 - Welcome & Salon Creation
**Agent:** Frontend Developer  
**Priority:** P0  
**Dependencies:** Task 1.3  
**Deliverables:**
- [ ] Create `OnboardingLayout` with progress indicator
- [ ] Build `WelcomeScreen` with brand introduction
- [ ] Implement `SalonDetailsForm`:
  - [ ] Salon name input
  - [ ] Address with map picker
  - [ ] GST number field
  - [ ] Contact information
  - [ ] Logo upload
- [ ] Add form validation with Zod
- [ ] Connect to backend onboarding API

**Reference:** Mockups 01, 02  
**Files:** `apps/owner/src/pages/onboarding/Step1Welcome.tsx`, `apps/owner/src/pages/onboarding/Step2SalonDetails.tsx`

### Task 2.2: Onboarding Step 2 - Layout Configuration
**Agent:** Frontend Developer  
**Priority:** P0  
**Dependencies:** Task 2.1  
**Deliverables:**
- [ ] Build visual layout designer
- [ ] Create drag-and-drop chair/station placement
- [ ] Implement room/section management
- [ ] Add capacity configuration
- [ ] Save layout to backend

**Reference:** Mockup 03  
**Files:** `apps/owner/src/pages/onboarding/Step3Layout.tsx`, `apps/owner/src/components/layout/LayoutDesigner.tsx`

### Task 2.3: Onboarding Step 3 - Services Setup
**Agent:** Frontend Developer  
**Priority:** P0  
**Dependencies:** Task 2.2  
**Deliverables:**
- [ ] Fetch service templates from backend
- [ ] Create service selection grid
- [ ] Implement service customization:
  - [ ] Duration settings
  - [ ] Pricing configuration
  - [ ] Category assignment
- [ ] Add "Add Custom Service" functionality
- [ ] Bulk import from templates

**Reference:** Mockup 04  
**Files:** `apps/owner/src/pages/onboarding/Step4Services.tsx`, `apps/owner/src/components/services/ServiceSelector.tsx`

### Task 2.4: Onboarding Step 4 - Staff Setup
**Agent:** Frontend Developer  
**Priority:** P0  
**Dependencies:** Task 2.3  
**Deliverables:**
- [ ] Build staff invitation form
- [ ] Create role assignment (Owner, Manager, Stylist, etc.)
- [ ] Implement specialization selection
- [ ] Add commission structure setup
- [ ] Create staff schedule template

**Reference:** Mockup 05  
**Files:** `apps/owner/src/pages/onboarding/Step5Staff.tsx`, `apps/owner/src/components/staff/StaffInviteForm.tsx`

### Task 2.5: Onboarding Step 5 - Business Hours
**Agent:** Frontend Developer  
**Priority:** P0  
**Dependencies:** Task 2.4  
**Deliverables:**
- [ ] Create weekly schedule grid
- [ ] Implement time picker for each day
- [ ] Add break/lunch time configuration
- [ ] Set up holiday/special hours
- [ ] Complete onboarding and redirect to dashboard

**Files:** `apps/owner/src/pages/onboarding/Step6Hours.tsx`, `apps/owner/src/components/schedule/BusinessHoursForm.tsx`

---

## 📊 PHASE 3: CORE DASHBOARD & OPERATIONS (Week 3-5)
**Goal:** Main dashboard and booking management

### Task 3.1: Dashboard Home Screen
**Agent:** Frontend Developer  
**Priority:** P0  
**Dependencies:** Task 1.3  
**Deliverables:**
- [ ] Build dashboard layout with 5-tab navigation
- [ ] Implement KPI cards:
  - [ ] Today's revenue
  - [ ] Active bookings
  - [ ] Staff utilization
  - [ ] Customer count
- [ ] Add "Why?" and "Optimize" AI action buttons
- [ ] Create quick action grid
- [ ] Implement "Morning Pulse" summary card
- [ ] Add real-time updates via WebSocket

**Reference:** Mockups 06, 14  
**Files:** `apps/owner/src/pages/dashboard/Home.tsx`, `apps/owner/src/components/dashboard/KPICard.tsx`

### Task 3.2: Bookings Calendar View
**Agent:** Frontend Developer  
**Priority:** P0  
**Dependencies:** Task 3.1  
**Deliverables:**
- [ ] Implement calendar component (day/week/month views)
- [ ] Create booking slot visualization
- [ ] Add drag-and-drop rescheduling
- [ ] Build filter controls (staff, service, status)
- [ ] Implement color-coding for booking status
- [ ] Add "New Booking" floating button

**Reference:** Mockup 07  
**Files:** `apps/owner/src/pages/bookings/Calendar.tsx`, `apps/owner/src/components/calendar/BookingCalendar.tsx`

### Task 3.3: New Booking Flow
**Agent:** Frontend Developer  
**Priority:** P0  
**Dependencies:** Task 3.2  
**Deliverables:**
- [ ] Create multi-step booking wizard:
  - [ ] Step 1: Select customer (search/create new)
  - [ ] Step 2: Choose services
  - [ ] Step 3: Select staff & time slot
  - [ ] Step 4: Confirm & payment
- [ ] Implement AI slot suggestions
- [ ] Add customer history sidebar
- [ ] Create booking confirmation modal

**Reference:** Mockup 08  
**Files:** `apps/owner/src/pages/bookings/NewBooking.tsx`, `apps/owner/src/components/bookings/BookingWizard.tsx`

### Task 3.4: Customer Management (CRM)
**Agent:** Frontend Developer  
**Priority:** P1  
**Dependencies:** Task 3.1  
**Deliverables:**
- [ ] Build customer list with search/filter
- [ ] Create customer profile page:
  - [ ] Personal details
  - [ ] Booking history
  - [ ] Preferences & notes
  - [ ] Membership status
  - [ ] Communication history
- [ ] Implement customer segmentation
- [ ] Add "Send Message" WhatsApp integration

**Reference:** Mockup 09  
**Files:** `apps/owner/src/pages/customers/List.tsx`, `apps/owner/src/pages/customers/Profile.tsx`

---

## 👥 PHASE 4: MANAGEMENT & ANALYTICS (Week 5-6)
**Goal:** Staff management and business intelligence

### Task 4.1: Staff Management
**Agent:** Frontend Developer  
**Priority:** P1  
**Dependencies:** Task 3.1  
**Deliverables:**
- [ ] Create staff list view
- [ ] Build staff profile pages:
  - [ ] Personal info & photo
  - [ ] Schedule & availability
  - [ ] Performance metrics
  - [ ] Commission tracking
  - [ ] Service assignments
- [ ] Implement shift management
- [ ] Add attendance tracking

**Reference:** Mockup 10  
**Files:** `apps/owner/src/pages/staff/List.tsx`, `apps/owner/src/pages/staff/Profile.tsx`

### Task 4.2: Analytics Dashboard
**Agent:** Frontend Developer + AI Engineer  
**Priority:** P1  
**Dependencies:** Task 3.1  
**Deliverables:**
- [ ] Build analytics overview page
- [ ] Implement charts:
  - [ ] Revenue trends (line chart)
  - [ ] Service popularity (bar chart)
  - [ ] Staff performance (radar chart)
  - [ ] Customer acquisition (funnel)
- [ ] Add date range selector
- [ ] Create exportable reports
- [ ] Integrate AI insights

**Reference:** Mockup 11  
**Files:** `apps/owner/src/pages/analytics/Dashboard.tsx`, `apps/owner/src/components/analytics/Charts.tsx`

### Task 4.3: AI Assistant Interface
**Agent:** AI Engineer + Frontend Developer  
**Priority:** P0  
**Dependencies:** Task 3.1  
**Deliverables:**
- [ ] Create floating AI widget button
- [ ] Build chat interface (fullscreen & overlay)
- [ ] Implement streaming message display
- [ ] Add quick action suggestions
- [ ] Create conversation history
- [ ] Integrate with AI service WebSocket
- [ ] Add voice input support

**Reference:** Mockup 12  
**Files:** `apps/owner/src/components/ai/AIChat.tsx`, `apps/owner/src/services/ai.ts`

---

## ⚙️ PHASE 5: SETTINGS & SYSTEM (Week 6-7)
**Goal:** Configuration and system management

### Task 5.1: Settings Panel
**Agent:** Frontend Developer  
**Priority:** P1  
**Dependencies:** Task 3.1  
**Deliverables:**
- [ ] Create settings categories:
  - [ ] Business Profile
  - [ ] Services & Pricing
  - [ ] Staff & Permissions
  - [ ] Notifications
  - [ ] Integrations (WhatsApp, Payments)
  - [ ] Billing & Subscription
- [ ] Implement dark mode toggle
- [ ] Add language selection
- [ ] Create backup/export options

**Reference:** Mockup 13  
**Files:** `apps/owner/src/pages/settings/Index.tsx`, `apps/owner/src/pages/settings/BusinessProfile.tsx`

### Task 5.2: Notifications Center
**Agent:** Frontend Developer  
**Priority:** P2  
**Dependencies:** Task 3.1  
**Deliverables:**
- [ ] Build notifications list
- [ ] Implement notification categories:
  - [ ] Booking alerts
  - [ ] Staff updates
  - [ ] AI insights
  - [ ] System messages
- [ ] Add notification preferences
- [ ] Create push notification setup

**Reference:** Mockup 15  
**Files:** `apps/owner/src/pages/notifications/Index.tsx`

### Task 5.3: Payments & Billing
**Agent:** Frontend Developer  
**Priority:** P1  
**Dependencies:** Task 3.1  
**Deliverables:**
- [ ] Create payments dashboard
- [ ] Implement transaction history
- [ ] Add payment method management
- [ ] Build invoice generator
- [ ] Create subscription management
- [ ] Integrate with payment gateway

**Reference:** Mockup 16  
**Files:** `apps/owner/src/pages/payments/Index.tsx`, `apps/owner/src/components/payments/TransactionList.tsx`

---

## 🤖 PHASE 6: AI INTEGRATION (Week 4-7)
**Goal:** Deep AI agent integration throughout app

### Task 6.1: AI Service Client
**Agent:** AI Engineer  
**Priority:** P0  
**Dependencies:** Task 1.3  
**Deliverables:**
- [ ] Create AI service client
- [ ] Implement streaming response handler
- [ ] Add request/response caching
- [ ] Create error handling & retry logic
- [ ] Build agent routing system
- [ ] Add context management

**Files:** `apps/owner/src/services/aiClient.ts`, `apps/owner/src/hooks/useAI.ts`

### Task 6.2: Proactive AI Insights
**Agent:** AI Engineer  
**Priority:** P0  
**Dependencies:** Task 6.1, Task 3.1  
**Deliverables:**
- [ ] Implement "Morning Pulse" generation
- [ ] Create insight cards for dashboard
- [ ] Build "Gap Detection" alerts
- [ ] Add "No-Show Prediction" warnings
- [ ] Implement "Revenue Opportunity" suggestions
- [ ] Create AI-driven KPI explanations

**Reference:** Mockup 14 (Morning Pulse)  
**Files:** `apps/owner/src/components/ai/InsightsBar.tsx`, `apps/owner/src/hooks/useInsights.ts`

### Task 6.3: Agent-Specific Features
**Agent:** AI Engineer  
**Priority:** P1  
**Dependencies:** Task 6.1  
**Deliverables:**
- [ ] Booking Agent: Smart slot suggestions
- [ ] Slot Optimizer: Gap filling UI
- [ ] Marketing Agent: Campaign creator
- [ ] Analytics Agent: Natural language queries
- [ ] Retention Agent: At-risk customer alerts
- [ ] Pricing Agent: Dynamic pricing suggestions

**Files:** `apps/owner/src/components/ai/agents/`

---

## 🧪 PHASE 7: TESTING & QUALITY (Week 6-8)
**Goal:** Comprehensive test coverage

### Task 7.1: Unit & Integration Tests
**Agent:** QA Engineer  
**Priority:** P0  
**Dependencies:** All development tasks  
**Deliverables:**
- [ ] Set up Vitest testing framework
- [ ] Write unit tests for components (80% coverage)
- [ ] Create integration tests for API calls
- [ ] Test state management logic
- [ ] Mock AI service responses

**Files:** `apps/owner/src/**/*.test.tsx`, `apps/owner/src/**/*.test.ts`

### Task 7.2: E2E Testing with Playwright
**Agent:** QA Engineer  
**Priority:** P0  
**Dependencies:** Task 7.1  
**Deliverables:**
- [ ] Create E2E test suite:
  - [ ] Onboarding flow tests
  - [ ] Authentication tests
  - [ ] Dashboard functionality tests
  - [ ] Booking management tests
  - [ ] Customer management tests
  - [ ] AI chat tests
- [ ] Add visual regression tests
- [ ] Test PWA installability
- [ ] Test offline functionality
- [ ] Mobile viewport testing

**Files:** `tests/e2e/owner-*.spec.ts`

### Task 7.3: Performance Optimization
**Agent:** QA Engineer + Frontend Developer  
**Priority:** P1  
**Dependencies:** Task 7.2  
**Deliverables:**
- [ ] Run Lighthouse audits (target: 90+ all categories)
- [ ] Optimize bundle size (code splitting)
- [ ] Implement lazy loading for routes
- [ ] Add image optimization
- [ ] Optimize AI response caching
- [ ] Test on low-end devices

**Files:** `apps/owner/src/routes/`, `apps/owner/vite.config.ts`

---

## 🚀 PHASE 8: DEPLOYMENT & PRODUCTION (Week 7-8)
**Goal:** Production deployment and monitoring

### Task 8.1: Production Build Setup
**Agent:** DevOps Engineer  
**Priority:** P0  
**Dependencies:** Task 7.3  
**Deliverables:**
- [ ] Configure production environment variables
- [ ] Set up Docker build optimization
- [ ] Create multi-stage Dockerfile
- [ ] Configure nginx for SPA routing
- [ ] Set up Cloud Build pipeline
- [ ] Optimize for Cloud Run deployment

**Files:** `apps/owner/Dockerfile`, `apps/owner/nginx.conf`, `deploy/`

### Task 8.2: CI/CD Pipeline
**Agent:** DevOps Engineer  
**Priority:** P0  
**Dependencies:** Task 8.1  
**Deliverables:**
- [ ] Create GitHub Actions workflow:
  - [ ] Lint & type check
  - [ ] Run unit tests
  - [ ] Run E2E tests
  - [ ] Build & push Docker image
  - [ ] Deploy to Cloud Run
- [ ] Set up staging environment
- [ ] Configure automated rollback
- [ ] Add deployment notifications

**Files:** `.github/workflows/owner-deploy.yml`

### Task 8.3: Monitoring & Analytics
**Agent:** DevOps Engineer  
**Priority:** P1  
**Dependencies:** Task 8.2  
**Deliverables:**
- [ ] Set up error tracking (Sentry)
- [ ] Configure performance monitoring
- [ ] Add user analytics (posthog/plausible)
- [ ] Create uptime monitoring
- [ ] Set up log aggregation
- [ ] Build admin dashboard

**Files:** `apps/owner/src/services/monitoring.ts`

---

## 📊 TASK SUMMARY

| Phase | Tasks | Duration | Agents |
|-------|-------|----------|--------|
| 1. Foundation | 4 tasks | 2 weeks | Frontend, Architect |
| 2. Onboarding | 5 tasks | 1.5 weeks | Frontend |
| 3. Core Operations | 4 tasks | 2 weeks | Frontend |
| 4. Management | 3 tasks | 1.5 weeks | Frontend, AI |
| 5. Settings | 3 tasks | 1 week | Frontend |
| 6. AI Integration | 3 tasks | 3 weeks (parallel) | AI Engineer |
| 7. Testing | 3 tasks | 2 weeks | QA |
| 8. Deployment | 3 tasks | 1.5 weeks | DevOps |

**Total Tasks:** 28  
**Total Duration:** 8 weeks (with parallel work)  
**Critical Path:** 1.1 → 1.2 → 1.3 → 2.1 → 3.1 → 6.1 → 6.2 → 7.2 → 8.2

---

## 🎯 SUCCESS CRITERIA

### Functional
- [ ] All 16 screens implemented matching mockups
- [ ] 25+ AI agents integrated and functional
- [ ] Complete onboarding flow working end-to-end
- [ ] Real-time updates via WebSocket
- [ ] Offline mode functional

### Quality
- [ ] 90%+ unit test coverage
- [ ] 100% E2E test pass rate
- [ ] Lighthouse score 90+ (all categories)
- [ ] Zero critical security vulnerabilities
- [ ] WCAG 2.1 AA accessibility compliance

### Performance
- [ ] First Contentful Paint < 1.5s
- [ ] Time to Interactive < 3s
- [ ] Bundle size < 500KB (gzipped)
- [ ] AI response time < 2s average

### Production
- [ ] Deployed to Cloud Run
- [ ] CI/CD pipeline operational
- [ ] Monitoring & alerting active
- [ ] Documentation complete
- [ ] Handover to operations team

---

## 📁 DELIVERABLES

### Code
- Complete Owner PWA in `apps/owner/`
- Reusable component library
- Custom hooks and utilities
- Type definitions

### Tests
- Unit tests (Vitest)
- Integration tests
- E2E tests (Playwright)
- Performance benchmarks

### Documentation
- Component storybook
- API integration guide
- Deployment runbook
- User manual

### Assets
- All 27 mockups as reference
- Design system documentation
- Icon library
- Animation specifications

---

## ⚠️ RISKS & MITIGATION

| Risk | Impact | Mitigation |
|------|--------|------------|
| AI integration complexity | High | Start early, use existing AI service |
| Mockup interpretation | Medium | Weekly design reviews with user |
| Performance on low-end devices | Medium | Regular testing on target devices |
| Backend API changes | Low | Lock API contracts before start |
| Timeline slippage | Medium | Parallel workstreams, buffer time |

---

## ✅ APPROVAL CHECKLIST

Before starting implementation, confirm:
- [ ] Task breakdown is comprehensive
- [ ] Timeline is acceptable
- [ ] Agent assignments are appropriate
- [ ] Mockup references are clear
- [ ] Success criteria are measurable
- [ ] Risk mitigation is acceptable

**Ready to assign tasks to expert agents upon approval!**
