/**
 * E2E Tests for Client PWA
 */
import { test, expect } from '@playwright/test';

test.describe('Client PWA - Booking Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display salon name on homepage', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Salon Flow');
  });

  test('should show services list', async ({ page }) => {
    // Navigate to services
    await page.click('text=Services');
    await expect(page.locator('[data-testid="service-card"]')).toHaveCountGreaterThan(0);
  });

  test('should allow booking a service', async ({ page }) => {
    // Select service
    await page.click('[data-testid="service-card"]:first-child');
    
    // Select date
    await page.fill('[data-testid="date-picker"]', '2024-02-20');
    
    // Select time slot
    await page.click('[data-testid="time-slot"]:first-child');
    
    // Confirm booking
    await page.click('text=Confirm Booking');
    
    // Verify success message
    await expect(page.locator('.toast-success')).toBeVisible();
  });

  test('should show booking confirmation with QR code', async ({ page }) => {
    // Navigate to booking confirmation
    await page.goto('/booking/confirmation/test-booking-id');
    
    // Verify QR code is displayed
    await expect(page.locator('[data-testid="qr-code"]')).toBeVisible();
  });
});

test.describe('Client PWA - Authentication', () => {
  test('should allow phone number login', async ({ page }) => {
    await page.goto('/login');
    
    // Enter phone number
    await page.fill('[data-testid="phone-input"]', '+919876543210');
    
    // Request OTP
    await page.click('text=Send OTP');
    
    // Verify OTP input is shown
    await expect(page.locator('[data-testid="otp-input"]')).toBeVisible();
  });
});
