# Salon Flow Owner PWA - AI-Native UI Implementation Plan

## Executive Summary

Transform the Owner PWA from a traditional dashboard to an AI-native "Co-Pilot" experience that prioritizes proactive insights over reactive operations.

## Design Philosophy

### Core Principles
1. **Insights Over Operations** - Surface strategic intelligence, not just data
2. **AI as Co-Pilot** - AI proactively suggests actions, user decides
3. **5-Second Rule** - Key insights visible within 5 seconds
4. **Mobile-First** - Designed for on-the-go salon owners
5. **Trust Through Transparency** - Always show AI reasoning

## Architecture Overview

### Navigation Structure (5-Tab Mobile-First)

```
┌─────────────────────────────────────────────────────────────┐
│                        OWNER PWA                             │
├─────────────────────────────────────────────────────────────┤
│  🏠 Home    💰 Revenue    👥 Customers    💇 Staff    🤖 AI  │
│  (Pulse)    (Money)       (People)        (Team)      (Hub)  │
└─────────────────────────────────────────────────────────────┘
```

### Component Hierarchy

```
src/
├── components/
│   ├── ai/
│   │   ├── AIInsightsBar.tsx       # Global proactive alerts
│   │   ├── MorningPulseCheck.tsx   # Daily AI summary
│   │   ├── AIChatWidget.tsx        # Floating chat interface
│   │   ├── AIPoweredCard.tsx       # KPI cards with AI insights
│   │   ├── CampaignGenerator.tsx   # AI marketing creator
│   │   └── InsightExplanation.tsx  # "Why?" explanations
│   ├── layout/
│   │   ├── MobileTabBar.tsx        # Bottom navigation
│   │   ├── Header.tsx              # Top header with AI status
│   │   └── AIProvider.tsx          # AI context wrapper
│   └── dashboard/
│       ├── PulseDashboard.tsx      # Home/AI Pulse view
│       ├── RevenueDashboard.tsx    # Financial insights
│       ├── CustomerInsights.tsx    # Customer analytics
│       └── StaffPerformance.tsx    # Team metrics
├── hooks/
│   ├── useAIInsights.ts            # Fetch AI recommendations
│   ├── useMorningPulse.ts          # Daily summary hook
│   └── useStreamingChat.ts         # SSE chat streaming
└── services/
    ├── aiService.ts                # AI API client
    └── streamingService.ts         # SSE handler
```

## Phase 1: Foundation (Week 1-2)

### 1.1 Mobile-First Navigation
- [ ] Create `MobileTabBar.tsx` with 5 tabs
- [ ] Implement responsive layout with bottom navigation
- [ ] Add gesture support for tab switching
- [ ] Create tab-specific headers

### 1.2 AI Context & State
- [ ] Create `AIProvider.tsx` for global AI state
- [ ] Implement `useAIInsights.ts` hook
- [ ] Set up SSE streaming infrastructure
- [ ] Create AI status indicator in header

### 1.3 Core AI Components
- [ ] Build `AIInsightsBar.tsx` - Global alert bar
- [ ] Build `MorningPulseCheck.tsx` - Daily summary modal
- [ ] Build `AIPoweredCard.tsx` - Smart KPI cards

## Phase 2: AI Pulse Dashboard (Week 3-4)

### 2.1 Home/Pulse View
```
┌─────────────────────────────────────────────────────────────┐
│ Good Morning, Rajesh!                    🔔 3    👤 Profile  │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🌅 Morning Pulse Check                                  │ │
│ │ "You have 18 bookings today (3 high-value). 2 gaps      │ │
│ │  detected. Potential revenue: ₹12,500. I suggest        │ │
│ │  offering 15% discount to fill the 2 PM gap."           │ │
│ │                                    [View Details] [✓]   │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 💰 Today's Revenue                    ↑ 12% vs yesterday│ │
│ │ ₹24,500                                                 │ │
│ │ [Sparkline showing trend]                                │ │
│ │ 💡 "Hair coloring is trending. Consider adding a        │ │
│ │      senior stylist shift on Saturday." [Optimize]     │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 📅 Today's Schedule                                      │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ 10:00 │ 👤 Priya Sharma    │ Hair Cut    │ ₹500  │ ✓ │ │ │
│ │ │ 10:45 │ 👤 Amit Kumar      │ Beard Trim  │ ₹300  │ ✓ │ │ │
│ │ │ 11:30 │ ⚠️ GAP - 45 min    │ Fill?       │ ₹400  │ 🤖│ │ │
│ │ │ 12:15 │ 👤 Sneha Reddy     │ Hair Color  │ ₹2,500│ ⭐│ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🤖 AI Recommendations                                    │ │
│ │ • 3 customers haven't visited in 30+ days [Win-back]    │ │
│ │ • Inventory alert: Hair serum low (3 left) [Order]      │ │
│ │ • Peak pricing opportunity: Saturday 2-5 PM [Enable]    │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 AI-Powered KPI Cards
- [ ] Revenue card with trend analysis
- [ ] Bookings card with gap detection
- [ ] Customer card with retention alerts
- [ ] Staff card with performance insights

## Phase 3: Revenue Dashboard (Week 5-6)

### 3.1 Financial Insights
```
┌─────────────────────────────────────────────────────────────┐
│ 💰 Revenue Dashboard                    This Week ▼         │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 📊 Revenue Trend                                         │ │
│ │ [Chart showing weekly revenue with AI annotations]       │ │
│ │ 💡 "Revenue up 15% due to Diwali promotions.             │ │
│ │      Consider extending offer by 3 days." [Apply]       │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌───────────────────┐ ┌───────────────────┐                 │
│ │ 💵 Cash           │ │ 💳 Digital        │                 │
│ │ ₹45,000 (60%)     │ │ ₹30,000 (40%)     │                 │
│ └───────────────────┘ └───────────────────┘                 │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🎯 Dynamic Pricing Suggestions                           │ │
│ │ • Saturday 2-5 PM: +20% peak pricing [Enable]           │ │
│ │ • Monday-Wed: -10% off-peak discount [Enable]           │ │
│ │ • Festival pricing: Diwali package +25% [Active]        │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Phase 4: Customer Insights (Week 7-8)

### 4.1 Customer Analytics
```
┌─────────────────────────────────────────────────────────────┐
│ 👥 Customer Insights                    This Month ▼        │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ⚠️ At-Risk Customers (5)                                 │ │
│ │ 💡 "These customers haven't visited in 30+ days.         │ │
│ │      Sending personalized offers could recover ₹8,500." │ │
│ │ [Create Win-back Campaign]                               │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌───────────────────┐ ┌───────────────────┐                 │
│ │ 🌟 VIP Customers   │ │ 🎂 Birthdays      │                 │
│ │ 42 (13% revenue)   │ │ 8 this month      │                 │
│ └───────────────────┘ └───────────────────┘                 │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 📈 Customer Segments                                     │ │
│ │ • Loyal (156): Visit monthly, high LTV                   │ │
│ │ • At-Risk (23): Declining visit frequency                │ │
│ │ • New (45): First visit in last 30 days                  │ │
│ │ • Dormant (89): No visit in 60+ days                     │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Phase 5: AI Hub (Week 9-10)

### 5.1 AI Command Center
```
┌─────────────────────────────────────────────────────────────┐
│ 🤖 AI Hub                              Salon Status: Active │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 📢 Campaign Generator                                    │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ Type: [Promotional ▼]  Target: [At-Risk ▼]          │ │ │
│ │ │ Occasion: [Diwali ▼]                                 │ │ │
│ │ │                                                      │ │ │
│ │ │ [Generate Campaign]                                  │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🤖 Active AI Agents                                      │ │
│ │ • Slot Optimizer: Running (5 gaps detected)             │ │
│ │ • Waitlist Manager: 3 customers waiting                 │ │
│ │ • Retention Agent: 2 win-back campaigns active          │ │
│ │ • Inventory Monitor: 1 alert pending                    │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 💬 AI Chat                                               │ │
│ │ [Chat interface with streaming responses]                │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Technical Implementation

### API Integration

```typescript
// AI Service Endpoints
const AI_ENDPOINTS = {
  chat: '/api/v1/chat',
  morningPulse: '/api/v1/analytics/insights/{salon_id}',
  recommendations: '/api/v1/analytics/recommendations/{salon_id}',
  gapDetection: '/api/v1/agents/slot-optimizer/detect-gaps',
  atRiskCustomers: '/api/v1/agents/retention/at-risk-customers',
  campaignGenerator: '/api/v1/marketing/campaign',
  dynamicPricing: '/api/v1/agents/dynamic-pricing/demand-analysis',
};
```

### Streaming Chat Implementation

```typescript
// hooks/useStreamingChat.ts
export function useStreamingChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);

  const sendMessage = async (content: string) => {
    setIsStreaming(true);
    
    const response = await fetch(`${AI_URL}/api/v1/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: content, session_id: sessionId }),
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    while (reader) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value);
      // Parse SSE and update messages
    }
    
    setIsStreaming(false);
  };

  return { messages, sendMessage, isStreaming };
}
```

## File Structure

```
apps/owner/src/
├── components/
│   ├── ai/
│   │   ├── AIInsightsBar.tsx
│   │   ├── MorningPulseCheck.tsx
│   │   ├── AIChatWidget.tsx
│   │   ├── AIPoweredCard.tsx
│   │   ├── CampaignGenerator.tsx
│   │   ├── InsightExplanation.tsx
│   │   └── index.ts
│   ├── layout/
│   │   ├── MobileTabBar.tsx
│   │   ├── Header.tsx
│   │   ├── AIProvider.tsx
│   │   └── index.ts
│   └── dashboard/
│       ├── PulseDashboard.tsx
│       ├── RevenueDashboard.tsx
│       ├── CustomerInsights.tsx
│       ├── StaffPerformance.tsx
│       └── index.ts
├── hooks/
│   ├── useAIInsights.ts
│   ├── useMorningPulse.ts
│   ├── useStreamingChat.ts
│   └── index.ts
├── services/
│   ├── aiService.ts
│   ├── streamingService.ts
│   └── index.ts
└── types/
    ├── ai.ts
    └── index.ts
```

## Success Metrics

| Metric | Target |
|--------|--------|
| Time to first insight | < 5 seconds |
| AI recommendation acceptance | > 40% |
| Daily active usage | > 80% |
| Campaign generation time | < 30 seconds |
| Revenue impact | +15% in 3 months |

## Dependencies

- Backend API: All 86 endpoints operational ✅
- AI Service: All 54 endpoints operational ✅
- Notification Service: SMS/WhatsApp ready ✅
- Firebase Auth: Configured ✅

