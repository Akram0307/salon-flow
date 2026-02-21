# Salon Flow - AI Agents Master Plan
## 25 Specialized AI Agents for Salon Management SaaS

**Generated:** 2026-02-21  
**Status:** Planning Phase  
**Target:** 25 AI Agents (12 Implemented + 13 New)

---

## 📊 Current Status Summary

| Category | Implemented | Planned | Total |
|----------|-------------|---------|-------|
| Core Operations | 4 | 0 | 4 |
| Revenue Optimization | 4 | 2 | 6 |
| Operations Management | 2 | 3 | 5 |
| Customer Experience | 2 | 3 | 5 |
| Marketing & Growth | 0 | 5 | 5 |
| **TOTAL** | **12** | **13** | **25** |

---

## 🤖 Complete Agent Registry (25 Agents)

### ✅ PHASE 1: Core Operations Agents (4 Implemented)

| # | Agent Name | Status | Model | Purpose |
|---|------------|--------|-------|---------|
| 1 | **Booking Agent** | ✅ Implemented | gemini-2.5-flash | Handle appointment booking, rescheduling, cancellations |
| 2 | **Marketing Agent** | ✅ Implemented | gemini-2.5-flash | Generate campaigns, offers, promotional content |
| 3 | **Analytics Agent** | ✅ Implemented | gemini-2.5-flash | Business insights, revenue analysis, trends |
| 4 | **Customer Support Agent** | ✅ Implemented | gemini-2.5-flash | Handle queries, complaints, FAQs |

### ✅ PHASE 2: Revenue Optimization Agents (4 Implemented + 2 Planned)

| # | Agent Name | Status | Model | Purpose |
|---|------------|--------|-------|---------|
| 5 | **Waitlist Manager** | ✅ Implemented | gemini-2.5-flash | Auto-fill cancellations, prioritize waitlist |
| 6 | **Slot Optimizer** | ✅ Implemented | gemini-2.5-flash | Detect gaps, fill idle time, optimize schedule |
| 7 | **Upsell Engine** | ✅ Implemented | gemini-2.5-flash | Suggest add-ons, upgrades, combos |
| 8 | **Dynamic Pricing** | ✅ Implemented | gemini-2.5-flash | Demand-based pricing, peak/off-peak adjustments |
| 9 | **Bundle Creator** | ✅ Implemented | gemini-2.5-flash | Create service packages, bridal/groom bundles |
| 10 | **Demand Predictor** | 🔲 Planned | gemini-2.5-flash | Forecast demand, predict busy periods |

### ✅ PHASE 3: Operations Management Agents (2 Implemented + 3 Planned)

| # | Agent Name | Status | Model | Purpose |
|---|------------|--------|-------|---------|
| 11 | **Inventory Intelligence** | ✅ Implemented | gemini-2.5-flash | Stock monitoring, reorder alerts, usage analysis |
| 12 | **Staff Scheduling** | ✅ Implemented | gemini-2.5-flash | Shift optimization, skill matching, time-off |
| 13 | **Quality Assurance** | 🔲 Planned | gemini-2.5-flash | Service quality monitoring, compliance checks |
| 14 | **Resource Allocator** | 🔲 Planned | gemini-2.5-flash | Chair/room assignment, equipment management |
| 15 | **Compliance Monitor** | 🔲 Planned | gemini-2.5-flash | Hygiene standards, safety protocols |

### ✅ PHASE 4: Customer Experience Agents (2 Implemented + 3 Planned)

| # | Agent Name | Status | Model | Purpose |
|---|------------|--------|-------|---------|
| 16 | **Customer Retention** | ✅ Implemented | gemini-2.5-flash | At-risk detection, winback campaigns |
| 17 | **WhatsApp Concierge** | 🔲 Planned | gemini-2.5-flash | WhatsApp booking, inquiries, support |
| 18 | **Voice Receptionist** | 🔲 Planned | gemini-2.5-flash | Phone booking, call handling |
| 19 | **Feedback Analyzer** | 🔲 Planned | gemini-2.5-flash | Review analysis, sentiment tracking |
| 20 | **VIP Priority** | 🔲 Planned | gemini-2.5-flash | Premium customer handling, special treatment |

### ✅ PHASE 5: Marketing & Growth Agents (5 Planned)

| # | Agent Name | Status | Model | Purpose |
|---|------------|--------|-------|---------|
| 21 | **Social Media Manager** | 🔲 Planned | gemini-2.5-flash | Post scheduling, engagement, content creation |
| 22 | **Image Creatives Generator** | 🔲 Planned | gemini-3-pro-image | Generate marketing images, posters |
| 23 | **Content Writer** | 🔲 Planned | gemini-2.5-flash | Blog posts, captions, ad copy |
| 24 | **Review Monitor** | 🔲 Planned | gemini-2.5-flash | Track reviews, respond to feedback |
| 25 | **Campaign Orchestrator** | 🔲 Planned | gemini-2.5-flash | Multi-channel campaign management |

---

## 📋 Implementation Task List

### 🔴 HIGH PRIORITY - Phase 2 Completion (2 Agents)

| Task ID | Agent | Description | Assigned To | Est. Time |
|---------|-------|-------------|-------------|----------|
| AI-010 | Demand Predictor | Forecast demand using historical data | AI Engineer | 4 hours |
| AI-011 | WhatsApp Concierge | Twilio integration for WhatsApp booking | AI Engineer | 6 hours |

### 🟠 MEDIUM PRIORITY - Phase 3 Completion (3 Agents)

| Task ID | Agent | Description | Assigned To | Est. Time |
|---------|-------|-------------|-------------|----------|
| AI-012 | Quality Assurance | Service quality monitoring system | AI Engineer | 4 hours |
| AI-013 | Resource Allocator | Chair/room assignment optimization | AI Engineer | 4 hours |
| AI-014 | Compliance Monitor | Hygiene & safety compliance | AI Engineer | 3 hours |

### 🟡 STANDARD PRIORITY - Phase 4 Completion (3 Agents)

| Task ID | Agent | Description | Assigned To | Est. Time |
|---------|-------|-------------|-------------|----------|
| AI-015 | Voice Receptionist | Twilio Voice integration | AI Engineer | 8 hours |
| AI-016 | Feedback Analyzer | Sentiment analysis, review processing | AI Engineer | 4 hours |
| AI-017 | VIP Priority | Premium customer handling | AI Engineer | 3 hours |

### 🟢 ENHANCEMENT PRIORITY - Phase 5 Completion (5 Agents)

| Task ID | Agent | Description | Assigned To | Est. Time |
|---------|-------|-------------|-------------|----------|
| AI-018 | Social Media Manager | Multi-platform social management | AI Engineer | 6 hours |
| AI-019 | Image Creatives Generator | Marketing image generation | AI Engineer | 4 hours |
| AI-020 | Content Writer | Blog, caption, ad copy generation | AI Engineer | 4 hours |
| AI-021 | Review Monitor | Review tracking & response | AI Engineer | 3 hours |
| AI-022 | Campaign Orchestrator | Multi-channel campaign management | AI Engineer | 5 hours |

---

## 🏗️ Architecture Requirements

### Hybrid Architecture Components

1. **Hexagonal Layer** - Multi-channel adapters (WhatsApp, Voice, Web, SMS)
2. **Pipeline Layer** - Request processing, caching, guardrails
3. **Microkernel Layer** - Plugin-based agent management
4. **CQRS Layer** - Optimized read/write operations

### Infrastructure Requirements

| Component | Current | Required | Status |
|-----------|---------|----------|--------|
| OpenRouter API | ✅ Active | - | Configured |
| Upstash Redis | ✅ Active | - | Configured |
| Upstash Vector | 🔲 Needed | For RAG | Pending |
| Twilio WhatsApp | 🔲 Needed | For Concierge | Pending Credentials |
| Twilio Voice | 🔲 Needed | For Receptionist | Pending Credentials |
| GCP Pub/Sub | ✅ Active | - | Configured |

---

## 👥 Expert Agent Assignments

### AI Engineer Team (Primary)
- **AI-Engineer-1**: Core agent development (Demand Predictor, Quality Assurance)
- **AI-Engineer-2**: Integration agents (WhatsApp Concierge, Voice Receptionist)
- **AI-Engineer-3**: Marketing agents (Social Media, Content, Campaigns)

### Backend Developer Team (Support)
- **Backend-Dev-1**: API endpoints for new agents
- **Backend-Dev-2**: Database schema updates

### DevOps Engineer (Infrastructure)
- **DevOps-1**: Twilio setup, Upstash Vector configuration

### QA Engineer (Testing)
- **QA-1**: Agent testing, integration testing

---

## 📅 Implementation Timeline

| Week | Phase | Tasks | Deliverables |
|------|-------|-------|--------------|
| Week 1 | Phase 2 | AI-010, AI-011 | Demand Predictor, WhatsApp Concierge |
| Week 2 | Phase 3 | AI-012, AI-013, AI-014 | QA, Resource, Compliance Agents |
| Week 3 | Phase 4 | AI-015, AI-016, AI-017 | Voice, Feedback, VIP Agents |
| Week 4 | Phase 5 | AI-018 to AI-022 | Marketing Suite (5 agents) |

---

## 💰 Cost Estimation

| Component | Monthly Cost |
|-----------|-------------|
| OpenRouter API (25 agents) | ~₹800 |
| Upstash Redis | ₹850 |
| Upstash Vector (new) | ~₹500 |
| Twilio WhatsApp | ~₹4,500 |
| GCP Cloud Run | ~₹300 |
| **Total** | **~₹6,950** |

**Budget Status:** ✅ Under ₹15,000 target (53% savings)

---

## ✅ Approval Required

1. **Technical Stack** - Confirm Gemini models via OpenRouter
2. **Architecture** - Approve Hybrid Architecture implementation
3. **Timeline** - Confirm 4-week implementation schedule
4. **Budget** - Approve ₹6,950/month operational cost
5. **Twilio Credentials** - Provide for WhatsApp/Voice agents

---

*Document Version: 1.0*  
*Last Updated: 2026-02-21*
