# Enhanced Billing System with Price Override

## Overview

A comprehensive billing system that allows managers to modify service prices based on staff suggestions, with full audit trail and approval workflows.

---

## Feature Requirements

### 1. Price Override Capability
- Manager can modify any service price during billing
- Override reasons must be documented
- Discount thresholds require additional approval

### 2. Staff Suggestion Workflow
- Staff can suggest price modifications from their app
- Suggestions appear in real-time on manager's dashboard
- Manager can approve/reject with one click

### 3. Approval Workflow
- Discounts < 10%: Auto-approved (logged)
- Discounts 10-20%: Manager approval required
- Discounts > 20%: Owner approval required (if multi-level)

### 4. Audit Trail
- All price changes logged with:
  - Original price
  - New price
  - Reason code
  - Approved by
  - Timestamp
  - Staff suggestion reference

---

## User Interface Design

### Manager Billing Interface

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 💰 BILLING - Booking #BK-2026-0222-003                    Feb 22, 2026    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Customer: Priya Sharma (Platinum Member)                                  │
│  Stylist: Rahul Kumar                                                       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ SERVICES                                                              │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ Service                    │ Staff    │ Price    │ Override │ Actions│   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ Hair Cut + Styling         │ Rahul    │ ₹500     │ ₹500     │ [✏️]   │   │
│  │ Hair Color (Global)        │ Rahul    │ ₹2,500   │ ₹2,000   │ [✏️]   │   │
│  │   └─ 💡 Staff Suggestion: "Customer is regular, 20% discount"       │   │
│  │   └─ ✅ Approved by Manager @ 10:15 AM                               │   │
│  │ Deep Conditioning          │ Priya    │ ₹800     │ ₹800     │ [✏️]   │   │
│  │                                                                           │
│  │ [+ Add Service] [+ Add Custom Item]                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ PRICE ADJUSTMENTS                                                     │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ Subtotal:                                              ₹3,800        │   │
│  │ Membership Discount (10%):                              -₹380        │   │
│  │ Manual Adjustment:                                      -₹500        │   │
│  │   └─ Reason: Customer satisfaction (service delay)                    │   │
│  │ ─────────────────────────────────────────────────────────            │   │
│  │ GST (5%):                                                ₹146        │   │
│  │ ─────────────────────────────────────────────────────────            │   │
│  │ TOTAL:                                                 ₹3,066        │   │
│  │                                                         ──────        │   │
│  │ Amount Paid:                                           ₹3,066        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 💡 PENDING STAFF SUGGESTIONS (2)                          [View All] │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ • Priya suggests 15% off for Meena (loyalty)     [Approve] [Reject] │   │
│  │ • Rahul suggests complimentary hair spa for Amit  [Approve] [Reject] │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  [Save Draft] [Request Approval] [Generate Invoice] [Send to WhatsApp]     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Price Override Modal

```
┌─────────────────────────────────────────────────────────────────┐
│ ✏️ Override Price - Hair Color (Global)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Original Price:     ₹2,500                                     │
│  Current Override:   ₹2,000 (20% off)                           │
│                                                                 │
│  New Price:          [₹________]                                │
│                                                                 │
│  Discount %:         [____%]   Auto-calculated                  │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│  Override Reason:                                               │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ○ Customer Loyalty                                          ││
│  │ ○ Service Recovery (Issue)                                  ││
│  │ ○ Promotional Offer                                         ││
│  │ ○ Staff Suggestion                                          ││
│  │ ○ Price Match Competitor                                    ││
│  │ ○ Custom Reason: [________________________]                 ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  📝 Notes:                                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Customer is a 3-year platinum member, requested discount   ││
│  │ due to slight delay in service                             ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ⚠️ Discount exceeds 15% - Additional approval may be required  │
│                                                                 │
│  [Cancel]                              [Apply Override]          │
└─────────────────────────────────────────────────────────────────┘
```

### Staff Suggestion Panel (Real-time)

```
┌─────────────────────────────────────────────────────────────────┐
│ 💡 Staff Suggestions                            🔴 2 Pending     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 🧑‍💼 Priya Kumar | 10:45 AM                                │  │
│  │ Booking: BK-2026-0222-015 | Customer: Meena Sharma       │  │
│  │ Service: Bridal Package                                   │  │
│  │ Suggestion: 15% discount                                  │  │
│  │ Reason: "Customer is 5-year loyal, referring 2 friends"   │  │
│  │ Impact: ₹4,500 → ₹3,825 (Save ₹675)                       │  │
│  │                                                           │  │
│  │ [✅ Approve] [❌ Reject] [💬 Chat]                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 🧑‍💼 Rahul Kumar | 11:02 AM                                │  │
│  │ Booking: BK-2026-0222-018 | Customer: Amit Patel         │  │
│  │ Suggestion: Add complimentary Hair Spa                    │  │
│  │ Reason: "First-time customer, give premium experience"    │  │
│  │ Impact: +₹0 (Complimentary, value ₹1,200)                 │  │
│  │                                                           │  │
│  │ [✅ Approve] [❌ Reject] [💬 Chat]                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  [View History] [Settings]                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Database Schema

### Price Override Log
```typescript
interface PriceOverrideLog {
  id: string;
  salon_id: string;
  booking_id: string;
  service_id: string;
  service_name: string;
  original_price: number;
  new_price: number;
  discount_percent: number;
  reason_code: 'loyalty' | 'service_recovery' | 'promotion' | 'staff_suggestion' | 'price_match' | 'custom';
  reason_text: string;
  suggested_by?: string;  // staff_id if staff suggested
  approved_by: string;    // manager_id
  approved_at: Date;
  created_at: Date;
}
```

### Staff Suggestion
```typescript
interface StaffSuggestion {
  id: string;
  salon_id: string;
  booking_id: string;
  staff_id: string;
  staff_name: string;
  suggestion_type: 'discount' | 'complimentary' | 'upgrade' | 'custom';
  service_id?: string;
  service_name?: string;
  original_price: number;
  suggested_price: number;
  discount_percent: number;
  reason: string;
  status: 'pending' | 'approved' | 'rejected' | 'expired';
  reviewed_by?: string;
  reviewed_at?: Date;
  rejection_reason?: string;
  created_at: Date;
  expires_at: Date;  // Auto-expire after 30 mins
}
```

---

## API Endpoints

### Price Override
```
POST   /api/v1/billing/override          # Create price override
GET    /api/v1/billing/overrides         # List overrides (with filters)
GET    /api/v1/billing/overrides/{id}    # Get override details
DELETE /api/v1/billing/overrides/{id}    # Remove override
```

### Staff Suggestions
```
POST   /api/v1/billing/suggestions              # Staff creates suggestion
GET    /api/v1/billing/suggestions              # List suggestions (manager)
POST   /api/v1/billing/suggestions/{id}/approve # Approve suggestion
POST   /api/v1/billing/suggestions/{id}/reject  # Reject suggestion
GET    /api/v1/billing/suggestions/pending     # Get pending count
```

### Billing
```
POST   /api/v1/billing/generate         # Generate final bill
GET    /api/v1/billing/{id}/invoice     # Get invoice PDF
POST   /api/v1/billing/{id}/whatsapp    # Send invoice via WhatsApp
```

---

## Approval Rules Configuration

```typescript
interface ApprovalRules {
  salon_id: string;
  auto_approve_threshold: number;     // e.g., 10% auto-approve
  manager_approval_threshold: number; // e.g., 20% needs manager
  owner_approval_threshold: number;   // e.g., >20% needs owner
  max_discount_per_day: number;       // e.g., ₹10,000 max per day
  require_reason_for_discount: boolean;
  allow_staff_suggestions: boolean;
  suggestion_expiry_minutes: number;  // e.g., 30 mins
}
```

---

## Real-Time Events (WebSocket)

```typescript
// Events sent to Manager Dashboard
interface BillingEvents {
  'suggestion:new': StaffSuggestion;
  'suggestion:approved': { id: string; by: string };
  'suggestion:rejected': { id: string; by: string; reason: string };
  'override:created': PriceOverrideLog;
  'bill:generated': { booking_id: string; amount: number };
}
```

---

## Implementation Priority

1. **Phase 1**: Core price override with audit log
2. **Phase 2**: Staff suggestion workflow
3. **Phase 3**: Real-time notifications
4. **Phase 4**: Approval rules engine
5. **Phase 5**: Analytics and reporting

