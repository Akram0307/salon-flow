const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  try {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
    
    const url = page.url();
    const mainHtml = await page.evaluate(() => {
      const main = document.querySelector('main');
      return main ? main.innerHTML : 'NO MAIN TAG';
    });
    
    fs.writeFileSync('/tmp/main_content.txt', `FINAL URL: ${url}\n\nMAIN HTML:\n${mainHtml}`);
    await browser.close();
  } catch (e) {
    fs.writeFileSync('/tmp/main_content.txt', `ERROR: ${e.message}`);
  }
})();
