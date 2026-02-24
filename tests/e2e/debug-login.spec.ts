import { test } from '@playwright/test';
import fs from 'fs';

test('debug login page render', async ({ page }) => {
  // Navigate to login page
  await page.goto('/login', { waitUntil: 'networkidle' });
  
  // Wait a moment for any React redirects to occur
  await page.waitForTimeout(2000);
  
  const finalUrl = page.url();
  
  // Extract the main tag content
  const mainHtml = await page.locator('main').innerHTML().catch(e => 'Error finding main: ' + e.message);
  
  // Write results to a file so we can read it reliably
  const output = `FINAL URL: ${finalUrl}\n\nMAIN HTML:\n${mainHtml}`;
  fs.writeFileSync('/tmp/playwright_debug.txt', output);
});
