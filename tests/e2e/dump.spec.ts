import { test } from '@playwright/test';
import fs from 'fs';

test('dump dom and logs', async ({ page }) => {
  const logs: string[] = [];
  page.on('console', msg => logs.push(`CONSOLE [${msg.type()}]: ${msg.text()}`));
  page.on('pageerror', err => logs.push(`PAGE ERROR: ${err.message}`));

  await page.goto('/login');
  await page.waitForTimeout(2000);

  const html = await page.content();
  const url = page.url();
  
  fs.writeFileSync('/a0/usr/workdir/dom_dump.html', `<!-- URL: ${url} -->\n` + html);
  fs.writeFileSync('/a0/usr/workdir/page_logs.txt', logs.join('\n'));
});
