import { test, expect } from '@playwright/test';
import fs from 'fs';

test('debug login page state', async ({ page }) => {
  await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  
  const finalUrl = page.url();
  const htmlContent = await page.content();
  
  fs.writeFileSync('/a0/usr/workdir/cli_debug_url.txt', finalUrl);
  fs.writeFileSync('/a0/usr/workdir/cli_debug_html.txt', htmlContent);
  
  // Assert to see if it fails in the CLI output
  expect(finalUrl).toContain('/login');
});
