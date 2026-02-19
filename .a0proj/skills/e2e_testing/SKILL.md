# E2E Testing Skill

## Overview
Implement end-to-end testing for PWAs using Playwright.

## Test Structure
```
e2e/
├── booking.spec.ts
├── auth.spec.ts
├── staff-workflow.spec.ts
└── customer-journey.spec.ts
```

## Booking Flow Test
```typescript
import { test, expect } from '@playwright/test'

test('complete booking flow', async ({ page }) => {
  await page.goto('https://client.salonsaas.com')

  // Start conversation
  await page.fill('[data-testid="chat-input"]', 'Book a haircut for tomorrow')
  await page.press('[data-testid="chat-input"]', 'Enter')

  // Wait for response
  await expect(page.locator('.message.assistant')).toBeVisible()

  // Select time slot
  await page.click('[data-testid="slot-15:00"]')

  // Confirm booking
  await page.click('[data-testid="confirm-booking"]')

  // Verify confirmation
  await expect(page.locator('.booking-confirmed')).toBeVisible()
})
```

## PWA Tests
```typescript
test('offline functionality', async ({ page, context }) => {
  await page.goto('https://staff.salonsaas.com')
  await context.setOffline(true)
  await expect(page.locator('.offline-indicator')).toBeVisible()
})
```
