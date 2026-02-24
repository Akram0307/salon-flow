import { test, expect } from '@playwright/test';

test('verify login page routing', async ({ page }) => {
  console.log('Starting navigation to /login');
  await page.goto('http://localhost:3000/login');
  await page.waitForTimeout(2000);
  
  const currentUrl = page.url();
  console.log('FINAL_URL: ' + currentUrl);
  
  // Assert we are still on the login page
  expect(currentUrl).toContain('/login');
});
