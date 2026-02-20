/**
 * E2E Tests for Staff PWA
 */
import { test, expect } from '@playwright/test';

test.describe('Staff PWA - Daily Operations', () => {
  test.use({ baseURL: 'http://localhost:3001' });

  test.beforeEach(async ({ page }) => {
    // Login as staff
    await page.goto('/login');
    await page.fill('[data-testid="staff-id"]', 'STAFF001');
    await page.fill('[data-testid="pin"]', '1234');
    await page.click('text=Login');
  });

  test('should show today\'s appointments', async ({ page }) => {
    await expect(page.locator('[data-testid="appointment-list"]')).toBeVisible();
  });

  test('should allow checking in customer via QR', async ({ page }) => {
    // Navigate to check-in
    await page.click('text=Check In');
    
    // Scan QR (simulated)
    await page.click('[data-testid="scan-qr"]');
    
    // Verify customer details shown
    await expect(page.locator('[data-testid="customer-info"]')).toBeVisible();
  });

  test('should allow adding upsell service', async ({ page }) => {
    // Select active appointment
    await page.click('[data-testid="appointment-card"]:first-child');
    
    // Add service
    await page.click('text=Add Service');
    await page.click('[data-testid="service-item"]:first-child');
    
    // Verify service added
    await expect(page.locator('.service-added')).toBeVisible();
  });
});
