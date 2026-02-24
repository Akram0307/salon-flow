import { test, expect } from '@playwright/test';

test.describe('Owner PWA - Deep Interactive Workflows', () => {
  test.use({ baseURL: 'https://salon-flow-owner-687369167038.asia-south1.run.app' });

  test('Bookings Workflow: Can interact with booking controls', async ({ page }) => {
    await page.goto('/bookings');
    await page.waitForLoadState('networkidle');

    // Look for common 'Add' or 'New' buttons in the bookings view
    const addButton = page.getByRole('button', { name: /add|new|create/i }).first();
    if (await addButton.count() > 0) {
        await addButton.click();
        // Verify a modal, dialog, or form appears
        const dialog = page.getByRole('dialog').or(page.locator('form')).first();
        await expect(dialog).toBeVisible();

        // Close it if there's a cancel/close button to leave state clean
        const closeBtn = dialog.getByRole('button', { name: /cancel|close/i }).first();
        if (await closeBtn.count() > 0) await closeBtn.click();
    }
  });

  test('Customers Workflow: Can search and open add customer form', async ({ page }) => {
    await page.goto('/customers');
    await page.waitForLoadState('networkidle');

    // Test Search functionality
    const searchInput = page.getByPlaceholder(/search/i).first();
    if (await searchInput.count() > 0) {
        await searchInput.fill('Jane Doe');
        await expect(searchInput).toHaveValue('Jane Doe');
    }

    // Test Add Customer functionality
    const addButton = page.getByRole('button', { name: /add|new/i }).first();
    if (await addButton.count() > 0) {
        await addButton.click();
        const dialog = page.getByRole('dialog').or(page.locator('form')).first();
        await expect(dialog).toBeVisible();
    }
  });

  test('Staff Workflow: Can interact with staff management', async ({ page }) => {
    await page.goto('/staff');
    await page.waitForLoadState('networkidle');

    const addButton = page.getByRole('button', { name: /add|new/i }).first();
    if (await addButton.count() > 0) {
        await addButton.click();
        const dialog = page.getByRole('dialog').or(page.locator('form')).first();
        await expect(dialog).toBeVisible();
    }
  });

  test('Settings Workflow: Can navigate nested settings tabs', async ({ page }) => {
    await page.goto('/settings');
    await page.waitForLoadState('networkidle');

    // Navigate to Billing
    const billingLink = page.getByRole('link', { name: /billing/i }).first();
    if (await billingLink.count() > 0) {
        await billingLink.click();
        await expect(page).toHaveURL(/.*billing/);
        await expect(page.locator('main')).toBeVisible();
    }

    // Navigate to Integrations
    const integrationsLink = page.getByRole('link', { name: /integration/i }).first();
    if (await integrationsLink.count() > 0) {
        await integrationsLink.click();
        await expect(page).toHaveURL(/.*integration/);
        await expect(page.locator('main')).toBeVisible();
    }
  });
});
