# Browser Testing Skill

## Overview
Comprehensive browser-based testing for Salon Flow PWAs using Playwright CLI. This skill enables AI agents to test, debug, and fix production issues across all four PWAs: Owner, Manager, Staff, and Client.

## Version
- Skill Version: 1.0.0
- Last Updated: 2026-02-22
- Author: Agent Zero

---

## 🎯 Prerequisites

### Install Playwright
```bash
# Install Playwright browsers
npx playwright install

# Install system dependencies (if needed)
npx playwright install-deps

# Verify installation
npx playwright --version
```

### Project URLs (Production)
| PWA | URL |
|-----|-----|
| Owner | https://owner-salonsaas-487508.asia-south1.run.app |
| Manager | https://manager-salonsaas-487508.asia-south1.run.app |
| Staff | http://localhost:3001 (dev) |
| Client | http://localhost:3002 (dev) |
| Backend API | https://api-salonsaas-487508.asia-south1.run.app |
| AI Service | https://ai-salonsaas-487508.asia-south1.run.app |

---

## 📁 Test Structure

```
tests/
├── e2e/
│   ├── owner.spec.ts      # Owner PWA tests
│   ├── manager.spec.ts    # Manager PWA tests
│   ├── staff.spec.ts      # Staff PWA tests
│   ├── client.spec.ts     # Client PWA tests
│   └── integration.spec.ts # Cross-service tests
└── fixtures/
    ├── staff.json
    ├── customers.json
    └── services.json
```

---

## 🚀 Core Procedures

### Procedure 1: Run All E2E Tests
**Use when:** Verifying full system health

```bash
# Run all tests
npx playwright test

# Run with specific browser
npx playwright test --project=chromium

# Run with visible browser (headed)
npx playwright test --headed

# Run with detailed output
npx playwright test --reporter=list
```

### Procedure 2: Test Specific PWA
**Use when:** Focusing on one application

```bash
# Test Owner PWA
npx playwright test tests/e2e/owner.spec.ts

# Test Manager PWA
npx playwright test tests/e2e/manager.spec.ts

# Test Staff PWA
npx playwright test tests/e2e/staff.spec.ts

# Test Client PWA
npx playwright test tests/e2e/client.spec.ts
```

### Procedure 3: Debug Failing Tests
**Use when:** Tests are failing

```bash
# Debug mode with Inspector
npx playwright test --debug --headed

# UI mode for interactive debugging
npx playwright test --ui

# Run only failed tests from last run
npx playwright test --last-failed

# View trace from failed test
npx playwright show-trace trace.zip
```

### Procedure 4: Generate New Tests
**Use when:** Creating tests for new features

```bash
# Record and generate test code
npx playwright codegen https://owner-salonsaas-487508.asia-south1.run.app

# Generate to specific file
npx playwright codegen https://manager-salonsaas-487508.asia-south1.run.app -o tests/e2e/new-feature.spec.ts

# Generate in different language
npx playwright codegen --target=python https://owner-salonsaas-487508.asia-south1.run.app
```

---

## 🤖 AI Agent Browser Automation (playwright-cli)

### Workflow Pattern
```
1. NAVIGATE → playwright-cli open <url>
2. SNAPSHOT → playwright-cli snapshot (get element refs: e1, e2, e3...)
3. INTERACT → playwright-cli click e3 / fill e5 "text"
4. VERIFY → playwright-cli screenshot
5. REPEAT → Re-snapshot after page changes
```

### Procedure 5: AI-Powered Login Test
**Use when:** Testing authentication flows

```bash
# Open login page
playwright-cli open https://owner-salonsaas-487508.asia-south1.run.app/login

# Get page snapshot
playwright-cli snapshot

# Fill email (use element ref from snapshot)
playwright-cli fill e5 "owner@salon.com"

# Fill password
playwright-cli fill e6 "password123"

# Click login button
playwright-cli click e7

# Verify login success
playwright-cli snapshot
playwright-cli screenshot login-success.png
```

### Procedure 6: AI-Powered Booking Flow Test
**Use when:** Testing customer booking journey

```bash
# Open client app
playwright-cli open https://client-salonsaas-487508.asia-south1.run.app

# Snapshot page
playwright-cli snapshot

# Click services
playwright-cli click e3

# Select service
playwright-cli snapshot
playwright-cli click e10

# Select date
playwright-cli fill e15 "2026-02-25"

# Select time slot
playwright-cli click e20

# Confirm booking
playwright-cli click e25

# Verify confirmation
playwright-cli screenshot booking-confirmed.png
```

---

## ✅ Production Readiness Checklist

### Owner PWA Tests
```typescript
// tests/e2e/owner.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Owner PWA - Production Ready', () => {
  test.use({ baseURL: 'https://owner-salonsaas-487508.asia-south1.run.app' });

  test('should load dashboard', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1')).toBeVisible();
  });

  test('should show analytics widgets', async ({ page }) => {
    await page.goto('/analytics');
    await expect(page.locator('[data-testid="revenue-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="booking-stats"]')).toBeVisible();
  });

  test('should manage staff', async ({ page }) => {
    await page.goto('/staff');
    await expect(page.locator('[data-testid="staff-list"]')).toBeVisible();
  });

  test('should show AI assistant', async ({ page }) => {
    await page.goto('/assistant');
    await expect(page.locator('[data-testid="chat-input"]')).toBeVisible();
  });

  test('should handle settings', async ({ page }) => {
    await page.goto('/settings');
    await expect(page.locator('[data-testid="salon-settings"]')).toBeVisible();
  });
});
```

### Manager PWA Tests
```typescript
// tests/e2e/manager.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Manager PWA - Production Ready', () => {
  test.use({ baseURL: 'https://manager-salonsaas-487508.asia-south1.run.app' });

  test('should load POS system', async ({ page }) => {
    await page.goto('/pos');
    await expect(page.locator('[data-testid="pos-terminal"]')).toBeVisible();
  });

  test('should process billing', async ({ page }) => {
    await page.goto('/billing');
    await expect(page.locator('[data-testid="bill-form"]')).toBeVisible();
  });

  test('should show today\'s appointments', async ({ page }) => {
    await page.goto('/appointments');
    await expect(page.locator('[data-testid="appointment-list"]')).toBeVisible();
  });

  test('should handle price override', async ({ page }) => {
    await page.goto('/billing');
    await page.click('[data-testid="override-price"]');
    await expect(page.locator('[data-testid="override-dialog"]')).toBeVisible();
  });

  test('should show real-time notifications', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('[data-testid="notification-bell"]')).toBeVisible();
  });
});
```

### Staff PWA Tests
```typescript
// tests/e2e/staff.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Staff PWA - Production Ready', () => {
  test.use({ baseURL: 'http://localhost:3001' });

  test('should login with PIN', async ({ page }) => {
    await page.goto('/login');
    await page.fill('[data-testid="staff-id"]', 'STAFF001');
    await page.fill('[data-testid="pin"]', '1234');
    await page.click('text=Login');
    await expect(page).toHaveURL(/dashboard/);
  });

  test('should show today\'s schedule', async ({ page }) => {
    await page.goto('/schedule');
    await expect(page.locator('[data-testid="schedule-list"]')).toBeVisible();
  });

  test('should allow QR check-in', async ({ page }) => {
    await page.goto('/checkin');
    await page.click('[data-testid="scan-qr"]');
    await expect(page.locator('[data-testid="qr-scanner"]')).toBeVisible();
  });

  test('should add upsell service', async ({ page }) => {
    await page.goto('/appointments');
    await page.click('[data-testid="appointment-card"]:first-child');
    await page.click('text=Add Service');
    await expect(page.locator('[data-testid="service-list"]')).toBeVisible();
  });
});
```

### Client PWA Tests
```typescript
// tests/e2e/client.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Client PWA - Production Ready', () => {
  test.use({ baseURL: 'http://localhost:3002' });

  test('should load homepage', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1')).toContainText('Salon Flow');
  });

  test('should show services', async ({ page }) => {
    await page.goto('/services');
    await expect(page.locator('[data-testid="service-card"]')).toHaveCountGreaterThan(0);
  });

  test('should complete booking flow', async ({ page }) => {
    await page.goto('/services');
    await page.click('[data-testid="service-card"]:first-child');
    await page.fill('[data-testid="date-picker"]', '2026-02-25');
    await page.click('[data-testid="time-slot"]:first-child');
    await page.click('text=Confirm Booking');
    await expect(page.locator('.toast-success')).toBeVisible();
  });

  test('should show QR code on confirmation', async ({ page }) => {
    await page.goto('/booking/confirmation/test-booking-id');
    await expect(page.locator('[data-testid="qr-code"]')).toBeVisible();
  });

  test('should handle phone OTP login', async ({ page }) => {
    await page.goto('/login');
    await page.fill('[data-testid="phone-input"]', '+919876543210');
    await page.click('text=Send OTP');
    await expect(page.locator('[data-testid="otp-input"]')).toBeVisible();
  });
});
```

---

## 🔧 Common Fixes

### Fix 1: Authentication Issues
**Symptom:** 401 Unauthorized errors

```bash
# Check if Firebase Auth is properly initialized
# Check if JWT token is being sent
# Verify CORS settings

# Test API health
curl https://api-salonsaas-487508.asia-south1.run.app/health
```

### Fix 2: Page Not Loading
**Symptom:** Blank page or 404

```bash
# Check if PWA is deployed
gcloud run services list --region=asia-south1

# Check logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# Verify build succeeded
ls -la apps/owner/dist/
```

### Fix 3: API Connection Failed
**Symptom:** Network errors in console

```bash
# Check CORS configuration
# Verify API URL in environment
# Check if API is healthy

curl -I https://api-salonsaas-487508.asia-south1.run.app/docs
```

### Fix 4: AI Chat Not Working
**Symptom:** Chat input not responding

```bash
# Check AI service health
curl https://ai-salonsaas-487508.asia-south1.run.app/health

# Check OpenRouter API key
gcloud secrets versions access latest --secret="openrouter-api-key"

# Check Redis connection
curl https://ai-salonsaas-487508.asia-south1.run.app/health/redis
```

---

## 📊 Test Reports

### Generate HTML Report
```bash
# Run tests and generate report
npx playwright test --reporter=html

# View report
npx playwright show-report
```

### Generate JSON Report
```bash
npx playwright test --reporter=json --output=test-results.json
```

### CI/CD Integration
```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx playwright test
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

---

## 🎭 Playwright Config

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## 📝 Quick Reference

| Task | Command |
|------|--------|
| Run all tests | `npx playwright test` |
| Run specific test | `npx playwright test path/to/test.spec.ts` |
| Debug mode | `npx playwright test --debug` |
| UI mode | `npx playwright test --ui` |
| Headed mode | `npx playwright test --headed` |
| Generate tests | `npx playwright codegen <url>` |
| View report | `npx playwright show-report` |
| View trace | `npx playwright show-trace trace.zip` |
| Install browsers | `npx playwright install` |
| Update snapshots | `npx playwright test -u` |

---

## 🚨 Troubleshooting

### Test Timeout Issues
```bash
# Increase timeout
npx playwright test --timeout=60000

# Or in test file
test('my test', async ({ page }) => {
  test.setTimeout(60000);
});
```

### Flaky Tests
```bash
# Run with retries
npx playwright test --retries=3

# Run serially
npx playwright test --workers=1
```

### Browser Not Found
```bash
# Install specific browser
npx playwright install chromium

# Install all dependencies
npx playwright install-deps
```

---

## 📚 Related Skills
- `e2e_testing` - Basic E2E testing patterns
- `cicd_pipeline` - CI/CD integration
- `performance_testing` - Load testing
- `security_testing` - Security audits
