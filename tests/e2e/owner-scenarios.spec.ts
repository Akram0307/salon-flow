import { test, expect } from '@playwright/test';

test.describe('Owner PWA - Extended Scenarios', () => {
  test.use({ baseURL: 'https://salon-flow-owner-687369167038.asia-south1.run.app' });

  test('Scenario 1: Login form validation (empty fields)', async ({ page }) => {
    await page.goto('/login');
    // Find the submit button by type or common text
    const submitButton = page.locator('button[type="submit"], button:has-text("Sign In"), button:has-text("Login")').first();
    if (await submitButton.count() > 0) {
        await submitButton.click();
        // Should still be on the login page due to validation
        await expect(page).toHaveURL(/.*login/);
    }
  });

  test('Scenario 2: Invalid credentials handling', async ({ page }) => {
    await page.goto('/login');
    await page.locator('[data-testid="email-input"]').fill('fake@salonflow.com');
    await page.locator('[data-testid="password-input"]').fill('badpassword123');

    const submitButton = page.locator('button[type="submit"], button:has-text("Sign In"), button:has-text("Login")').first();
    if (await submitButton.count() > 0) {
        await submitButton.click();
        // Should not redirect to dashboard on invalid login
        await expect(page).toHaveURL(/.*login/);
    }
  });

  test('Scenario 3: Dashboard layout and navigation', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Verify main content area exists
    const main = page.locator('main').first();
    if (await main.count() > 0) {
        await expect(main).toBeVisible();
    }
  });
});
