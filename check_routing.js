const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  await page.goto('http://localhost:3000/login');
  await page.waitForTimeout(2000);
  
  console.log('FINAL URL:', page.url());
  
  const mainContent = await page.evaluate(() => {
    const main = document.querySelector('main');
    return main ? main.innerHTML : 'NO MAIN TAG FOUND';
  });
  
  console.log('\nMAIN TAG CONTENT:');
  console.log(mainContent.trim() || 'MAIN TAG IS EMPTY');
  
  await browser.close();
})();
