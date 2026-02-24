import { test, expect } from '@playwright/test';

test.describe('Owner PWA - Core Workflows', () => {
  test.use({ baseURL: 'https://salon-flow-owner-687369167038.asia-south1.run.app' });

  test('Workflow: Bookings Management', async ({ page }) => {
    await page.goto('/bookings');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/.*bookings/);
    // Verify page didn't crash by checking for main container
    await expect(page.locator('main').first()).toBeVisible();
  });

  test('Workflow: Customer Management', async ({ page }) => {
    await page.goto('/customers');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/.*customers/);
    await expect(page.locator('main').first()).toBeVisible();
  });

  test('Workflow: Staff Management', async ({ page }) => {
    await page.goto('/staff');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/.*staff/);
    await expect(page.locator('main').first()).toBeVisible();
  });

  test('Workflow: Analytics & Reporting', async ({ page }) => {
    await page.goto('/analytics');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/.*analytics/);
    await expect(page.locator('main').first()).toBeVisible();
  });

  test('Workflow: Settings & Configuration', async ({ page }) => {
    // General Settings
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/.*settings/);
    await expect(page.locator('main').first()).toBeVisible();

    // Billing Settings
    await page.goto('/settings/billing');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/.*settings\/billing/);
    await expect(page.locator('main').first()).toBeVisible();

    // Integrations Settings
    await page.goto('/settings/integrations');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/.*settings\/integrations/);
    await expect(page.locator('main').first()).toBeVisible();
  });
});
