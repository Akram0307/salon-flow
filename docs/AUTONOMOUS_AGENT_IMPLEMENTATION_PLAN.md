# Salon Flow: Autonomous AI Agent Implementation Plan
## Comprehensive Task List for User Approval

---

## Executive Summary

Based on consultations with Salon Business Domain Expert, AI/ML Engineer, and Backend Architect, this plan outlines the implementation of autonomous AI agents to maximize salon profitability.

**Primary Goal**: Reduce idle time and maximize profitable bookings through autonomous AI agents.

**Projected Impact**: 
- 20-30% revenue increase per stylist within 6 months
- ₹4.8L-8.2L additional revenue per stylist annually from gap filling
- 40% reduction in no-shows

---

## Phase 1: Foundation Infrastructure (Weeks 1-2)

### 1.1 Firestore Schema Extensions
**Priority: Critical | Effort: 2 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 1.1.1 | Create `autonomous_decisions` collection | Schema + indexes |
| 1.1.2 | Create `agent_states` collection for circuit breaker | Schema + state machine |
| 1.1.3 | Create `approvals` collection for human-in-the-loop | Schema + workflow |
| 1.1.4 | Create `audit_logs` collection for compliance | Schema + retention policy |
| 1.1.5 | Create `customer_scores` collection for LTV/churn | Schema + scoring fields |
| 1.1.6 | Create `gaps` collection for schedule gap tracking | Schema + priority fields |
| 1.1.7 | Create `outreach` collection for communication tracking | Schema + status fields |

### 1.2 Backend API Infrastructure
**Priority: Critical | Effort: 3 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 1.2.1 | Create autonomous router (`/api/v1/autonomous/*`) | FastAPI router |
| 1.2.2 | Implement decision CRUD endpoints | 5 endpoints |
| 1.2.3 | Implement agent state management endpoints | 4 endpoints |
| 1.2.4 | Implement approval workflow endpoints | 3 endpoints |
| 1.2.5 | Implement gap management endpoints | 3 endpoints |
| 1.2.6 | Implement outreach tracking endpoints | 3 endpoints |
| 1.2.7 | Create webhook endpoints for Twilio callbacks | 3 endpoints |

### 1.3 Event Bus & Orchestration
**Priority: High | Effort: 2 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 1.3.1 | Set up GCP Pub/Sub topics for agent events | 5 topics |
| 1.3.2 | Implement EventPublisher service | Python class |
| 1.3.3 | Create AgentMessage protocol | Pydantic model |
| 1.3.4 | Implement Redis-based distributed locking | Lock service |
| 1.3.5 | Create agent coordinator service | Python class |

---

## Phase 2: Smart Fill Agent Core (Weeks 3-4)

### 2.1 Smart Fill Agent Implementation
**Priority: Critical | Effort: 4 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 2.1.1 | Create SmartFillAgent class extending BaseAgent | Python class |
| 2.1.2 | Implement `scan_for_gaps()` method | Gap detection logic |
| 2.1.3 | Implement `predict_no_show()` method | Prediction model |
| 2.1.4 | Implement `calculate_profit_score()` method | Scoring algorithm |
| 2.1.5 | Implement `execute_autonomous_fill()` method | Fill workflow |
| 2.1.6 | Implement candidate ranking algorithm | Priority queue |
| 2.1.7 | Implement discount governance (tiered caps) | Discount service |

### 2.2 No-Show Prediction Model
**Priority: High | Effort: 3 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 2.2.1 | Implement weighted prediction formula | Python function |
| 2.2.2 | Create feature extraction pipeline | Feature service |
| 2.2.3 | Implement customer history scoring | History analyzer |
| 2.2.4 | Add weather API integration for risk factor | External API |
| 2.2.5 | Implement lead time risk calculation | Time analyzer |
| 2.2.6 | Create prediction confidence thresholds | Config + logic |

### 2.3 Profit Scoring Algorithm
**Priority: High | Effort: 2 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 2.2.1 | Implement profit score formula | Python function |
| 2.2.2 | Create LTV calculation service | LTV service |
| 2.2.3 | Implement loyalty bonus scoring | Loyalty service |
| 2.2.4 | Add urgency factor calculation | Urgency service |
| 2.2.5 | Normalize scores to 0-100 scale | Normalization |

---

## Phase 3: Autonomous Operations (Weeks 5-6)

### 3.1 WhatsApp/Twilio Integration
**Priority: Critical | Effort: 3 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 3.1.1 | Create WhatsAppIntegration class | Python class |
| 3.1.2 | Implement `send_gap_fill_offer()` method | Message sender |
| 3.1.3 | Implement `send_no_show_prevention()` method | Reminder sender |
| 3.1.4 | Create message templates for offers | Template library |
| 3.1.5 | Implement one-tap booking link generation | Deep links |
| 3.1.6 | Handle incoming WhatsApp responses | Webhook handler |
| 3.1.7 | Implement response deadline escalation | Timeout logic |

### 3.2 Firestore Real-time Listeners
**Priority: High | Effort: 2 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 3.2.1 | Create FirestoreListener class | Python class |
| 3.2.2 | Implement booking change listener | on_snapshot handler |
| 3.2.3 | Implement schedule change listener | on_snapshot handler |
| 3.2.4 | Connect listeners to agent triggers | Event emission |

### 3.3 Background Task Scheduler
**Priority: Critical | Effort: 3 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 3.3.1 | Set up Cloud Tasks queues | 4 queues |
| 3.3.2 | Create task scheduler service | Python class |
| 3.3.3 | Implement gap scan job (5-minute interval) | Scheduled task |
| 3.3.4 | Implement no-show check job (15-minute interval) | Scheduled task |
| 3.3.5 | Implement waitlist escalation job (1-minute interval) | Scheduled task |
| 3.3.6 | Implement cleanup job (hourly) | Scheduled task |
| 3.3.7 | Add error handling with exponential backoff | Retry logic |

---

## Phase 4: Safety & Governance (Weeks 7-8)

### 4.1 Circuit Breaker Implementation
**Priority: Critical | Effort: 2 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 4.1.1 | Create CircuitBreaker class | Python class |
| 4.1.2 | Implement error threshold monitoring | Counter service |
| 4.1.3 | Implement cooldown mechanism | Timer service |
| 4.1.4 | Add half-open state for recovery | State machine |
| 4.1.5 | Create circuit breaker reset endpoint | API endpoint |

### 4.2 Rate Limiting
**Priority: High | Effort: 1 day**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 4.2.1 | Implement hourly action limits (20/hour) | Rate limiter |
| 4.2.2 | Implement daily action limits (100/day) | Rate limiter |
| 4.2.3 | Implement per-customer limits (3/day) | Rate limiter |
| 4.2.4 | Create rate limit alert system | Alert service |

### 4.3 Approval Workflow
**Priority: High | Effort: 2 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 4.3.1 | Create approval request service | Python class |
| 4.3.2 | Implement approval expiration (15-min timeout) | Timeout handler |
| 4.3.3 | Create approval notification to owner | Push/SMS |
| 4.3.4 | Implement approve/reject actions | API endpoints |
| 4.3.5 | Add escalation for expired approvals | Escalation logic |

### 4.4 Audit & Compliance
**Priority: High | Effort: 2 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 4.4.1 | Implement comprehensive audit logging | Logger service |
| 4.4.2 | Create decision explanation generator | Explainability |
| 4.4.3 | Implement data retention policy (90 days) | Cleanup job |
| 4.4.4 | Create compliance report generator | Report service |
| 4.4.5 | Add opt-out management for customers | Preference center |

---

## Phase 5: Owner PWA Integration (Weeks 9-10)

### 5.1 Autonomous Dashboard
**Priority: High | Effort: 3 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 5.1.1 | Create Autonomous Dashboard page | React component |
| 5.1.2 | Implement real-time gap visualization | Chart component |
| 5.1.3 | Create agent status cards | Status cards |
| 5.1.4 | Implement KPI metrics display | Metrics cards |
| 5.1.5 | Add revenue impact tracker | Revenue chart |

### 5.2 Approval Management UI
**Priority: High | Effort: 2 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 5.2.1 | Create Approval Queue component | React component |
| 5.2.2 | Implement approve/reject actions | Action buttons |
| 5.2.3 | Add approval detail modal | Modal component |
| 5.2.4 | Create approval history view | History list |

### 5.3 Agent Configuration UI
**Priority: Medium | Effort: 2 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 5.3.1 | Create Agent Settings page | React component |
| 5.3.2 | Implement autonomy level toggles | Toggle switches |
| 5.3.3 | Add discount cap configuration | Input fields |
| 5.3.4 | Create schedule configuration | Time pickers |
| 5.3.5 | Add circuit breaker reset button | Action button |

---

## Phase 6: Enhanced Agents (Weeks 11-12)

### 6.1 Waitlist Manager Enhancement
**Priority: High | Effort: 2 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 6.1.1 | Enhance WaitlistManager with autonomous ops | Class update |
| 6.1.2 | Implement priority queue ranking | Queue service |
| 6.1.3 | Add automatic slot assignment | Assignment logic |
| 6.1.4 | Implement 10-minute response window | Timeout handler |

### 6.2 Dynamic Pricing Agent
**Priority: Medium | Effort: 3 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 6.2.1 | Create DynamicPricingAgent class | Python class |
| 6.2.2 | Implement demand analysis | Analysis service |
| 6.2.3 | Create pricing adjustment logic (±10% auto) | Pricing engine |
| 6.2.4 | Add supervised pricing for >10% changes | Approval workflow |
| 6.2.5 | Implement peak/off-peak detection | Detection logic |

### 6.3 Customer Retention Agent Enhancement
**Priority: Medium | Effort: 2 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 6.3.1 | Enhance RetentionAgent with churn prediction | Class update |
| 6.3.2 | Implement at-risk detection (70% threshold) | Detection logic |
| 6.3.3 | Create win-back campaign generator | Campaign service |
| 6.3.4 | Add loyalty reward automation | Reward service |

### 6.4 Upsell Engine Enhancement
**Priority: Medium | Effort: 2 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 6.4.1 | Enhance UpsellEngine with autonomous suggestions | Class update |
| 6.4.2 | Implement opportunity detection | Detection logic |
| 6.4.3 | Create bundle recommendation engine | Bundle service |
| 6.4.4 | Add upsell tracking and conversion metrics | Analytics |

---

## Phase 7: Testing & Deployment (Weeks 13-14)

### 7.1 Unit & Integration Tests
**Priority: Critical | Effort: 3 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 7.1.1 | Write SmartFillAgent unit tests | Test file |
| 7.1.2 | Write prediction model tests | Test file |
| 7.1.3 | Write API endpoint tests | Test file |
| 7.1.4 | Write integration tests for workflows | Test file |
| 7.1.5 | Write circuit breaker tests | Test file |

### 7.2 End-to-End Testing
**Priority: High | Effort: 2 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 7.2.1 | Create E2E test for gap fill workflow | Playwright test |
| 7.2.2 | Create E2E test for approval workflow | Playwright test |
| 7.2.3 | Create E2E test for WhatsApp integration | Playwright test |
| 7.2.4 | Test circuit breaker scenarios | Manual test |

### 7.3 Deployment
**Priority: Critical | Effort: 2 days**

| Task ID | Task Description | Deliverable |
|---------|-----------------|------------|
| 7.3.1 | Deploy Firestore schema updates | Schema migration |
| 7.3.2 | Deploy backend API changes | Cloud Run update |
| 7.3.3 | Deploy AI service changes | Cloud Run update |
| 7.3.4 | Deploy Owner PWA changes | Cloud Run update |
| 7.3.5 | Configure Cloud Scheduler jobs | Scheduler setup |
| 7.3.6 | Set up monitoring alerts | Cloud Monitoring |

---

## Summary: Task Counts by Phase

| Phase | Duration | Tasks | Priority Distribution |
|-------|----------|-------|----------------------|
| 1. Foundation | 2 weeks | 17 tasks | 12 Critical, 5 High |
| 2. Smart Fill Core | 2 weeks | 14 tasks | 7 Critical, 7 High |
| 3. Autonomous Ops | 2 weeks | 14 tasks | 7 Critical, 7 High |
| 4. Safety & Governance | 2 weeks | 14 tasks | 3 Critical, 11 High |
| 5. Owner PWA | 2 weeks | 13 tasks | 7 High, 6 Medium |
| 6. Enhanced Agents | 2 weeks | 12 tasks | 4 High, 8 Medium |
| 7. Testing & Deploy | 2 weeks | 13 tasks | 5 Critical, 5 High |
| **TOTAL** | **14 weeks** | **97 tasks** | **27 Critical, 35 High, 35 Medium** |

---

## Autonomy Level Definitions

| Level | Discount Cap | Actions | Human Involvement |
|-------|-------------|---------|-------------------|
| **FULL_AUTO** | ≤20% | Gap fills, waitlist, reminders, confirmations | None - logged only |
| **SUPERVISED** | 20-35% | High-value offers, dynamic pricing >10%, win-back >₹500 | Approval required |
| **MANUAL_ONLY** | N/A | Refunds, complaints, terminations, pricing strategy | Human decision |

---

## Key Performance Indicators

| KPI | Current Baseline | 3-Month Target | 6-Month Target |
|-----|------------------|----------------|----------------|
| Gap Fill Rate | 35% | 60% | 73% |
| No-Show Rate | 18% | 12% | 8% |
| Revenue per Stylist | ₹4.2L/month | ₹4.8L/month | ₹5.4L/month |
| Staff Utilization | 62% | 72% | 80% |
| Customer Retention | 72% | 77% | 82% |
| Average Ticket Value | ₹650 | ₹720 | ₹800 |

---

## Risk Mitigation Summary

| Risk | Mitigation |
|------|------------|
| Over-discounting | Hard cap at 20% autonomous, approval required above |
| Double-booking | Distributed locking, idempotent operations |
| Over-messaging | Frequency caps: 3/day, 10/week per customer |
| System failure | Circuit breaker, graceful degradation to manual mode |
| Compliance | Audit trail, opt-out management, 90-day retention |

---

## Approval Request

Please review and approve the following:

1. **Implementation Phases** - 7 phases over 14 weeks
2. **Task List** - 97 detailed tasks
3. **Autonomy Levels** - FULL_AUTO, SUPERVISED, MANUAL_ONLY framework
4. **KPI Targets** - Gap fill 73%, No-show reduction to 8%
5. **Risk Mitigations** - Circuit breaker, rate limits, approval workflows

**Questions for User Decision:**

- [ ] Should we start with Phase 1 immediately?
- [ ] Any adjustments to autonomy thresholds (discount caps)?
- [ ] Priority changes for specific agents?
- [ ] Budget/timeline constraints?

---

*Plan synthesized from expert consultations*
*Date: February 22, 2026*
