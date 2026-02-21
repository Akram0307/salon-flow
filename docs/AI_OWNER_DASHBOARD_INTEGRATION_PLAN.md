# Salon Flow: AI Agent Integration Plan for Owner Dashboard

## Executive Summary

This document provides a comprehensive integration plan for connecting the Owner Dashboard frontend with the AI Service's 25+ specialized agents. The plan covers UI/UX design, technical implementation, and performance optimization strategies.

---

## 1. AI Agent Integration Points

### 1.1 Agent Accessibility Matrix

| Agent | Dashboard Access | UI Location | Priority | Use Case |
|-------|-----------------|-------------|----------|----------|
| **Booking** | ✅ Full | AI Assistant, Bookings Page | P0 | Slot suggestions, stylist matching |
| **Marketing** | ✅ Full | Marketing Tab | P0 | Campaign generation, content creation |
| **Analytics** | ✅ Full | Dashboard, Analytics Page | P0 | Business insights, trend analysis |
| **Support** | ✅ Full | AI Assistant | P1 | Customer complaint handling, FAQs |
| **Upsell Engine** | ✅ Full | Revenue Tab | P1 | Add-on suggestions, upgrade recommendations |
| **Dynamic Pricing** | ✅ Full | Services, Revenue Tab | P1 | Peak/off-peak pricing, festival pricing |
| **Slot Optimizer** | ✅ Full | Schedule Page | P1 | Gap detection, fill strategies |
| **Waitlist Manager** | ✅ Full | Bookings Page | P1 | Cancellation handling, priority queue |
| **Inventory Intelligence** | ✅ Full | Inventory Tab | P2 | Stock alerts, reorder predictions |
| **Staff Scheduling** | ✅ Full | Staff Page | P2 | Weekly schedules, shift optimization |
| **Customer Retention** | ✅ Full | Customers Page | P2 | At-risk detection, win-back campaigns |
| **Bundle Creator** | ✅ Full | Services, Marketing | P2 | Bridal/groom packages, seasonal bundles |
| **WhatsApp Concierge** | ⚠️ Monitor Only | Integrations Page | P2 | Conversation logs, handoff alerts |
| **Demand Predictor** | ✅ Full | Analytics, Staffing | P3 | Demand forecasting, resource planning |
| **Voice Receptionist** | ⚠️ Monitor Only | Integrations Page | P3 | Call logs, booking confirmations |

### 1.2 Recommended UI Presentation

#### A. Global AI Assistant (Floating Widget)
```
┌─────────────────────────────────────────────────────────────┐
│  💬 AI Assistant                                    [−] [×] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🤖 How can I help you today?                        │   │
│  │                                                     │   │
│  │ I can help with:                                    │   │
│  │ • Booking suggestions & stylist matching            │   │
│  │ • Marketing campaign creation                       │   │
│  │ • Business analytics & insights                     │   │
│  │ • Customer support & complaints                     │   │
│  │ • Revenue optimization strategies                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 👤 Show me today's booking gaps                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🤖 I found 3 gaps in today's schedule:             │   │
│  │                                                     │   │
│  │ ⏰ 11:00-11:45 - Priya (45 min gap)                │   │
│  │   → Suggest: Quick trim or touch-up services       │   │
│  │   → 3 customers nearby could fill this slot        │   │
│  │                                                     │   │
│  │ ⏰ 14:30-15:30 - Rahul (60 min gap)                │   │
│  │   → Potential revenue loss: ₹800                   │   │
│  │   → [Send targeted offers] [View customers]        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 💡 Quick Actions:                                   │   │
│  │ [📊 Business Summary] [📈 Revenue Tips]            │   │
│  │ [📢 Create Campaign] [👥 Customer Insights]        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🔵 Type a message...                          [Send]│   │
│  └─────────────────────────────────────────────────────┘   │
│  Confidence: 92% | Model: Gemini 2.5 Flash | ⚡ Cached    │
└─────────────────────────────────────────────────────────────┘
```

#### B. Contextual AI Panels (Page-Specific)

**Dashboard Page - AI Insights Panel:**
```
┌─────────────────────────────────────────────────────────────┐
│ 📊 Today's AI Insights                          [Refresh]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 🔔 Revenue Opportunity                                       │
│ "You have 3 high-value customers who haven't booked in     │
│  30+ days. Send a personalized offer to potentially        │
│  recover ₹4,500 in revenue."                               │
│ [Create Win-back Campaign]                                  │
│                                                             │
│ ─────────────────────────────────────────────────────────  │
│                                                             │
│ 📈 Trend Alert                                              │
│ "Hair coloring services are up 23% this week. Consider     │
│  adding a senior stylist shift on Saturday afternoon."     │
│ [Adjust Schedule] [View Details]                            │
│                                                             │
│ ─────────────────────────────────────────────────────────  │
│                                                             │
│ ⚠️ Inventory Alert                                          │
│ "Hair serum stock is running low (3 units left). Based on  │
│  usage patterns, you'll need to reorder in 4 days."       │
│ [Create Purchase Order]                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Marketing Page - Campaign Generator:**
```
┌─────────────────────────────────────────────────────────────┐
│ 📢 AI Campaign Generator                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Campaign Type:  [Promotional ▼]                             │
│ Target:         [Loyal Customers ▼]                         │
│ Occasion:       [Diwali ▼]                                  │
│                                                             │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ 🤖 Generating campaign...                          │   │
│ │ ████████████████████████████████░░░░ 85%           │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                             │
│ Generated Campaign:                                         │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ Headline: "Diwali Glow Up! ✨"                      │   │
│ │                                                     │   │
│ │ Message: "This festive season, let your beauty      │   │
│ │ shine! Book your Diwali makeover and enjoy 20%     │   │
│ │ off on all hair & beauty services."                │   │
│ │                                                     │   │
│ │ CTA: "Book Now - Limited Slots!"                   │   │
│ │ Best Send Time: 10:00 AM, Oct 28                    │   │
│ │ Channels: WhatsApp, SMS                             │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                             │
│ [Edit] [Regenerate] [Preview] [Send Now] [Schedule]        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Chat Interface Design

### 2.1 Streaming Response Implementation (SSE)

**Backend Enhancement Required:**
```python
# services/ai/app/api/chat.py - Add streaming endpoint

from fastapi.responses import StreamingResponse
import asyncio

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint using Server-Sent Events"""
    
    async def generate_stream():
        session_id = request.session_id or str(uuid.uuid4())
        agent = get_agent(request.agent_type)
        context = await get_salon_context(request.salon_id)
        
        # Send session ID first
        yield f"data: {{\"type\": \"session\", \"session_id\": \"{session_id}\"}}\n\n"
        
        # Stream response chunks
        full_response = ""
        async for chunk in agent.generate_stream(
            prompt=request.message,
            context=context,
            history=sessions.get(session_id, [])
        ):
            full_response += chunk
            yield f"data: {{\"type\": \"token\", \"content\": \"{chunk}\"}}\n\n"
        
        # Send completion with metadata
        yield f"data: {{\"type\": \"done\", \"message\": \"{full_response}\", \"confidence\": 0.92}}\n\n"
        
        # Update session
        sessions[session_id] = sessions.get(session_id, [])[-8:] + [
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": full_response}
        ]
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
```

**Frontend Service Layer:**
```typescript
// apps/owner/src/services/aiChatService.ts

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  confidence?: number;
  cached?: boolean;
}

export interface StreamCallbacks {
  onSession: (sessionId: string) => void;
  onToken: (token: string) => void;
  onComplete: (message: ChatMessage) => void;
  onError: (error: Error) => void;
}

export class AIChatService {
  private baseUrl = import.meta.env.VITE_AI_SERVICE_URL;
  
  async sendMessage(
    message: string,
    salonId: string,
    sessionId: string | null,
    agentType: string = 'booking',
    callbacks: StreamCallbacks
  ): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/v1/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        salon_id: salonId,
        session_id: sessionId,
        agent_type: agentType,
      }),
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    while (reader) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n').filter(line => line.startsWith('data: '));

      for (const line of lines) {
        const data = JSON.parse(line.slice(6));
        
        switch (data.type) {
          case 'session':
            callbacks.onSession(data.session_id);
            break;
          case 'token':
            callbacks.onToken(data.content);
            break;
          case 'done':
            callbacks.onComplete({
              role: 'assistant',
              content: data.message,
              timestamp: new Date(),
              confidence: data.confidence,
              cached: data.cached,
            });
            break;
          case 'error':
            callbacks.onError(new Error(data.message));
            break;
        }
      }
    }
  }
}
```

### 2.2 Multi-Language Support

**Language Detection & Response:**
```typescript
// apps/owner/src/hooks/useLanguageDetection.ts

const LANGUAGE_PATTERNS = {
  hindi: /[\u0900-\u097F]/,
  telugu: /[\u0C00-\u0C7F]/,
  english: /^[a-zA-Z0-9\s\p{P}]+$/u,
};

export function detectLanguage(text: string): 'en' | 'hi' | 'te' {
  if (LANGUAGE_PATTERNS.telugu.test(text)) return 'te';
  if (LANGUAGE_PATTERNS.hindi.test(text)) return 'hi';
  return 'en';
}

// Send language preference in context
const context = {
  preferred_language: detectLanguage(userMessage),
  salon_locale: 'en-IN',
};
```

**Backend Guardrails Integration:**
```python
# Already implemented in services/ai/app/core/guardrails.py
# SalonGuardrails class handles:
# - Language detection (en, hi, te)
# - Response language matching
# - Cultural context awareness
```

### 2.3 Context Management

**Session Context Structure:**
```typescript
interface SessionContext {
  salon_id: string;
  user_id: string;
  user_role: 'owner' | 'manager' | 'staff';
  current_page: string;
  selected_entity?: {
    type: 'booking' | 'customer' | 'staff' | 'service';
    id: string;
  };
  time_context: {
    timezone: string;
    current_time: string;
    selected_date?: string;
  };
  business_context: {
    salon_name: string;
    currency: string;
    active_staff_count: number;
    today_bookings_count: number;
  };
}
```

### 2.4 Conversation History

**React Hook for Chat State:**
```typescript
// apps/owner/src/hooks/useAIChat.ts

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ChatState {
  sessions: Record<string, ChatMessage[]>;
  activeSessionId: string | null;
  
  addMessage: (sessionId: string, message: ChatMessage) => void;
  getHistory: (sessionId: string) => ChatMessage[];
  clearSession: (sessionId: string) => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      sessions: {},
      activeSessionId: null,
      
      addMessage: (sessionId, message) => set(state => ({
        sessions: {
          ...state.sessions,
          [sessionId]: [...(state.sessions[sessionId] || []), message],
        },
      })),
      
      getHistory: (sessionId) => get().sessions[sessionId] || [],
      
      clearSession: (sessionId) => set(state => {
        const { [sessionId]: _, ...rest } = state.sessions;
        return { sessions: rest };
      }),
    }),
    {
      name: 'ai-chat-history',
      partialize: (state) => ({
        sessions: Object.fromEntries(
          Object.entries(state.sessions).slice(-5) // Keep last 5 sessions
        ),
      }),
    }
  )
);
```

---

## 3. AI-Powered Features

### 3.1 Business Insights Dashboard

**Component Architecture:**
```tsx
// apps/owner/src/components/AI/BusinessInsights.tsx

import { useQuery } from '@tanstack/react-query';

export function BusinessInsights({ salonId }: { salonId: string }) {
  const { data: insights, isLoading } = useQuery({
    queryKey: ['ai-insights', salonId],
    queryFn: () => fetchAIInsights(salonId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 15 * 60 * 1000, // Refresh every 15 min
  });

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {/* Revenue Opportunity Card */}
      <InsightCard
        type="opportunity"
        title="Revenue Opportunity"
        icon="💰"
        insight={insights?.revenue_opportunity}
        actionLabel="View Details"
        onAction={() => {/* Navigate to revenue page */}}
      />
      
      {/* Trend Alert Card */}
      <InsightCard
        type="trend"
        title="Trending Services"
        icon="📈"
        insight={insights?.trending_services}
        actionLabel="Adjust Services"
      />
      
      {/* Customer Insight Card */}
      <InsightCard
        type="alert"
        title="At-Risk Customers"
        icon="⚠️"
        insight={insights?.at_risk_customers}
        actionLabel="Create Campaign"
        variant="warning"
      />
    </div>
  );
}
```

**API Integration:**
```typescript
// apps/owner/src/services/insightsService.ts

export async function fetchAIInsights(salonId: string) {
  const response = await fetch(
    `${AI_SERVICE_URL}/api/v1/agents/retention/at-risk-customers`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        salon_id: salonId,
        customer_data: await fetchCustomerData(salonId),
        visit_threshold_days: 45,
      }),
    }
  );
  return response.json();
}
```

### 3.2 Marketing Campaign Generator

**Full Implementation:**
```tsx
// apps/owner/src/components/AI/CampaignGenerator.tsx

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';

interface CampaignFormData {
  campaign_type: 'promotional' | 'seasonal' | 'loyalty' | 'birthday';
  target_audience: {
    segment: string;
    min_visits?: number;
    last_visit_days?: number;
  };
  offer_details: {
    discount_percent?: number;
    services?: string[];
    validity_days: number;
  };
}

export function CampaignGenerator({ salonId }: { salonId: string }) {
  const [formData, setFormData] = useState<CampaignFormData>({
    campaign_type: 'promotional',
    target_audience: { segment: 'all' },
    offer_details: { validity_days: 7 },
  });
  
  const [generatedCampaign, setGeneratedCampaign] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);

  const generateMutation = useMutation({
    mutationFn: async () => {
      setIsStreaming(true);
      const response = await fetch(
        `${AI_SERVICE_URL}/api/v1/marketing/campaign`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            salon_id: salonId,
            ...formData,
          }),
        }
      );
      return response.json();
    },
    onSuccess: (data) => {
      setGeneratedCampaign(data);
      setIsStreaming(false);
    },
  });

  return (
    <div className="space-y-6">
      {/* Campaign Type Selection */}
      <CampaignTypeSelector
        value={formData.campaign_type}
        onChange={(type) => setFormData(prev => ({ ...prev, campaign_type: type }))}
      />
      
      {/* Target Audience */}
      <AudienceSelector
        value={formData.target_audience}
        onChange={(audience) => setFormData(prev => ({ ...prev, target_audience: audience }))}
      />
      
      {/* Offer Details */}
      <OfferBuilder
        value={formData.offer_details}
        onChange={(offer) => setFormData(prev => ({ ...prev, offer_details: offer }))}
      />
      
      {/* Generate Button */}
      <button
        onClick={() => generateMutation.mutate()}
        disabled={isStreaming}
        className="btn-primary"
      >
        {isStreaming ? (
          <><Spinner /> Generating Campaign...</>
        ) : (
          'Generate Campaign'
        )}
      </button>
      
      {/* Generated Campaign Preview */}
      {generatedCampaign && (
        <CampaignPreview
          campaign={generatedCampaign}
          onEdit={() => {}}
          onRegenerate={() => generateMutation.mutate()}
          onSend={() => {/* Send via WhatsApp/SMS */}}
        />
      )}
    </div>
  );
}
```

### 3.3 Revenue Optimization Suggestions

**Dynamic Pricing Panel:**
```tsx
// apps/owner/src/components/AI/DynamicPricingPanel.tsx

export function DynamicPricingPanel({ salonId }: { salonId: string }) {
  const { data: pricingSuggestions } = useQuery({
    queryKey: ['dynamic-pricing', salonId],
    queryFn: () => fetchPricingSuggestions(salonId),
  });

  return (
    <div className="space-y-4">
      {/* Peak Period Pricing */}
      <div className="card">
        <h3 className="text-lg font-semibold">Peak Period Pricing</h3>
        <div className="mt-4 space-y-2">
          {pricingSuggestions?.peak_periods?.map((period) => (
            <div key={period.id} className="flex justify-between items-center">
              <span>{period.time_range}</span>
              <span className="text-green-600">+{period.suggested_increase}%</span>
              <button className="btn-sm">Apply</button>
            </div>
          ))}
        </div>
      </div>
      
      {/* Off-Peak Discounts */}
      <div className="card">
        <h3 className="text-lg font-semibold">Off-Peak Discounts</h3>
        <div className="mt-4 space-y-2">
          {pricingSuggestions?.off_peak?.map((period) => (
            <div key={period.id} className="flex justify-between items-center">
              <span>{period.time_range}</span>
              <span className="text-blue-600">-{period.suggested_discount}%</span>
              <button className="btn-sm">Apply</button>
            </div>
          ))}
        </div>
      </div>
      
      {/* Festival Pricing */}
      <div className="card">
        <h3 className="text-lg font-semibold">Upcoming Festival Pricing</h3>
        <div className="mt-4">
          {pricingSuggestions?.festivals?.map((festival) => (
            <div key={festival.name} className="border-b py-2">
              <div className="flex justify-between">
                <span className="font-medium">{festival.name}</span>
                <span className="text-sm text-gray-500">{festival.dates}</span>
              </div>
              <p className="text-sm text-gray-600 mt-1">{festival.recommendation}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

### 3.4 Staff Scheduling Recommendations

**Schedule Optimization Component:**
```tsx
// apps/owner/src/components/AI/ScheduleOptimizer.tsx

export function ScheduleOptimizer({ salonId, date }: Props) {
  const [optimizing, setOptimizing] = useState(false);
  const [suggestions, setSuggestions] = useState(null);

  const optimizeSchedule = async () => {
    setOptimizing(true);
    const response = await fetch(
      `${AI_SERVICE_URL}/api/v1/agents/scheduling/optimize-shifts`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          salon_id: salonId,
          current_schedule: await fetchCurrentSchedule(salonId, date),
          demand_patterns: await fetchDemandPatterns(salonId),
          staff_preferences: await fetchStaffPreferences(salonId),
        }),
      }
    );
    setSuggestions(await response.json());
    setOptimizing(false);
  };

  return (
    <div className="space-y-4">
      <button
        onClick={optimizeSchedule}
        disabled={optimizing}
        className="btn-primary"
      >
        {optimizing ? 'Analyzing Schedule...' : 'AI Optimize Schedule'}
      </button>
      
      {suggestions && (
        <div className="space-y-4">
          {/* Gap Detection Results */}
          <div className="card">
            <h4>Detected Gaps</h4>
            {suggestions.gaps?.map((gap) => (
              <GapCard key={gap.id} gap={gap} onFill={handleFillGap} />
            ))}
          </div>
          
          {/* Skill Match Suggestions */}
          <div className="card">
            <h4>Skill-Demand Alignment</h4>
            {suggestions.skill_matches?.map((match) => (
              <SkillMatchCard key={match.staff_id} match={match} />
            ))}
          </div>
          
          {/* Overtime Warnings */}
          {suggestions.overtime_warnings?.length > 0 && (
            <div className="card border-yellow-200 bg-yellow-50">
              <h4 className="text-yellow-800">Overtime Alerts</h4>
              {suggestions.overtime_warnings.map((warning) => (
                <OvertimeWarning key={warning.staff_id} warning={warning} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

### 3.5 Inventory Alerts

**Real-time Inventory Intelligence:**
```tsx
// apps/owner/src/components/AI/InventoryAlerts.tsx

export function InventoryAlerts({ salonId }: { salonId: string }) {
  const { data: alerts } = useQuery({
    queryKey: ['inventory-alerts', salonId],
    queryFn: () => fetchInventoryAlerts(salonId),
    refetchInterval: 60000, // Every minute
  });

  return (
    <div className="space-y-3">
      {/* Critical Alerts */}
      {alerts?.critical?.map((alert) => (
        <div key={alert.product_id} className="card border-red-200 bg-red-50">
          <div className="flex items-center gap-2">
            <span className="text-red-600">⚠️</span>
            <span className="font-semibold text-red-800">Low Stock: {alert.product_name}</span>
          </div>
          <p className="text-sm text-red-700 mt-1">
            Only {alert.current_stock} units left. Estimated stockout: {alert.stockout_date}
          </p>
          <div className="mt-2 flex gap-2">
            <button className="btn-sm btn-primary">Quick Order</button>
            <button className="btn-sm">View Usage</button>
          </div>
        </div>
      ))}
      
      {/* Expiry Warnings */}
      {alerts?.expiry?.map((alert) => (
        <div key={alert.product_id} className="card border-yellow-200 bg-yellow-50">
          <div className="flex items-center gap-2">
            <span>⏰</span>
            <span className="font-semibold text-yellow-800">Expiring Soon: {alert.product_name}</span>
          </div>
          <p className="text-sm text-yellow-700 mt-1">
            Expires on {alert.expiry_date}. Consider using in promotions.
          </p>
        </div>
      ))}
      
      {/* Reorder Suggestions */}
      {alerts?.reorder?.map((suggestion) => (
        <div key={suggestion.product_id} className="card">
          <div className="flex justify-between items-center">
            <span>{suggestion.product_name}</span>
            <span className="text-sm text-gray-500">
              Suggested order: {suggestion.suggested_quantity} units
            </span>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Based on {suggestion.usage_trend_days}-day usage trend
          </p>
        </div>
      ))}
    </div>
  );
}
```

---

## 4. User Experience Considerations

### 4.1 Loading States

**Skeleton Components:**
```tsx
// apps/owner/src/components/AI/Skeletons.tsx

export function ChatMessageSkeleton() {
  return (
    <div className="animate-pulse space-y-2">
      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      <div className="h-4 bg-gray-200 rounded w-5/6"></div>
    </div>
  );
}

export function InsightCardSkeleton() {
  return (
    <div className="card animate-pulse">
      <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
      <div className="space-y-2">
        <div className="h-4 bg-gray-200 rounded w-full"></div>
        <div className="h-4 bg-gray-200 rounded w-2/3"></div>
      </div>
      <div className="h-8 bg-gray-200 rounded w-1/4 mt-4"></div>
    </div>
  );
}
```

**Streaming Indicator:**
```tsx
// apps/owner/src/components/AI/StreamingIndicator.tsx

export function StreamingIndicator() {
  return (
    <div className="flex items-center gap-2 text-gray-500">
      <div className="flex gap-1">
        <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
        <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
        <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
      </div>
      <span className="text-sm">AI is thinking...</span>
    </div>
  );
}
```

### 4.2 Error Handling

**Error Boundary for AI Components:**
```tsx
// apps/owner/src/components/AI/AIErrorBoundary.tsx

export class AIErrorBoundary extends React.Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="card border-red-200 bg-red-50">
          <h3 className="text-red-800 font-semibold">AI Service Unavailable</h3>
          <p className="text-red-600 text-sm mt-2">
            {this.state.error?.message || 'Unable to connect to AI service'}
          </p>
          <div className="mt-4 flex gap-2">
            <button
              onClick={() => this.setState({ hasError: false })}
              className="btn-sm btn-primary"
            >
              Try Again
            </button>
            <button
              onClick={() => window.location.reload()}
              className="btn-sm"
            >
              Refresh Page
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
```

**Retry Logic:**
```typescript
// apps/owner/src/utils/aiRetry.ts

export async function aiRequestWithRetry<T>(
  request: () => Promise<T>,
  maxRetries = 3,
  delay = 1000
): Promise<T> {
  let lastError: Error;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await request();
    } catch (error) {
      lastError = error;
      if (error.status === 429) { // Rate limited
        await new Promise(r => setTimeout(r, delay * (i + 1) * 2));
      } else if (error.status >= 500) { // Server error
        await new Promise(r => setTimeout(r, delay * (i + 1)));
      } else {
        throw error; // Client error, don't retry
      }
    }
  }
  
  throw lastError;
}
```

### 4.3 Confidence Indicators

**Confidence Badge Component:**
```tsx
// apps/owner/src/components/AI/ConfidenceBadge.tsx

interface Props {
  confidence: number;
  cached?: boolean;
}

export function ConfidenceBadge({ confidence, cached }: Props) {
  const getConfidenceColor = (conf: number) => {
    if (conf >= 0.9) return 'bg-green-100 text-green-800';
    if (conf >= 0.7) return 'bg-blue-100 text-blue-800';
    if (conf >= 0.5) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className="flex items-center gap-2 text-xs">
      <span className={`px-2 py-0.5 rounded-full ${getConfidenceColor(confidence)}`}>
        {Math.round(confidence * 100)}% confident
      </span>
      {cached && (
        <span className="text-gray-400" title="Response from cache">
          ⚡ Cached
        </span>
      )}
    </div>
  );
}
```

### 4.4 Human-in-the-Loop Workflows

**Approval Modal for AI Actions:**
```tsx
// apps/owner/src/components/AI/ApprovalModal.tsx

interface Props {
  action: AIAction;
  onApprove: () => void;
  onReject: () => void;
  onModify: (modifications: any) => void;
}

export function ApprovalModal({ action, onApprove, onReject, onModify }: Props) {
  const [modifications, setModifications] = useState({});

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl max-w-lg w-full mx-4 p-6">
        <h2 className="text-xl font-semibold">Review AI Action</h2>
        
        <div className="mt-4 space-y-4">
          {/* Action Summary */}
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">{action.description}</p>
            <div className="mt-2 text-sm">
              <strong>Impact:</strong> {action.impact}
            </div>
          </div>
          
          {/* Editable Fields */}
          {action.editable_fields?.map((field) => (
            <div key={field.name}>
              <label className="block text-sm font-medium mb-1">
                {field.label}
              </label>
              <input
                type={field.type}
                defaultValue={field.value}
                onChange={(e) => setModifications(prev => ({
                  ...prev,
                  [field.name]: e.target.value,
                }))}
                className="input"
              />
            </div>
          ))}
          
          {/* Confidence Warning */}
          {action.confidence < 0.7 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
              <p className="text-sm text-yellow-800">
                ⚠️ This action has lower confidence ({Math.round(action.confidence * 100)}%).
                Please review carefully before approving.
              </p>
            </div>
          )}
        </div>
        
        <div className="mt-6 flex justify-end gap-3">
          <button onClick={onReject} className="btn-secondary">
            Reject
          </button>
          <button
            onClick={() => onModify(modifications)}
            className="btn-secondary"
          >
            Modify & Approve
          </button>
          <button onClick={onApprove} className="btn-primary">
            Approve
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

## 5. Performance Optimization

### 5.1 Response Caching Strategy

**Multi-Layer Caching:**
```typescript
// apps/owner/src/services/cacheService.ts

export class AICacheService {
  private static instance: AICacheService;
  private memoryCache = new Map<string, { data: any; expiry: number }>();
  
  static getInstance() {
    if (!this.instance) {
      this.instance = new AICacheService();
    }
    return this.instance;
  }
  
  // Memory cache for instant access
  get<T>(key: string): T | null {
    const cached = this.memoryCache.get(key);
    if (cached && cached.expiry > Date.now()) {
      return cached.data as T;
    }
    this.memoryCache.delete(key);
    return null;
  }
  
  set(key: string, data: any, ttlMs: number) {
    this.memoryCache.set(key, {
      data,
      expiry: Date.now() + ttlMs,
    });
  }
  
  // Generate cache key for AI requests
  generateKey(request: AIRequest): string {
    return `ai:${request.agent_type}:${hashObject(request)}`;
  }
}

// React Query integration
export function useCachedAIQuery<T>(
  queryKey: string[],
  fetcher: () => Promise<T>,
  options: { staleTime?: number; cacheTime?: number } = {}
) {
  return useQuery({
    queryKey,
    queryFn: fetcher,
    staleTime: options.staleTime ?? 5 * 60 * 1000, // 5 minutes
    cacheTime: options.cacheTime ?? 30 * 60 * 1000, // 30 minutes
  });
}
```

### 5.2 Background Processing

**Web Worker for AI Tasks:**
```typescript
// apps/owner/src/workers/aiWorker.ts

self.onmessage = async (e) => {
  const { type, payload } = e.data;
  
  switch (type) {
    case 'ANALYZE_SCHEDULE':
      const result = await analyzeSchedule(payload);
      self.postMessage({ type: 'SCHEDULE_ANALYZED', result });
      break;
      
    case 'GENERATE_CAMPAIGN':
      const campaign = await generateCampaign(payload);
      self.postMessage({ type: 'CAMPAIGN_GENERATED', campaign });
      break;
  }
};

// Main thread usage
const worker = new Worker(new URL('./aiWorker.ts', import.meta.url));

worker.postMessage({
  type: 'ANALYZE_SCHEDULE',
  payload: { salonId, scheduleData },
});

worker.onmessage = (e) => {
  if (e.data.type === 'SCHEDULE_ANALYZED') {
    setAnalysisResult(e.data.result);
  worker.terminate();
  }
};
```

### 5.3 Progressive Loading

**Progressive Data Fetching:**
```tsx
// apps/owner/src/hooks/useProgressiveAI.ts

export function useProgressiveInsights(salonId: string) {
  const [insights, setInsights] = useState<Insights>({
    quick: null,    // Fast, cached insights
    detailed: null, // Full analysis
  });
  
  // Quick insights (cached, instant)
  const { data: quickInsights } = useQuery({
    queryKey: ['quick-insights', salonId],
    queryFn: () => fetchQuickInsights(salonId),
    staleTime: 0,
  });
  
  // Detailed insights (slower, comprehensive)
  const { data: detailedInsights } = useQuery({
    queryKey: ['detailed-insights', salonId],
    queryFn: () => fetchDetailedInsights(salonId),
    staleTime: 5 * 60 * 1000,
    enabled: !!quickInsights, // Wait for quick insights first
  });
  
  useEffect(() => {
    if (quickInsights) {
      setInsights(prev => ({ ...prev, quick: quickInsights }));
    }
  }, [quickInsights]);
  
  useEffect(() => {
    if (detailedInsights) {
      setInsights(prev => ({ ...prev, detailed: detailedInsights }));
    }
  }, [detailedInsights]);
  
  return insights;
}

// Usage in component
function Dashboard() {
  const { quick, detailed } = useProgressiveInsights(salonId);
  
  return (
    <div>
      {/* Show quick insights immediately */}
      {quick && <QuickInsightCards data={quick} />}
      
      {/* Show detailed insights when loaded */}
      {detailed ? (
        <DetailedInsightPanels data={detailed} />
      ) : (
        <DetailedInsightSkeletons />
      )}
    </div>
  );
}
```

---

## 6. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Implement SSE streaming endpoint in AI service
- [ ] Create AI chat service layer in frontend
- [ ] Build global AI assistant widget
- [ ] Add session management with Zustand

### Phase 2: Core Features (Week 3-4)
- [ ] Integrate Business Insights dashboard
- [ ] Build Marketing Campaign Generator
- [ ] Add Revenue Optimization panel
- [ ] Implement confidence indicators

### Phase 3: Advanced Features (Week 5-6)
- [ ] Staff Scheduling AI integration
- [ ] Inventory Intelligence alerts
- [ ] Customer Retention insights
- [ ] Human-in-the-loop workflows

### Phase 4: Optimization (Week 7-8)
- [ ] Multi-layer caching implementation
- [ ] Background processing with Web Workers
- [ ] Progressive loading patterns
- [ ] Performance monitoring

---

## 7. API Endpoints Summary

### Chat Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat` | Basic chat (non-streaming) |
| POST | `/api/v1/chat/stream` | SSE streaming chat |
| DELETE | `/api/v1/chat/session/{id}` | Clear session |

### Agent Endpoints (Key)
| Method | Endpoint | Agent |
|--------|----------|-------|
| POST | `/api/v1/agents/waitlist/process` | Waitlist Manager |
| POST | `/api/v1/agents/slot-optimizer/detect-gaps` | Slot Optimizer |
| POST | `/api/v1/agents/upsell/analyze` | Upsell Engine |
| POST | `/api/v1/agents/dynamic-pricing/peak-pricing` | Dynamic Pricing |
| POST | `/api/v1/agents/bundle-creator/bridal` | Bundle Creator |
| POST | `/api/v1/agents/inventory/monitor-stock` | Inventory Intelligence |
| POST | `/api/v1/agents/scheduling/weekly-schedule` | Staff Scheduling |
| POST | `/api/v1/agents/retention/at-risk-customers` | Customer Retention |

### Marketing Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/marketing/campaign` | Generate campaign |
| POST | `/api/v1/marketing/content` | Generate content |

### Analytics Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/analytics/insights` | Business insights |
| POST | `/api/v1/analytics/trends` | Trend analysis |

---

## 8. Security Considerations

1. **Authentication**: All AI endpoints require valid JWT token
2. **Rate Limiting**: 60 RPM / 1000 RPH per salon (enforced by backend)
3. **Data Isolation**: All requests include `salon_id` for multi-tenant isolation
4. **Input Validation**: All inputs validated via Pydantic schemas
5. **Output Sanitization**: AI responses filtered through guardrails

---

## 9. Monitoring & Observability

### Key Metrics to Track
- Response latency (p50, p95, p99)
- Cache hit rate
- Token usage per salon
- Error rate by agent type
- User satisfaction (thumbs up/down)

### Logging Strategy
```typescript
// Log AI interactions for analytics
logger.info('ai_interaction', {
  salon_id: salonId,
  agent_type: agentType,
  session_id: sessionId,
  response_time_ms: responseTime,
  cached: isCached,
  confidence: confidence,
  user_feedback: feedback,
});
```

---

*Document Version: 1.0*
*Last Updated: February 2026*
*Author: AI Architecture Team*
