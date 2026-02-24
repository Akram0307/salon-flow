const { chromium } = require('playwright');
(async () => {
  try {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    await page.goto('http://localhost:3000/login');
    await page.waitForTimeout(2000);
    
    console.log('URL:', page.url());
    
    const mainHtml = await page.evaluate(() => {
      const main = document.querySelector('main');
      return main ? main.innerHTML : 'NO MAIN TAG';
    });
    
    console.log('MAIN_HTML_START');
    console.log(mainHtml);
    console.log('MAIN_HTML_END');
    
    await browser.close();
  } catch (e) {
    console.error(e);
  }
})();
