# Testing Strategy - Salon_Flow

## Overview
Salon_Flow employs a dual-layer testing approach ensuring comprehensive coverage across all layers of the application.

## Layer 1: Backend Testing (pytest)

### API Tests
**Location**: `tests/api/`

| Test File | Coverage |
|-----------|----------|
| test_auth.py | Firebase Auth, JWT validation |
| test_tenants.py | Multi-tenant isolation, tenant CRUD |
| test_staff.py | Staff management, skills validation |
| test_customers.py | Customer profiles, booking history |
| test_bookings.py | Appointment scheduling, conflicts |
| test_services.py | Service catalog, pricing |
| test_payments.py | Payment processing, refunds |
| test_memberships.py | Subscription management |
| test_resources.py | Resource allocation |
| test_shifts.py | Staff scheduling |
| test_billing.py | Invoicing, reports |
| test_onboarding.py | Tenant onboarding flows |

### AI Service Tests
**Location**: `tests/ai/`

| Test File | Coverage |
|-----------|----------|
| test_ai_service.py | Core AI service functionality |
| test_agents_router.py | Agent routing logic |
| test_agents_router_comprehensive.py | Full agent routing suite |
| test_chat_api.py | Chat endpoints |
| test_chat.py | Chat functionality |
| test_analytics.py | Analytics pipeline |
| test_guardrails.py | Safety filters |
| test_cache_service.py | Redis caching |
| test_openrouter_client.py | LLM integration |
| test_pipeline.py | Processing pipeline |
| test_processor.py | Message processing |
| test_plugins.py | Plugin system |
| test_new_agents.py | New agent implementations |
| test_all_agents.py | Comprehensive agent tests |
| test_integration.py | End-to-end AI flows |
| test_adapters.py | External service adapters |
| test_marketing_api.py | Marketing automation |

### Running Backend Tests
```bash
# Run all API tests
pytest tests/api/ -v

# Run specific test file
pytest tests/api/test_auth.py -v

# Run with coverage
pytest tests/api/ --cov=services/api --cov-report=html

# Run AI tests
pytest tests/ai/ -v
```

## Layer 2: PWA/E2E Testing (Playwright CLI)

### Playwright CLI Version
- **Version**: 1.58.2
- **Workflow**: Navigate → Snapshot → Interact → Verify

### Configuration Files

| Config File | Purpose | Environment |
|-------------|---------|-------------|
| `playwright.config.ts` | Default local testing | Local Vite server |
| `playwright.prod.config.ts` | Production testing | Live production URL |
| `playwright.gcp.config.ts` | GCP deployment testing | Cloud Run |
| `playwright.debug.config.ts` | Debug mode with traces | Any |

### Test Files (E2E)

| Test File | App | Coverage |
|-----------|-----|----------|
| owner.spec.ts | Owner PWA | Authentication, dashboard, settings |
| owner-workflows.spec.ts | Owner PWA | Core business workflows |
| owner-scenarios.spec.ts | Owner PWA | Real-world scenarios |
| owner-deep-workflows.spec.ts | Owner PWA | Complex workflows |
| owner-gcp-integration.spec.ts | Owner PWA | GCP infrastructure tests |
| manager.spec.ts | Manager PWA | Manager portal features |
| staff.spec.ts | Staff PWA | Staff app functionality |
| client.spec.ts | Client PWA | Client booking experience |
| integration.spec.ts | All | Cross-app integration |
| cli-debug.spec.ts | All | CLI debugging utilities |

### PWA-Specific Testing

#### Service Worker Testing
1. Visit PWA online to register service worker
2. Wait for 'activated' state
3. Test offline mode with `context.setOffline(true)`
4. Verify cached content loads correctly

#### Manifest Testing
- Use `.first()` selector for `link[rel="manifest"]`
- Handle multiple manifest links (manifest.json, manifest.webmanifest)
- Verify PWA installability

#### Authentication Testing
- Use Firebase Auth JWT via localStorage (`salon_flow_token`)
- Use 'Storage State' for auth injection
- Use `await loginWithGCP(page)` helpers for GCP

### Running E2E Tests

```bash
# Run all E2E tests locally
npx playwright test

# Run specific PWA app tests
npx playwright test tests/e2e/owner.spec.ts
npx playwright test tests/e2e/staff.spec.ts
npx playwright test tests/e2e/manager.spec.ts
npx playwright test tests/e2e/client.spec.ts

# Run against production
npx playwright test --config=playwright.prod.config.ts

# Run GCP integration tests
npx playwright test --config=playwright.gcp.config.ts

# Run with debug traces
npx playwright test --config=playwright.debug.config.ts --trace on

# Run headed (visible browser)
npx playwright test --headed

# Run specific project
npx playwright test --project="Owner PWA"

# View HTML report
npx playwright show-report

# View GCP report
npx playwright show-report playwright-report-gcp
```

## Test Results & Artifacts

### Output Locations
- **Test Results**: `test-results/`
- **HTML Reports**: `playwright-report/`, `playwright-report-gcp/`
- **Traces**: `test-results/**/*.zip`
- **Screenshots**: `test-results/**/*.png`

### Trace Analysis
```bash
# Show trace viewer
npx playwright show-trace test-results/[test-name]/trace.zip
```

## Coverage Targets

| Layer | Target | Current |
|-------|--------|---------|
| Backend API | 85% | ~80% |
| AI Service | 80% | ~75% |
| E2E (Critical Paths) | 90% | ~90% |
| E2E (Full Suite) | 70% | ~69% |

## Testing Tools

### Backend
- pytest
- pytest-asyncio
- pytest-cov
- httpx (for async HTTP testing)

### E2E
- Playwright CLI 1.58.2
- @playwright/test
- Playwright HTML reporter
- Playwright trace viewer

## CI/CD Integration

### GitHub Actions
- `.github/workflows/test.yml` - Runs on PR
- `.github/workflows/deploy.yml` - Runs on main

### Test Gates
1. All API tests must pass
2. All AI service tests must pass
3. Critical E2E tests must pass
4. Coverage must not decrease

## Best Practices

### E2E Testing
- Use ARIA selectors over `data-testid` when possible
- Prefer `getByRole`, `getByPlaceholder`, `getByLabel`
- Use storage state for auth to speed up tests
- Group related tests with `test.describe()`
- Use `test.beforeEach()` for common setup
- Tag slow tests with `test.slow()`
- Use snapshots for visual regression testing

### API Testing
- Mock external services (Twilio, OpenRouter)
- Use test fixtures for database seeding
- Clean up test data after tests
- Test both success and error cases
- Validate response schemas with Pydantic
