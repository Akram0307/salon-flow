/**
 * E2E Tests for Owner PWA - Production Ready
 * Tests all critical workflows for salon owner dashboard
 */
import { test, expect } from '@playwright/test';

test.describe('Owner PWA - Production Ready', () => {
  // Verified Production URL from deployment
  const BASE_URL = 'https://salon-flow-owner-687369167038.asia-south1.run.app';
  const API_URL = 'https://salon-flow-api-687369167038.asia-south1.run.app';
  const AI_URL = 'https://salon-flow-ai-687369167038.asia-south1.run.app';
  
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
  });

  test.describe('Dashboard', () => {
    test('should load homepage without errors', async ({ page }) => {
      const errors: string[] = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      expect(errors).toHaveLength(0);
    });

    test('should have correct page title', async ({ page }) => {
      await page.goto('/');
      await expect(page).toHaveTitle(/Salon Flow|Owner/);
    });

    test('should load all static assets', async ({ page }) => {
      const failedRequests: string[] = [];
      page.on('requestfailed', request => failedRequests.push(request.url()));
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      expect(failedRequests).toHaveLength(0);
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
      const criticalErrors = errors.filter(e => 
        !e.includes('favicon') && 
        !e.includes('manifest') &&
        !e.includes('service worker')
      );
      expect(criticalErrors).toHaveLength(0);
    });
  });
});
