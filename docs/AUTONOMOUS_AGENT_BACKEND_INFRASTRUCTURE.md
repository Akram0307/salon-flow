# Autonomous Agent Backend Infrastructure

## Overview

This document describes the complete backend infrastructure for autonomous AI agents in Salon Flow, enabling intelligent automation of salon operations including gap filling, no-show prevention, waitlist management, and customer retention.

## Architecture Components

### 1. Firestore Schema Extensions

#### Collections Structure

```
salons/{salon_id}/
├── autonomous_decisions/{decision_id}
├── agent_states/{agent_name}
├── approvals/{approval_id}
├── audit_logs/{log_id}
├── customer_scores/{customer_id}
├── gaps/{gap_id}
└── outreach/{outreach_id}
```

#### autonomous_decisions Collection

```python
{
    "id": "dec_xxx",
    "salon_id": "salon_123",
    "agent_name": "gap_fill_agent",
    "decision_type": "gap_fill",  # gap_fill, no_show_prevention, waitlist_promotion, discount_offer, dynamic_pricing
    "autonomy_level": "supervised",  # full_auto, supervised, manual_only
    "context": {
        "trigger_id": "gap_xxx",
        "trigger_type": "schedule_gap",
        "customer_id": "cust_xxx",
        "staff_id": "staff_xxx",
        "service_id": "svc_xxx",
        "time_slot": "2024-01-15T14:00:00Z"
    },
    "action_taken": "outreach_initiated",
    "action_details": {
        "gap_duration_minutes": 60,
        "potential_revenue": 500,
        "customer_segment": "vip"
    },
    "revenue_impact": {
        "potential": 500,
        "actual": 0,
        "currency": "INR"
    },
    "approval": {
        "required": true,
        "status": "pending",  # pending, approved, rejected, expired, not_required
        "approval_id": "apr_xxx",
        "approved_by": null,
        "approved_at": null
    },
    "outcome": {
        "status": "pending",  # pending, success, failed, expired, rejected
        "result": null,
        "completed_at": null,
        "booking_created_id": null
    },
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z",
    "expires_at": "2024-01-15T10:15:00Z"
}
```

#### agent_states Collection

```python
{
    "id": "state_salon_123_gap_fill_agent",
    "salon_id": "salon_123",
    "agent_name": "gap_fill_agent",
    "status": "active",  # active, paused, error, circuit_breaker
    "last_execution": "2024-01-15T10:00:00Z",
    "next_scheduled": "2024-01-15T10:05:00Z",
    "circuit_breaker": {
        "state": "closed",  # closed, open, half_open
        "error_count": 0,
        "last_error": null,
        "last_error_time": null,
        "cooldown_until": null,
        "auto_recovery": true
    },
    "config": {
        "max_hourly_actions": 20,
        "max_daily_actions": 100,
        "cooldown_minutes": 5,
        "custom": {}
    },
    "counters": {
        "date": "2024-01-15",
        "actions_taken": 15,
        "actions_successful": 14,
        "actions_failed": 1,
        "revenue_generated": 3500,
        "by_type": {
            "gap_fill": {"count": 10, "revenue": 2500},
            "no_show_prevention": {"count": 5, "revenue": 1000}
        }
    },
    "rate_limits": {
        "hourly_actions": {"limit": 20, "current": 15, "remaining": 5},
        "daily_actions": {"limit": 100, "current": 45, "remaining": 55}
    },
    "health": {
        "last_heartbeat": "2024-01-15T10:00:00Z",
        "consecutive_failures": 0,
        "average_response_time_ms": 150,
        "success_rate_24h": 0.95
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
}
```

#### approvals Collection

```python
{
    "id": "apr_xxx",
    "salon_id": "salon_123",
    "decision_id": "dec_xxx",
    "agent_name": "gap_fill_agent",
    "action_type": "gap_fill",
    "action_summary": "Fill 60-min gap with VIP customer Priya",
    "action_details": {
        "gap_id": "gap_xxx",
        "customer_id": "cust_xxx",
        "customer_name": "Priya Sharma",
        "staff_name": "Rahul",
        "time_slot": "2:00 PM - 3:00 PM",
        "potential_revenue": 500
    },
    "priority": "medium",  # low, medium, high, urgent
    "status": "pending",  # pending, approved, rejected, expired, cancelled
    "expires_at": "2024-01-15T10:15:00Z",
    "notifications_sent": {
        "whatsapp": true,
        "push": true,
        "email": false
    },
    "response": {
        "action": null,
        "responded_by": null,
        "responded_at": null,
        "notes": null
    },
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
}
```

#### audit_logs Collection

```python
{
    "id": "log_xxx",
    "salon_id": "salon_123",
    "event_type": "decision_made",  # decision_made, approval_requested, approval_granted, approval_rejected, config_changed, manual_override, external_call
    "severity": "info",  # debug, info, warning, error, critical
    "actor": "gap_fill_agent",  # agent name or user ID
    "action": "Decision: gap_fill",
    "resource_type": "decision",
    "resource_id": "dec_xxx",
    "details": {
        "decision_type": "gap_fill",
        "autonomy_level": "supervised",
        "action_taken": "outreach_initiated"
    },
    "ip_address": null,
    "user_agent": null,
    "created_at": "2024-01-15T10:00:00Z"
}
```

#### customer_scores Collection

```python
{
    "id": "score_cust_xxx",
    "salon_id": "salon_123",
    "customer_id": "cust_xxx",
    "segment": "vip",  # vip, high_value, regular, new, at_risk
    "ltv": {
        "total": 25000,
        "last_12_months": 8000,
        "projected_annual": 10000,
        "average_per_visit": 500
    },
    "visit_frequency": {
        "total_visits": 50,
        "last_90_days": 8,
        "average_days_between": 11,
        "last_visit": "2024-01-10",
        "next_predicted": "2024-01-21"
    },
    "churn_risk": {
        "score": 25,  # 0-100, higher = more risk
        "factors": ["decreasing_frequency"],
        "last_assessment": "2024-01-15"
    },
    "preferences": {
        "preferred_staff": ["staff_xxx"],
        "preferred_services": ["svc_xxx"],
        "preferred_time_slots": ["morning", "weekend"]
    },
    "engagement": {
        "whatsapp_opt_in": true,
        "response_rate": 0.8,
        "last_response": "2024-01-14"
    },
    "scores": {
        "retention": 75,
        "upsell": 60,
        "referral": 40
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
}
```

#### gaps Collection

```python
{
    "id": "gap_xxx",
    "salon_id": "salon_123",
    "staff_id": "staff_xxx",
    "staff_name": "Rahul Kumar",
    "date": "2024-01-15",
    "start_time": "2024-01-15T14:00:00Z",
    "end_time": "2024-01-15T15:00:00Z",
    "duration_minutes": 60,
    "priority": "high",  # low, medium, high, critical
    "status": "open",  # open, filled, expired, ignored
    "potential_revenue": 500,
    "services_fittable": ["svc_xxx", "svc_yyy"],
    "fill_attempts": 2,
    "last_attempt_at": "2024-01-15T10:00:00Z",
    "filled_by": null,
    "created_at": "2024-01-15T08:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
}
```

#### outreach Collection

```python
{
    "id": "out_xxx",
    "salon_id": "salon_123",
    "customer_id": "cust_xxx",
    "customer_name": "Priya Sharma",
    "customer_phone": "+919876543210",
    "outreach_type": "gap_fill",  # gap_fill, no_show_prevention, waitlist_promotion, discount_offer, retention, rebooking
    "channel": "whatsapp",  # whatsapp, sms, push, email
    "status": "pending",  # pending, sent, delivered, read, responded, failed, expired
    "message": "Hi Priya! We have a slot available today at 2 PM with Rahul...",
    "trigger_id": "gap_xxx",
    "trigger_type": "gap",
    "offer_details": {
        "discount_percent": 10,
        "valid_until": "2024-01-15T15:00:00Z"
    },
    "expires_at": "2024-01-15T14:15:00Z",
    "attempts": 1,
    "last_attempt_at": "2024-01-15T10:00:00Z",
    "response": {
        "received": false,
        "action": null,
        "responded_at": null,
        "booking_id": null
    },
    "delivery": {
        "message_id": null,
        "sent_at": null,
        "delivered_at": null,
        "read_at": null,
        "error": null
    },
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
}
```

---

### 2. API Endpoints Design

#### Autonomous Agent Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/autonomous/decisions` | Create decision record |
| GET | `/autonomous/decisions` | List decisions with filters |
| GET | `/autonomous/decisions/{id}` | Get decision details |
| PATCH | `/autonomous/decisions/{id}` | Update decision outcome |
| GET | `/autonomous/decisions/stats/daily` | Daily decision statistics |

#### Agent State Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/autonomous/agents` | List all agents |
| GET | `/autonomous/agents/{name}` | Get agent state |
| PATCH | `/autonomous/agents/{name}` | Update agent status |
| PUT | `/autonomous/agents/{name}/config` | Update agent config |
| POST | `/autonomous/agents/{name}/reset-circuit-breaker` | Reset circuit breaker |

#### Approval Workflow Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/autonomous/approvals` | List approvals |
| GET | `/autonomous/approvals/pending` | Get pending approvals |
| GET | `/autonomous/approvals/{id}` | Get approval details |
| POST | `/autonomous/approvals/{id}/action` | Approve/reject request |
| GET | `/autonomous/approvals/stats/summary` | Approval statistics |

#### Gap Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/autonomous/gaps` | List gaps |
| GET | `/autonomous/gaps/open` | Get open gaps |
| GET | `/autonomous/gaps/high-priority` | Get high priority gaps |
| GET | `/autonomous/gaps/{id}` | Get gap details |
| GET | `/autonomous/gaps/stats/daily` | Gap statistics |

#### Outreach Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/autonomous/outreach` | Create outreach |
| GET | `/autonomous/outreach` | List outreach |
| GET | `/autonomous/outreach/{id}` | Get outreach details |
| PATCH | `/autonomous/outreach/{id}` | Update outreach status |
| GET | `/autonomous/outreach/stats/summary` | Outreach statistics |

#### Analytics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/autonomous/analytics/dashboard` | Dashboard data |
| GET | `/autonomous/analytics/revenue-impact` | Revenue impact analysis |

---

### 3. Background Task Infrastructure

#### Cloud Tasks Queues

```yaml
queues:
  - name: autonomous-agents
    rate_limits:
      max_concurrent_dispatches: 10
      max_dispatches_per_second: 5
    retry_config:
      max_attempts: 3
      min_backoff: 10s
      max_backoff: 300s
      
  - name: notifications
    rate_limits:
      max_concurrent_dispatches: 20
      max_dispatches_per_second: 10
    retry_config:
      max_attempts: 3
      
  - name: analytics
    rate_limits:
      max_concurrent_dispatches: 5
      max_dispatches_per_second: 2
    
  - name: cleanup
    rate_limits:
      max_concurrent_dispatches: 3
      max_dispatches_per_second: 1
```

#### Task Types

| Queue | Task Type | Handler | Schedule |
|-------|-----------|---------|----------|
| autonomous-agents | gap_fill | /internal/tasks/execute | Every 5 min |
| autonomous-agents | no_show_prevention | /internal/tasks/execute | Every 10 min |
| autonomous-agents | waitlist_promotion | /internal/tasks/execute | Every 5 min |
| autonomous-agents | retention_check | /internal/tasks/execute | Hourly |
| notifications | send_whatsapp | /internal/tasks/send-notification | On-demand |
| analytics | aggregate_daily | /internal/tasks/analytics | Daily 00:00 |
| cleanup | expired_approvals | /internal/tasks/cleanup | Hourly |
| cleanup | expired_outreach | /internal/tasks/cleanup | Hourly |

#### Agent Scheduler Configuration

```python
AGENT_INTERVALS = {
    "gap_fill_agent": 5,        # Every 5 minutes
    "no_show_prevention_agent": 10,  # Every 10 minutes
    "waitlist_agent": 5,       # Every 5 minutes
    "retention_agent": 60,     # Hourly
    "upsell_agent": 30,        # Every 30 minutes
    "analytics_agent": 60,     # Hourly
    "cleanup_agent": 60,       # Hourly
}
```

---

### 4. Security & Governance

#### Rate Limiting Configuration

```python
DEFAULT_RATE_LIMITS = {
    "hourly_actions": 20,
    "daily_actions": 100,
    "per_customer_hourly": 1,  # Max 1 outreach per customer per hour
    "per_customer_daily": 3,   # Max 3 outreach per customer per day
}
```

#### Circuit Breaker Configuration

```python
CIRCUIT_BREAKER_CONFIG = {
    "error_threshold": 5,      # Open after 5 consecutive errors
    "cooldown_minutes": 5,     # Wait 5 min before half-open
    "half_open_attempts": 1,   # Try 1 request in half-open state
    "auto_recovery": True,     # Auto-recover from open state
}
```

#### Approval Workflow Rules

| Decision Type | Autonomy Level | Approval Required |
|---------------|----------------|-------------------|
| gap_fill | full_auto | No |
| gap_fill | supervised | Yes |
| no_show_prevention | full_auto | No |
| discount_offer | supervised | Yes |
| discount_offer > 20% | manual_only | Yes |
| dynamic_pricing | supervised | Yes |

#### Multi-Tenant Isolation

- All queries filtered by `salon_id`
- Firestore security rules enforce tenant isolation
- Agent state tracked per salon
- Rate limits applied per salon

---

### 5. Integration Architecture

#### Pub/Sub Events

```python
# Event types published to 'salon-events' topic
EVENT_TYPES = [
    "AUTONOMOUS_DECISION",
    "GAP_DETECTED",
    "GAP_FILLED",
    "GAP_EXPIRED",
    "OUTREACH_SENT",
    "OUTREACH_DELIVERED",
    "OUTREACH_RESPONDED",
    "APPROVAL_REQUESTED",
    "APPROVAL_APPROVED",
    "APPROVAL_REJECTED",
    "APPROVAL_EXPIRED",
]
```

#### Webhook Endpoints

| Endpoint | Service | Purpose |
|----------|---------|---------|
| POST /webhooks/twilio/status | Twilio | Message delivery status |
| POST /webhooks/twilio/incoming | Twilio | Incoming WhatsApp/SMS |
| POST /webhooks/twilio/voice | Twilio | Voice call callbacks |

#### Real-time Updates

- Firestore listeners for approval status changes
- Pub/Sub to WebSocket bridge for dashboard updates
- Push notifications for urgent approvals

---

## File Structure

```
services/api/app/
├── models/autonomous/
│   ├── __init__.py
│   ├── decision.py          # AutonomousDecisionModel
│   ├── agent_state.py       # AgentStateModel
│   ├── approval.py          # ApprovalModel
│   ├── audit.py             # AuditLogModel
│   ├── customer_score.py    # CustomerScoreModel
│   ├── gap.py               # GapModel
│   └── outreach.py          # OutreachModel
│
├── schemas/autonomous/
│   ├── __init__.py
│   ├── decision.py          # DecisionCreate, DecisionResponse
│   ├── agent_state.py       # AgentStateResponse, AgentConfigUpdate
│   ├── approval.py          # ApprovalRequestCreate, ApprovalAction
│   ├── gap.py               # GapCreate, GapResponse
│   └── outreach.py          # OutreachCreate, OutreachResponse
│
├── services/autonomous/
│   ├── __init__.py
│   ├── event_publisher.py   # Pub/Sub event publishing
│   ├── gap_fill_service.py  # Gap fill orchestration
│   ├── outreach_service.py  # Outreach coordination
│   └── approval_service.py  # Approval workflow
│
├── tasks/
│   ├── __init__.py
│   ├── cloud_tasks.py       # Cloud Tasks client
│   └── scheduler.py         # Agent scheduler
│
├── api/
│   ├── autonomous.py        # Autonomous agent router
│   ├── webhooks.py          # Twilio webhooks
│   └── internal.py          # Internal task handlers
```

---

## Deployment Configuration

### Cloud Run Services

```yaml
services:
  - name: salon-flow-api
    region: asia-south1
    env:
      - GCP_PROJECT_ID=salon-saas-487508
      - GCP_REGION=asia-south1
      - PUBSUB_TOPIC=salon-events
    secrets:
      - TWILIO_ACCOUNT_SID
      - TWILIO_AUTH_TOKEN
      - UPSTASH_REDIS_REST_URL
      - UPSTASH_REDIS_REST_TOKEN
```

### IAM Permissions

```yaml
serviceAccount: salon-flow-api@salon-saas-487508.iam.gserviceaccount.com
roles:
  - roles/datastore.user
  - roles/pubsub.publisher
  - roles/pubsub.subscriber
  - roles/cloudtasks.enqueuer
  - roles/secretmanager.secretAccessor
```

---

## Monitoring & Observability

### Key Metrics

- `autonomous_decisions_total` - Total decisions by type
- `autonomous_decisions_success_rate` - Success rate
- `autonomous_revenue_generated` - Revenue from autonomous actions
- `agent_circuit_breaker_state` - Circuit breaker status
- `approval_response_time_seconds` - Time to approve/reject
- `outreach_delivery_rate` - Message delivery success

### Alerting Rules

```yaml
alerts:
  - name: high_failure_rate
    condition: success_rate < 0.8 for 5m
    severity: warning
    
  - name: circuit_breaker_open
    condition: circuit_breaker_state == open
    severity: critical
    
  - name: approval_backlog
    condition: pending_approvals > 10 for 15m
    severity: warning
```

---

## Next Steps

1. **Implement Twilio Integration**: Connect outreach service to Twilio API
2. **Add Frontend Components**: Approval UI in Owner PWA
3. **Implement Remaining Agents**: No-show prevention, waitlist, retention
4. **Add Analytics Dashboard**: Real-time metrics visualization
5. **Configure Cloud Scheduler**: Set up periodic agent triggers
