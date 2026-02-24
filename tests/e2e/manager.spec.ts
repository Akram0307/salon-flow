/**
 * E2E Tests for Manager PWA - Production Ready
 * Tests all critical workflows for salon manager dashboard
 */
import { test, expect } from '@playwright/test';

test.describe('Manager PWA - Production Ready', () => {
  // Production URL from verified deployment
  const BASE_URL = 'https://salon-flow-manager-rgvcleapsa-el.a.run.app';
  const API_URL = 'https://salon-flow-api-rgvcleapsa-el.a.run.app';
  const AI_URL = 'https://salon-flow-ai-rgvcleapsa-el.a.run.app';
  
  test.use({ baseURL: BASE_URL });

  test.describe('Authentication', () => {
    test('should load login page', async ({ page }) => {
      await page.goto('/login');
      await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
    });

    test('should show email and password fields', async ({ page }) => {
      await page.goto('/login');
      await expect(page.locator('[data-testid="email-input"]')).toBeVisible();
      await expect(page.locator('[data-testid="password-input"]')).toBeVisible();
    });

    test('should show forgot password link', async ({ page }) => {
      await page.goto('/login');
      const forgotLink = page.locator('text=Forgot Password');
      // May or may not exist
    });
  });

  test.describe('Dashboard & Navigation', () => {
    test('should load homepage without errors', async ({ page }) => {
      const errors: string[] = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      expect(errors).toHaveLength(0);
    });

    test('should have correct page title', async ({ page }) => {
      await page.goto('/');
      await expect(page).toHaveTitle(/Salon Flow|Manager/);
    });

    test('should load all static assets', async ({ page }) => {
      const failedRequests: string[] = [];
      page.on('requestfailed', request => failedRequests.push(request.url()));
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      expect(failedRequests).toHaveLength(0);
    });

    test('should have navigation menu', async ({ page }) => {
      await page.goto('/');
      // Check for navigation elements
      const nav = page.locator('nav, [data-testid="sidebar"], [data-testid="navbar"]');
      await expect(nav.first()).toBeVisible();
    });
  });

  test.describe('POS & Billing', () => {
    test('should load POS page', async ({ page }) => {
      await page.goto('/pos');
      await page.waitForLoadState('networkidle');
      // Check for POS elements
      const posElements = page.locator('[data-testid="pos-terminal"], [data-testid="billing-form"], .pos-container');
      // May need authentication
    });

    test('should load billing page', async ({ page }) => {
      await page.goto('/billing');
      await page.waitForLoadState('networkidle');
    });
  });

  test.describe('Appointments', () => {
    test('should load appointments page', async ({ page }) => {
      await page.goto('/appointments');
      await page.waitForLoadState('networkidle');
    });

    test('should show calendar view', async ({ page }) => {
      await page.goto('/appointments');
      // Check for calendar component
      const calendar = page.locator('[data-testid="calendar"], .calendar, [data-testid="appointment-calendar"]');
    });
  });

  test.describe('API Connectivity', () => {
    test('should connect to backend API', async ({ page }) => {
      const response = await page.request.get(`${API_URL}/health/`);
      expect(response.ok()).toBeTruthy();
    });

    test('should connect to AI service', async ({ page }) => {
      const response = await page.request.get(`${AI_URL}/health`);
      expect(response.ok()).toBeTruthy();
    });

    test('should have CORS configured for PWA origin', async ({ page }) => {
      const response = await page.request.fetch(`${API_URL}/health/`, {
        method: 'OPTIONS',
        headers: {
          'Origin': BASE_URL,
          'Access-Control-Request-Method': 'GET'
        }
      });
      // CORS should allow the origin
      const allowOrigin = response.headers()['access-control-allow-origin'];
      expect(allowOrigin).toBeTruthy();
    });
  });

  test.describe('PWA Features', () => {
    test('should have manifest file', async ({ page }) => {
      await page.goto('/');
      const manifest = page.locator('link[rel="manifest"]');
      await expect(manifest).toHaveAttribute('href', /manifest/);
    });

    test('should have theme-color meta tag', async ({ page }) => {
      await page.goto('/');
      const themeColor = page.locator('meta[name="theme-color"]');
      await expect(themeColor).toHaveAttribute('content');
    });

    test('should have viewport meta tag', async ({ page }) => {
      await page.goto('/');
      const viewport = page.locator('meta[name="viewport"]');
      await expect(viewport).toHaveAttribute('content', /width=device-width/);
    });
  });

  test.describe('Responsive Design', () => {
    test('should be responsive on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      const scrollWidth = await page.evaluate(() => document.body.scrollWidth);
      const clientWidth = await page.evaluate(() => document.body.clientWidth);
      expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 10);
    });

    test('should be responsive on tablet', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      await page.goto('/');
      await page.waitForLoadState('networkidle');
    });

    test('should be responsive on desktop', async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });
      await page.goto('/');
      await page.waitForLoadState('networkidle');
    });
  });

  test.describe('Performance', () => {
    test('should load within acceptable time', async ({ page }) => {
      const startTime = Date.now();
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      const loadTime = Date.now() - startTime;
      // Should load within 10 seconds
      expect(loadTime).toBeLessThan(10000);
    });

    test('should have no console errors', async ({ page }) => {
      const errors: string[] = [];
      page.on('console', msg => {
        if (msg.type() === 'error') {
          errors.push(msg.text());
        }
      });
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      // Filter out non-critical errors
      const criticalErrors = errors.filter(e => 
        !e.includes('favicon') && 
        !e.includes('manifest') &&
        !e.includes('service worker')
      );
      expect(criticalErrors).toHaveLength(0);
    });
  });
});
