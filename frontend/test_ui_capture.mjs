import { chromium } from 'playwright';
import fs from 'fs';

async function run() {
  console.log('Launching Chromium...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    ignoreHTTPSErrors: true
  });
  const page = await context.newPage();

  console.log('Navigating to https://sharegy.de ...');
  await page.goto('https://sharegy.de', { waitUntil: 'networkidle', timeout: 30000 });
  console.log('Page title:', await page.title());

  const screenshotPath = 'C:/Users/Ruediger/.gemini/antigravity-ide/brain/d8caeb27-bd67-41d4-9bee-6ed8a4fc7667/sharegy_landing.png';
  await page.screenshot({ path: screenshotPath, fullPage: true });
  console.log('Screenshot saved to:', screenshotPath);

  await browser.close();
  console.log('Done!');
}

run().catch(err => {
  console.error('Error during capture:', err);
  process.exit(1);
});
