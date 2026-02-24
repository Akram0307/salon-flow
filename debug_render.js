const { chromium } = require('playwright');

(async () => {
  try {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    
    console.log('Navigating to /login...');
    await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
    
    console.log('Current URL:', page.url());
    
    const mainHtml = await page.$eval('main', el => el.innerHTML).catch(e => 'Error finding main: ' + e.message);
    console.log('\n--- MAIN CONTENT ---');
    console.log(mainHtml.trim() ? mainHtml.substring(0, 1000) : 'MAIN IS EMPTY');
    
    await page.screenshot({ path: '/a0/usr/workdir/login_debug.png' });
    console.log('\nScreenshot saved to /a0/usr/workdir/login_debug.png');
    
    await browser.close();
  } catch (err) {
    console.error('Script failed:', err);
  }
})();
