# Salon Flow Owner PWA - Architecture Document

**Version:** 1.0.0  
**Date:** 2026-02-22  
**Status:** Foundation Phase (Task 1.1 Complete)

---

## 1. Overview

The Owner PWA is an AI-native, mobile-first Progressive Web Application designed for salon owners to manage their business operations efficiently. Built with React 18, TypeScript, and Tailwind CSS, it follows Atomic Design principles for scalable component architecture.

### Key Principles
- **Mobile-First:** Optimized for mobile devices with PWA capabilities
- **AI-Native:** Proactive AI insights integrated throughout the UI
- **Atomic Design:** Component hierarchy from atoms to pages
- **Type-Safe:** Full TypeScript coverage
- **Performance:** Optimized bundle size with code splitting

---

## 2. Folder Structure

```
apps/owner/src/
├── components/
│   ├── atoms/           # Basic building blocks
│   │   ├── Button/
│   │   ├── Input/
│   │   ├── Icon/
│   │   ├── Badge/
│   │   ├── Avatar/
│   │   ├── Skeleton/
│   │   └── index.ts
│   ├── molecules/       # Combinations of atoms
│   │   ├── FormField/
│   │   ├── SearchBar/
│   │   ├── StatValue/
│   │   ├── ListItem/
│   │   └── index.ts
│   ├── organisms/       # Complex components
│   │   ├── BookingCard/
│   │   ├── StatCard/
│   │   ├── CustomerCard/
│   │   ├── StaffCard/
│   │   ├── AIInsightCard/
│   │   └── index.ts
│   ├── templates/       # Page layouts
│   │   ├── MobileLayout/
│   │   ├── DashboardLayout/
│   │   ├── AuthLayout/
│   │   └── index.ts
│   └── pages/           # Screen components
│       ├── DashboardPage/
│       ├── BookingsPage/
│       ├── CustomersPage/
│       ├── StaffPage/
│       ├── SettingsPage/
│       └── index.ts
├── hooks/               # Custom React hooks
│   ├── useAuth.ts
│   ├── useBookings.ts
│   ├── useCustomers.ts
│   ├── useStaff.ts
│   ├── useAI.ts
│   ├── useOffline.ts
│   └── index.ts
├── stores/              # Zustand state management
│   ├── authStore.ts
│   ├── bookingStore.ts
│   ├── customerStore.ts
│   ├── staffStore.ts
│   ├── uiStore.ts
│   └── index.ts
├── services/            # API clients
│   ├── api/
│   │   ├── client.ts
│   │   ├── bookings.ts
│   │   ├── customers.ts
│   │   ├── staff.ts
│   │   └── index.ts
│   ├── ai/
│   │   ├── agentClient.ts
│   │   ├── streaming.ts
│   │   └── index.ts
│   └── firebase/
│       ├── auth.ts
│       ├── firestore.ts
│       └── index.ts
├── utils/               # Helper functions
│   ├── date.ts
│   ├── currency.ts
│   ├── validation.ts
│   ├── constants.ts
│   └── index.ts
├── types/               # TypeScript definitions
│   ├── booking.ts
│   ├── customer.ts
│   ├── staff.ts
│   ├── api.ts
│   ├── ai.ts
│   └── index.ts
├── styles/              # Global styles, theme
│   ├── theme.ts
│   ├── globals.css
│   └── index.ts
└── lib/                 # Third-party configurations
    ├── utils.ts
    └── firebase.ts
```

---

## 3. Component Architecture

### 3.1 Atomic Design Hierarchy

#### Atoms (Foundation)
- **Button:** Primary, secondary, ghost, icon variants
- **Input:** Text, number, date, search variants
- **Icon:** Lucide icons with size/color props
- **Badge:** Status, count, notification variants
- **Avatar:** User images with fallback initials
- **Skeleton:** Loading placeholders

#### Molecules (Combinations)
- **FormField:** Label + Input + Error message
- **SearchBar:** Input + Icon + Clear button
- **StatValue:** Value + Label + Trend indicator
- **ListItem:** Icon + Text + Action

#### Organisms (Complex Components)
- **BookingCard:** Customer info + Service + Time + Status
- **StatCard:** Icon + Value + Label + Trend + Sparkline
- **AIInsightCard:** Insight type + Message + Action buttons
- **CustomerCard:** Avatar + Name + Phone + Last visit

#### Templates (Layouts)
- **MobileLayout:** Header + Content + TabBar
- **DashboardLayout:** Sidebar (desktop) + Content area
- **AuthLayout:** Centered card with branding

#### Pages (Screens)
- **DashboardPage:** Stats + AI insights + Quick actions
- **BookingsPage:** Calendar + Booking list
- **CustomersPage:** Search + Customer grid
- **StaffPage:** Staff list + Performance metrics

---

## 4. Design Token System

### 4.1 Colors

```typescript
// Primary Palette - Indigo/Purple
primary: {
  50: '#eef2ff',
  100: '#e0e7ff',
  200: '#c7d2fe',
  300: '#a5b4fc',
  400: '#818cf8',
  500: '#6366f1',  // Primary
  600: '#4f46e5',  // Primary hover
  700: '#4338ca',
  800: '#3730a3',
  900: '#312e81',
}

// Secondary - Rose/Pink
secondary: {
  50: '#fff1f2',
  100: '#ffe4e6',
  200: '#fecdd3',
  300: '#fda4af',
  400: '#fb7185',
  500: '#f43f5e',
  600: '#e11d48',
  700: '#be123c',
  800: '#9f1239',
  900: '#881337',
}

// Semantic Colors
success: '#22c55e',
warning: '#f59e0b',
error: '#ef4444',
info: '#3b82f6',

// Surface Colors
surface: {
  light: '#ffffff',
  dark: '#0f172a',
  muted: '#f1f5f9',
}
```

### 4.2 Typography

```typescript
fontFamily: {
  sans: ['Inter', 'system-ui', 'sans-serif'],
  display: ['Plus Jakarta Sans', 'Inter', 'sans-serif'],
}

fontSize: {
  '2xs': '0.625rem',   // 10px - Captions
  'xs': '0.75rem',     // 12px - Small text
  'sm': '0.875rem',    // 14px - Body small
  'base': '1rem',      // 16px - Body
  'lg': '1.125rem',    // 18px - Lead
  'xl': '1.25rem',     // 20px - H4
  '2xl': '1.5rem',     // 24px - H3
  '3xl': '1.875rem',   // 30px - H2
  '4xl': '2.25rem',    // 36px - H1
}
```

### 4.3 Spacing

```typescript
// Base unit: 4px
spacing: {
  '0': '0',
  '1': '0.25rem',   // 4px
  '2': '0.5rem',    // 8px
  '3': '0.75rem',   // 12px
  '4': '1rem',      // 16px
  '5': '1.25rem',   // 20px
  '6': '1.5rem',    // 24px
  '8': '2rem',      // 32px
  '10': '2.5rem',   // 40px
  '12': '3rem',     // 48px
  '16': '4rem',     // 64px
}
```

### 4.4 Border Radius

```typescript
borderRadius: {
  'none': '0',
  'sm': '0.125rem',   // 2px
  'DEFAULT': '0.25rem', // 4px
  'md': '0.375rem',   // 6px
  'lg': '0.5rem',     // 8px
  'xl': '0.75rem',    // 12px
  '2xl': '1rem',      // 16px
  '3xl': '1.5rem',    // 24px
  'full': '9999px',
}
```

### 4.5 Shadows

```typescript
boxShadow: {
  'sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  'DEFAULT': '0 1px 3px 0 rgb(0 0 0 / 0.1)',
  'md': '0 4px 6px -1px rgb(0 0 0 / 0.1)',
  'lg': '0 10px 15px -3px rgb(0 0 0 / 0.1)',
  'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1)',
  'card': '0 1px 3px rgba(0, 0, 0, 0.1)',
  'card-hover': '0 10px 40px rgba(0, 0, 0, 0.1)',
  'glow': '0 0 20px rgba(99, 102, 241, 0.3)',
}
```

---

## 5. State Management

### 5.1 Zustand Stores

```typescript
// authStore.ts
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
}

// uiStore.ts
interface UIState {
  theme: 'light' | 'dark';
  isOffline: boolean;
  activeTab: string;
  setTheme: (theme: 'light' | 'dark') => void;
}

// bookingStore.ts
interface BookingState {
  bookings: Booking[];
  selectedDate: Date;
  filters: BookingFilters;
  fetchBookings: () => Promise<void>;
}
```

---

## 6. API Integration

### 6.1 REST API Client

```typescript
// services/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### 6.2 AI Streaming

```typescript
// services/ai/streaming.ts
export const streamAIResponse = async (
  message: string,
  onChunk: (chunk: string) => void
) => {
  const response = await fetch('/api/ai/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  
  const reader = response.body?.getReader();
  // Handle streaming...
};
```

---

## 7. Navigation Structure

### 7.1 Mobile Tab Bar (5 Tabs)

1. **Home** - Dashboard with AI insights
2. **Bookings** - Calendar and booking management
3. **Customers** - CRM and customer profiles
4. **Staff** - Staff management and scheduling
5. **More** - Settings, AI Assistant, Analytics

### 7.2 Route Structure

```typescript
const routes = [
  { path: '/', component: DashboardPage, tab: 'home' },
  { path: '/bookings', component: BookingsPage, tab: 'bookings' },
  { path: '/bookings/:id', component: BookingDetailPage },
  { path: '/customers', component: CustomersPage, tab: 'customers' },
  { path: '/customers/:id', component: CustomerDetailPage },
  { path: '/staff', component: StaffPage, tab: 'staff' },
  { path: '/settings', component: SettingsPage, tab: 'more' },
  { path: '/ai', component: AIAssistantPage, tab: 'more' },
];
```

---

## 8. PWA Configuration

### 8.1 Manifest

```json
{
  "name": "Salon Flow - Owner",
  "short_name": "Salon Flow",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#6366f1",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192" },
    { "src": "/icon-512.png", "sizes": "512x512" }
  ]
}
```

### 8.2 Service Worker

- Cache static assets
- Background sync for offline mutations
- Push notifications

---

## 9. Migration Path

### From Existing Structure

| Old Location | New Location |
|--------------|--------------|
| `components/ui/` | `components/atoms/` |
| `components/dashboard/` | `components/organisms/` |
| `components/layout/` | `components/templates/` |
| `pages/` | `components/pages/` |
| `hooks/` | `hooks/` (unchanged) |
| `stores/` | `stores/` (unchanged) |

### Gradual Migration
1. Create new folder structure
2. Move components incrementally
3. Update imports
4. Remove old folders once complete

---

## 10. Success Criteria

- [x] Architecture document created
- [x] Folder structure implemented
- [x] Design tokens defined
- [x] Tailwind config updated
- [x] Base layout components created
- [x] Code compiles without errors
- [x] Handoff document prepared

---

## 11. Next Steps

1. **Task 1.2:** Design System Implementation
2. **Task 1.3:** Component Library Setup
3. **Task 1.4:** State Management Setup

---

*Document Version: 1.0.0*  
*Last Updated: 2026-02-22*  
*Author: Solutions Architect*
