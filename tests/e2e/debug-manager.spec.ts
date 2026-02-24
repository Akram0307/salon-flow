import { test } from '@playwright/test';

test('capture manager errors', async ({ page }) => {
  const errors: string[] = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('CONSOLE ERROR:', msg.text());
      errors.push(msg.text());
    }
  });
  page.on('pageerror', err => {
    console.log('PAGE ERROR:', err.message);
    errors.push(err.message);
  });
  
  console.log('Navigating to Manager PWA...');
  await page.goto('https://salon-flow-manager-rgvcleapsa-el.a.run.app/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  
  const content = await page.content();
  if (content.includes('id="root"></div>') || content.includes('id="root"></div')) {
    console.log('RESULT: Root element is empty (Blank Screen)');
  } else {
    console.log('RESULT: App rendered successfully');
  }
});
