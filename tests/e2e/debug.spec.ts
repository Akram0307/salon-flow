import { test } from '@playwright/test';

test('Debug Manager PWA', async ({ page }) => {
  page.on('console', msg => {
    if (msg.type() === 'error' || msg.type() === 'warning') {
      console.log(`MANAGER CONSOLE [${msg.type()}]: ${msg.text()}`);
    }
  });
  page.on('pageerror', err => console.log(`MANAGER PAGE ERROR: ${err.message}`));
  
  console.log('Navigating to Manager PWA...');
  await page.goto('https://salon-flow-manager-rgvcleapsa-el.a.run.app/');
  await page.waitForTimeout(3000);
  const content = await page.content();
  console.log('Manager Root contains content:', !content.includes('id="root"></div>'));
});

test('Debug Owner PWA', async ({ page }) => {
  console.log('Navigating to Owner PWA /login...');
  await page.goto('https://salon-flow-owner-rgvcleapsa-el.a.run.app/login');
  await page.waitForTimeout(3000);
  console.log('OWNER FINAL URL:', page.url());
  
  const content = await page.content();
  console.log('OWNER HAS LOGIN FORM:', content.includes('data-testid="login-form"'));
});
