const { chromium } = require('playwright');

(async () => {
  console.log('Launching browser...');
  const browser = await chromium.launch();
  const context = await browser.newContext();
  
  // --- MANAGER PWA ---
  console.log('\n--- DEBUGGING MANAGER PWA ---');
  const managerPage = await context.newPage();
  managerPage.on('console', msg => {
    if (msg.type() === 'error') console.log('Manager Console Error:', msg.text());
  });
  managerPage.on('pageerror', err => console.log('Manager Page Error:', err.message));
  
  try {
    await managerPage.goto('https://salon-flow-manager-rgvcleapsa-el.a.run.app/', { waitUntil: 'networkidle' });
    await managerPage.waitForTimeout(2000);
    const content = await managerPage.content();
    if (content.includes('id="root"></div>') || content.includes('id="root"></div')) {
      console.log('Manager PWA rendered a blank screen (root is empty).');
    } else {
      console.log('Manager PWA rendered successfully.');
    }
  } catch (e) {
    console.log('Manager Navigation Error:', e.message);
  }

  // --- OWNER PWA ---
  console.log('\n--- DEBUGGING OWNER PWA ---');
  const ownerPage = await context.newPage();
  ownerPage.on('console', msg => {
    if (msg.type() === 'error') console.log('Owner Console Error:', msg.text());
  });
  ownerPage.on('pageerror', err => console.log('Owner Page Error:', err.message));
  
  try {
    console.log('Navigating to /login...');
    await ownerPage.goto('https://salon-flow-owner-rgvcleapsa-el.a.run.app/login', { waitUntil: 'networkidle' });
    await ownerPage.waitForTimeout(2000);
    console.log('Owner PWA URL after navigating to /login:', ownerPage.url());
    
    const loginForm = await ownerPage.$('[data-testid="login-form"]');
    if (loginForm) {
      console.log('Login form found in DOM.');
    } else {
      console.log('Login form NOT found in DOM.');
    }
  } catch (e) {
    console.log('Owner Navigation Error:', e.message);
  }

  await browser.close();
  console.log('\nDone.');
})();
