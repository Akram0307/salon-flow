# AI Service Module Implementation Plan

## 📊 Current State Analysis

### Deployed Services Status
| Service | Status | Routes | Notes |
|---------|--------|--------|-------|
| salon-flow-ai | ✅ Healthy | 16 | OpenRouter + Redis connected |
| salon-backend | ✅ Healthy | 59 | Core API functional |
| salon-flow-api | ⚠️ Timeout | - | Cold start issue (scale-to-zero) |

### Current AI Service Capabilities
- **12 Specialized Agents**: Booking, Marketing, Analytics, Support, Waitlist, Slot Optimizer, Upsell, Dynamic Pricing, Bundle Creator, Inventory, Scheduling, Retention
- **Basic Infrastructure**: OpenRouter integration, Redis caching, Guardrails
- **Model**: Gemini 2.5 Flash (default)

### Missing Components for Hybrid Architecture
1. **Hexagonal Layer**: WhatsApp/Voice/Web adapters
2. **Pipeline Layer**: Semantic cache, model router
3. **Microkernel**: Plugin system for agents
4. **CQRS**: Vector DB for fast reads
5. **Event Integration**: Pub/Sub with backend

---

## 🎯 Implementation Task List

### Phase 1: Backend Integration Preparation (2-3 days)

#### Task 1.1: Fix salon-flow-api Cold Start Issue
- [ ] Increase Cloud Run min instances to 1 (eliminate cold starts)
- [ ] Update Cloud Run timeout configuration
- [ ] Add warmup endpoint
- **Backend Changes Required**: None
- **Priority**: High

#### Task 1.2: Create AI Integration Endpoints in Backend
- [ ] Add `/api/v1/ai/chat` proxy endpoint
- [ ] Add `/api/v1/ai/agents` endpoint
- [ ] Add `/api/v1/ai/insights` endpoint
- [ ] Create shared authentication middleware
- **Backend Changes Required**: New router `ai_proxy.py`
- **Priority**: High

#### Task 1.3: Setup Event-Driven Communication
- [ ] Create GCP Pub/Sub topic: `salon-events`
- [ ] Create Pub/Sub topic: `ai-tasks`
- [ ] Add event publishing in backend (booking created, cancelled, etc.)
- [ ] Add event subscription in AI service
- **Backend Changes Required**: Event publisher utility
- **Priority**: Medium

---

### Phase 2: Hybrid Architecture Core (3-4 days)

#### Task 2.1: Hexagonal Adapters Layer
- [ ] Create `adapters/` directory structure
- [ ] Implement `BaseAdapter` abstract class
- [ ] Implement `WhatsAppAdapter` (Twilio integration)
- [ ] Implement `WebChatAdapter` (WebSocket)
- [ ] Implement `VoiceAdapter` (Twilio Voice - placeholder)
- **Backend Changes Required**: None
- **Priority**: High

#### Task 2.2: Pipeline Processing Layer
- [ ] Create `pipeline/` directory structure
- [ ] Implement `GuardrailLayer` (existing, refactor)
- [ ] Implement `ExactCacheLayer` (Redis)
- [ ] Implement `SemanticCacheLayer` (Upstash Vector)
- [ ] Implement `ModelRouterLayer` (cost optimization)
- **Backend Changes Required**: None
- **Priority**: High

#### Task 2.3: Microkernel Plugin System
- [ ] Create `plugins/` directory structure
- [ ] Implement `PluginLoader` with auto-discovery
- [ ] Implement `BaseAgentPlugin` class
- [ ] Migrate existing 12 agents to plugin format
- [ ] Add hot-reload capability
- **Backend Changes Required**: None
- **Priority**: Medium

#### Task 2.4: CQRS Data Layer
- [ ] Setup Upstash Vector index
- [ ] Create `read_models/` for denormalized data
- [ ] Implement sync mechanism (Firestore → Vector)
- [ ] Add customer embeddings for semantic search
- **Backend Changes Required**: Firestore triggers (optional)
- **Priority**: Medium

---

### Phase 3: Enhanced AI Features (2-3 days)

#### Task 3.1: Multi-Model Router
- [ ] Implement tiered model selection
  - Tier 1: Gemini 2.0 Flash (free) - simple queries
  - Tier 2: Gemini 2.5 Flash - standard queries
  - Tier 3: Gemini 3.0 Pro - complex reasoning
- [ ] Add query complexity analyzer
- [ ] Implement fallback chain
- **Backend Changes Required**: None
- **Priority**: High

#### Task 3.2: Semantic Caching
- [ ] Create embedding for queries
- [ ] Implement similarity search (threshold: 0.95)
- [ ] Add cache invalidation logic
- [ ] Track cache hit rates
- **Backend Changes Required**: None
- **Priority**: High

#### Task 3.3: Context Management
- [ ] Implement conversation history (Redis)
- [ ] Add salon context injection
- [ ] Create user preference tracking
- [ ] Add session management
- **Backend Changes Required**: None
- **Priority**: Medium

---

### Phase 4: WhatsApp Integration (2-3 days)

#### Task 4.1: Twilio WhatsApp Setup
- [ ] Configure Twilio credentials in GCP Secret Manager
- [ ] Create webhook endpoint `/webhook/whatsapp`
- [ ] Implement message parsing
- [ ] Add message formatting (WhatsApp templates)
- **Backend Changes Required**: None
- **Priority**: High (blocked by Twilio credentials)

#### Task 4.2: WhatsApp Agent Implementation
- [ ] Create `WhatsAppConciergeAgent`
- [ ] Implement booking flow via WhatsApp
- [ ] Add menu navigation
- [ ] Implement confirmation messages
- **Backend Changes Required**: None
- **Priority**: High

---

### Phase 5: Testing & Deployment (2 days)

#### Task 5.1: Comprehensive Testing
- [ ] Unit tests for all new components
- [ ] Integration tests for pipeline
- [ ] End-to-end WhatsApp flow tests
- [ ] Performance benchmarks
- **Backend Changes Required**: None
- **Priority**: High

#### Task 5.2: Deployment
- [ ] Update Cloud Run configuration
- [ ] Deploy new AI service
- [ ] Configure Pub/Sub subscriptions
- [ ] Setup monitoring and alerts
- **Backend Changes Required**: Deploy updated backend
- **Priority**: High

---

## 📋 Backend Changes Summary

### Required Changes in `services/api/`

1. **New Router: `app/api/ai_proxy.py`**
   - Proxy endpoints to AI service
   - Shared authentication
   - Request/response transformation

2. **New Utility: `app/services/event_publisher.py`**
   - Pub/Sub event publishing
   - Event schemas
   - Error handling

3. **Updated: `app/api/bookings.py`**
   - Publish `booking.created` event
   - Publish `booking.cancelled` event
   - Publish `booking.completed` event

4. **Updated: `app/api/customers.py`**
   - Publish `customer.created` event
   - Publish `customer.updated` event

5. **Updated: `app/core/config.py`**
   - Add `ai_service_url` config
   - Add `pubsub_topic` config

### No Breaking Changes
- All existing endpoints remain unchanged
- New endpoints are additive
- Event publishing is optional (graceful degradation)

---

## 📅 Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Backend Integration | 2-3 days | None |
| Phase 2: Hybrid Architecture | 3-4 days | Phase 1 |
| Phase 3: Enhanced Features | 2-3 days | Phase 2 |
| Phase 4: WhatsApp | 2-3 days | Twilio credentials |
| Phase 5: Testing & Deploy | 2 days | All phases |
| **Total** | **11-15 days** | |

---

## 💰 Cost Impact

| Component | Monthly Cost |
|-----------|-------------|
| Upstash Vector (1M vectors) | ~₹200 |
| Additional Cloud Run (AI) | ~₹0 (scale-to-zero) |
| Pub/Sub (1M messages) | ~₹50 |
| **Total Additional** | **~₹250/month** |

**Projected Total**: ~₹1,750/month (within ₹15,000 budget)

---

## ✅ Approval Required

Please review and approve:

1. **Backend Changes**: Add AI proxy endpoints and event publishing
2. **Architecture**: Hybrid architecture implementation approach
3. **Timeline**: 11-15 days implementation
4. **Cost**: Additional ~₹250/month for Upstash Vector

---

*Generated: 2026-02-21*
*Project: Salon Flow v0.3.0*
