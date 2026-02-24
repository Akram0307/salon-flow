const { chromium } = require('playwright');

(async () => {
  console.log('Launching browser...');
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('BROWSER CONSOLE:', msg.type(), msg.text()));
  page.on('pageerror', err => console.log('BROWSER ERROR:', err.message));
  
  console.log('Navigating to /login...');
  const response = await page.goto('http://localhost:3000/login');
  console.log('Response status:', response.status());
  
  await page.waitForTimeout(2000);
  
  const bodyHTML = await page.evaluate(() => document.body.innerHTML);
  console.log('\n--- RENDERED HTML ---');
  console.log(bodyHTML.substring(0, 1000) + (bodyHTML.length > 1000 ? '... [TRUNCATED]' : ''));
  
  await browser.close();
})();
