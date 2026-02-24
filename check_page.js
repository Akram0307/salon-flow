const { chromium } = require('playwright');
(async () => {
  try {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    
    page.on('console', msg => console.log('BROWSER LOG:', msg.text()));
    page.on('pageerror', err => console.log('BROWSER ERROR:', err.message));
    
    console.log('Navigating to /login...');
    await page.goto('http://localhost:3000/login');
    await page.waitForTimeout(2000);
    
    const body = await page.evaluate(() => document.body.innerHTML);
    console.log('\nRENDERED BODY HTML:');
    console.log(body.trim() === '<div id="root"></div>' ? 'BLANK SCREEN (React Crashed)' : body.substring(0, 500) + '...');
    
    await browser.close();
  } catch (e) {
    console.error('SCRIPT ERROR:', e);
  }
})();
