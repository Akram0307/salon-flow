# Playwright PWA Testing Skill

## Overview
Test Salon Flow Progressive Web Apps (PWAs) using Playwright CLI. Covers Owner, Manager, Staff, and Client PWAs with multi-tenant, role-based, and offline testing strategies.

## Prerequisites

### Environment Setup
```bash
# Install Playwright dependencies
npm install -g @playwright/test
npx playwright install

# Verify installation
npx playwright --version
```

### Project Structure
```
/a0/usr/projects/salon_flow/
├── apps/
│   ├── owner/          # Owner PWA (Vite + React)
│   ├── manager/        # Manager PWA (Vite + React)
│   ├── staff/          # Staff PWA (Vite + React)
│   └── client/         # Client PWA (Vite + React)
├── tests/e2e/          # E2E test specs
├── playwright.config.ts
└── playwright.*.config.ts  # Environment-specific configs
```

## Quick Start

### 1. Run All Tests
```bash
cd /a0/usr/projects/salon_flow
npx playwright test
```

### 2. Run Tests for Specific PWA
```bash
# Owner PWA tests
npx playwright test tests/e2e/owner*.spec.ts

# Manager PWA tests
npx playwright test tests/e2e/manager*.spec.ts

# Staff PWA tests
npx playwright test tests/e2e/staff*.spec.ts

# Client PWA tests
npx playwright test tests/e2e/client*.spec.ts
```

### 3. Run Tests with Specific Config
```bash
# Production config
npx playwright test --config=playwright.prod.config.ts

# Debug config
npx playwright test --config=playwright.debug.config.ts

# Integration config
npx playwright test --config=playwright.integration.config.json
```

## CLI Commands Reference

### Basic Commands
| Command | Description |
|---------|-------------|
| `npx playwright test` | Run all tests |
| `npx playwright test --ui` | Run with UI mode |
| `npx playwright test --headed` | Run in headed mode (visible browser) |
| `npx playwright test --debug` | Run with debugger |
| `npx playwright test --trace on` | Enable tracing |

### Filtering & Selection
| Command | Description |
|---------|-------------|
| `npx playwright test --grep "owner"` | Run tests matching pattern |
| `npx playwright test --project=chromium` | Run on specific browser |
| `npx playwright test tests/e2e/owner.spec.ts:42` | Run specific line |
| `npx playwright test --last-failed` | Re-run failed tests |

### Reporting & Output
| Command | Description |
|---------|-------------|
| `npx playwright test --reporter=list` | List reporter |
| `npx playwright test --reporter=html` | HTML report |
| `npx playwright test --reporter=json` | JSON output |
| `npx playwright show-report` | Open HTML report |

### Parallel Execution
| Command | Description |
|---------|-------------|
| `npx playwright test --workers=4` | Run with 4 workers |
| `npx playwright test --fully-parallel` | Fully parallel mode |
| `npx playwright test --shard=1/3` | Run shard 1 of 3 |

## PWA-Specific Testing

### Service Worker Testing
```typescript
// tests/e2e/pwa-service-worker.spec.ts
import { test, expect } from '@playwright/test';

test.describe('PWA Service Worker', () => {
  test('service worker registers', async ({ page }) => {
    await page.goto('/');
    
    const swRegistration = await page.evaluate(async () => {
      const registration = await navigator.serviceWorker.ready;
      return registration.scope;
    });
    
    expect(swRegistration).toBeDefined();
  });

  test('app works offline', async ({ page, context }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Go offline
    await context.setOffline(true);
    
    // Reload should still work (cached)
    await page.reload();
    await expect(page.locator('[data-testid="app-root"]')).toBeVisible();
    
    // Restore online
    await context.setOffline(false);
  });

  test('background sync queues requests', async ({ page, context }) => {
    await page.goto('/bookings');
    
    // Go offline
    await context.setOffline(true);
    
    // Create booking while offline
    await page.fill('[data-testid="customer-name"]', 'Test Customer');
    await page.click('[data-testid="save-booking"]');
    
    // Should show offline queue indicator
    await expect(page.locator('[data-testid="sync-pending"]')).toBeVisible();
    
    // Go online - should sync
    await context.setOffline(false);
    await expect(page.locator('[data-testid="sync-complete"]')).toBeVisible({ timeout: 10000 });
  });
});
```

### Mobile Viewport Testing
```typescript
// tests/e2e/mobile-responsive.spec.ts
import { test, expect, devices } from '@playwright/test';

const mobileDevices = [
  { name: 'iPhone 14', viewport: { width: 390, height: 844 } },
  { name: 'iPhone SE', viewport: { width: 375, height: 667 } },
  { name: 'Pixel 7', viewport: { width: 412, height: 915 } },
  { name: 'Samsung S22', viewport: { width: 360, height: 780 } },
];

for (const device of mobileDevices) {
  test.describe(`Mobile: ${device.name}`, () => {
    test.use({ viewport: device.viewport });
    
    test('navigation is accessible', async ({ page }) => {
      await page.goto('/');
      
      // Bottom nav should be visible on mobile
      await expect(page.locator('[data-testid="bottom-nav"]')).toBeVisible();
      
      // Side nav should be hidden
      await expect(page.locator('[data-testid="sidebar"]')).toBeHidden();
    });

    test('touch targets are adequate size', async ({ page }) => {
      await page.goto('/bookings');
      
      const buttons = await page.locator('button').all();
      for (const button of buttons) {
        const box = await button.boundingBox();
        expect(box?.width).toBeGreaterThanOrEqual(44);
        expect(box?.height).toBeGreaterThanOrEqual(44);
      }
    });
  });
}
```

### Install Prompt Testing
```typescript
// tests/e2e/pwa-install.spec.ts
test('PWA install prompt appears', async ({ page }) => {
  await page.goto('/');
  
  // Simulate beforeinstallprompt event
  await page.evaluate(() => {
    const event = new Event('beforeinstallprompt');
    (event as any).prompt = () => Promise.resolve({ outcome: 'accepted' });
    (event as any).userChoice = Promise.resolve({ outcome: 'accepted' });
    window.dispatchEvent(event);
  });
  
  // Install button should appear
  await expect(page.locator('[data-testid="install-pwa"]')).toBeVisible();
  
  // Click install
  await page.click('[data-testid="install-pwa"]');
  
  // Should show installed state
  await expect(page.locator('[data-testid="pwa-installed"]')).toBeVisible();
});
```

## Multi-Tenant Testing

### Tenant Isolation Tests
```typescript
// tests/e2e/multi-tenant.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Multi-Tenant Isolation', () => {
  const tenants = [
    { id: 'tenant-a', name: 'Salon A', subdomain: 'salon-a' },
    { id: 'tenant-b', name: 'Salon B', subdomain: 'salon-b' },
  ];

  for (const tenant of tenants) {
    test(`data isolation for ${tenant.name}`, async ({ browser }) => {
      // Context 1: Tenant A
      const context1 = await browser.newContext({
        storageState: `auth-${tenant.id}.json`,
      });
      const page1 = await context1.newPage();
      
      await page1.goto(`https://${tenant.subdomain}.salonflow.app/dashboard`);
      await page1.fill('[data-testid="service-name"]', 'Tenant A Service');
      await page1.click('[data-testid="save-service"]');
      
      // Context 2: Different tenant
      const context2 = await browser.newContext({
        storageState: 'auth-tenant-b.json',
      });
      const page2 = await context2.newPage();
      
      await page2.goto('https://salon-b.salonflow.app/services');
      
      // Should NOT see Tenant A's service
      await expect(page2.locator('text=Tenant A Service')).toBeHidden();
      
      await context1.close();
      await context2.close();
    });
  }
});
```

## Role-Based Testing

### Owner PWA Tests
```typescript
// tests/e2e/owner.spec.ts
test.describe('Owner PWA', () => {
  test.use({ storageState: 'auth-owner.json' });

  test('can access all salon settings', async ({ page }) => {
    await page.goto('/settings');
    
    // Owner sees all settings tabs
    await expect(page.locator('text=Billing')).toBeVisible();
    await expect(page.locator('text=Staff Management')).toBeVisible();
    await expect(page.locator('text=Integrations')).toBeVisible();
  });

  test('can manage multiple locations', async ({ page }) => {
    await page.goto('/locations');
    
    await page.click('[data-testid="add-location"]');
    await page.fill('[data-testid="location-name"]', 'Downtown Branch');
    await page.click('[data-testid="save-location"]');
    
    await expect(page.locator('text=Downtown Branch')).toBeVisible();
  });
});
```

### Manager PWA Tests
```typescript
// tests/e2e/manager.spec.ts
test.describe('Manager PWA', () => {
  test.use({ storageState: 'auth-manager.json' });

  test('can manage daily operations', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Manager sees operational dashboard
    await expect(page.locator('[data-testid="today-bookings"]')).toBeVisible();
    await expect(page.locator('[data-testid="staff-on-duty"]')).toBeVisible();
  });

  test('can create and manage bookings', async ({ page }) => {
    await page.goto('/bookings');
    await page.click('[data-testid="new-booking"]');
    
    await page.fill('[data-testid="customer-search"]', 'John Doe');
    await page.click('[data-testid="select-customer"]');
    await page.selectOption('[data-testid="service-select"]', 'Haircut');
    await page.click('[data-testid="confirm-booking"]');
    
    await expect(page.locator('[data-testid="booking-success"]')).toBeVisible();
  });
});
```

### Staff PWA Tests
```typescript
// tests/e2e/staff.spec.ts
test.describe('Staff PWA', () => {
  test.use({ storageState: 'auth-staff.json' });

  test('sees personal schedule', async ({ page }) => {
    await page.goto('/schedule');
    
    // Staff sees only their appointments
    await expect(page.locator('[data-testid="my-appointments"]')).toBeVisible();
    await expect(page.locator('[data-testid="other-staff"]')).toBeHidden();
  });

  test('can check in clients', async ({ page }) => {
    await page.goto('/checkin');
    
    await page.fill('[data-testid="client-code"]', 'ABC123');
    await page.click('[data-testid="checkin-button"]');
    
    await expect(page.locator('[data-testid="checkin-success"]')).toBeVisible();
  });
});
```

### Client PWA Tests
```typescript
// tests/e2e/client.spec.ts
test.describe('Client PWA', () => {
  test.use({ storageState: 'auth-client.json' });

  test('can book appointment', async ({ page }) => {
    await page.goto('/book');
    
    await page.selectOption('[data-testid="service-select"]', 'Haircut');
    await page.click('[data-testid="select-date"]');
    await page.click('[data-testid="time-slot-10am"]');
    await page.click('[data-testid="confirm-booking"]');
    
    await expect(page.locator('[data-testid="booking-confirmation"]')).toBeVisible();
  });

  test('can view booking history', async ({ page }) => {
    await page.goto('/history');
    
    await expect(page.locator('[data-testid="past-bookings"]')).toBeVisible();
  });
});
```

## Token-Efficient Patterns

### Page Object Model (POM)
```typescript
// tests/pages/LoginPage.ts
export class LoginPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.page.fill('[data-testid="email"]', email);
    await this.page.fill('[data-testid="password"]', password);
    await this.page.click('[data-testid="login-button"]');
  }

  async expectLoginSuccess() {
    await expect(this.page).toHaveURL('/dashboard');
  }

  async expectLoginError(message: string) {
    await expect(this.page.locator('[data-testid="error-message"]')).toContainText(message);
  }
}

// Usage in tests
test('login flow', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('owner@salon.com', 'password');
  await loginPage.expectLoginSuccess();
});
```

### Reusable Test Fixtures
```typescript
// tests/fixtures/salon-fixtures.ts
import { test as base } from '@playwright/test';

export const test = base.extend<{
  ownerPage: Page;
  managerPage: Page;
  staffPage: Page;
  clientPage: Page;
}>({
  ownerPage: async ({ browser }, use) => {
    const context = await browser.newContext({ storageState: 'auth-owner.json' });
    const page = await context.newPage();
    await use(page);
    await context.close();
  },
  
  managerPage: async ({ browser }, use) => {
    const context = await browser.newContext({ storageState: 'auth-manager.json' });
    const page = await context.newPage();
    await use(page);
    await context.close();
  },
  
  // ... similar for staff and client
});

// Usage
test('owner can view analytics', async ({ ownerPage }) => {
  await ownerPage.goto('/analytics');
  await expect(ownerPage.locator('[data-testid="revenue-chart"]')).toBeVisible();
});
```

### API Helpers
```typescript
// tests/helpers/api.ts
export async function createBooking(
  request: APIRequestContext,
  bookingData: BookingData
) {
  const response = await request.post('/api/v1/bookings', {
    data: bookingData,
  });
  expect(response.ok()).toBeTruthy();
  return response.json();
}

export async function seedTestData(request: APIRequestContext) {
  // Create test customer
  const customer = await request.post('/api/v1/customers', {
    data: { name: 'Test Customer', phone: '+1234567890' },
  });
  
  // Create test service
  const service = await request.post('/api/v1/services', {
    data: { name: 'Test Service', duration: 60, price: 50 },
  });
  
  return { customer: await customer.json(), service: await service.json() };
}
```

## Configuration Templates

### playwright.config.ts
```typescript
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
    video: 'retain-on-failure',
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

### Environment-Specific Configs
```typescript
// playwright.prod.config.ts
import { defineConfig } from '@playwright/test';
import baseConfig from './playwright.config';

export default defineConfig({
  ...baseConfig,
  use: {
    ...baseConfig.use,
    baseURL: 'https://app.salonflow.app',
  },
  retries: 3,
});
```

## Debugging & Troubleshooting

### Debug Commands
```bash
# Run with debugger
npx playwright test --debug

# Run specific test with headed browser
npx playwright test owner.spec.ts --headed --grep "can access"

# Generate trace for all tests
npx playwright test --trace on

# Open trace viewer
npx playwright show-trace trace.zip
```

### Common Issues

| Issue | Solution |
|-------|----------|
| `browserType.launch: Executable doesn't exist` | Run `npx playwright install` |
| `Timeout waiting for selector` | Increase timeout: `test.setTimeout(60000)` |
| `net::ERR_CONNECTION_REFUSED` | Ensure dev server is running |
| Tests flaky on CI | Increase retries, use `waitForLoadState` |
| Mobile tests fail | Check viewport settings, touch events |

### Debug Script
```typescript
// Add to test for debugging
test('debug test', async ({ page }) => {
  await page.goto('/');
  
  // Pause for manual inspection
  await page.pause();
  
  // Or slow down actions
  await page.click('[data-testid="button"]', { delay: 1000 });
});
```

## CI/CD Integration

### GitHub Actions
```yaml
# .github/workflows/playwright.yml
name: Playwright Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx playwright test
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

## Best Practices

### ✅ Do
- Use `data-testid` attributes for selectors
- Keep tests independent (no shared state)
- Use API helpers to seed data
- Test critical user paths first
- Run tests in parallel where possible
- Use fixtures for common setup

### ❌ Don't
- Rely on CSS classes for selectors
- Test implementation details
- Use hardcoded waits (`waitForTimeout`)
- Share browser contexts between tests
- Test third-party services directly

## References

- Playwright Docs: https://playwright.dev
- PWA Testing: https://web.dev/pwa-checklist/
- Best Practices: https://playwright.dev/docs/best-practices
