import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const ARTIFACT_DIR = 'C:/Users/Ruediger/.gemini/antigravity-ide/brain/d8caeb27-bd67-41d4-9bee-6ed8a4fc7667';
const SCREENSHOT_DIR = path.join(ARTIFACT_DIR, 'ui_inspection_screenshots');

if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

const PUBLIC_PAGES = [
  { name: '01_landing', url: 'https://sharegy.de/' },
  { name: '02_login', url: 'https://sharegy.de/login' },
  { name: '03_join', url: 'https://sharegy.de/join' },
  { name: '04_impressum', url: 'https://sharegy.de/impressum' },
  { name: '05_datenschutz', url: 'https://sharegy.de/datenschutz' },
  { name: '06_agb', url: 'https://sharegy.de/agb' },
  { name: '07_widerruf', url: 'https://sharegy.de/widerruf' },
];

const APP_PAGES = [
  { name: '10_app_dashboard', url: 'https://sharegy.de/app/dashboard' },
  { name: '11_app_devices', url: 'https://sharegy.de/app/devices' },
  { name: '12_app_energy', url: 'https://sharegy.de/app/energy' },
  { name: '13_app_producers', url: 'https://sharegy.de/app/producers' },
  { name: '14_app_solarforecast', url: 'https://sharegy.de/app/solarforecast' },
  { name: '15_app_metrics', url: 'https://sharegy.de/app/metrics' },
  { name: '16_app_structure', url: 'https://sharegy.de/app/structure' },
  { name: '17_app_alerts', url: 'https://sharegy.de/app/alerts' },
  { name: '18_app_tariff', url: 'https://sharegy.de/app/tariff' },
  { name: '19_app_interfaces', url: 'https://sharegy.de/app/interfaces' },
  { name: '20_app_status', url: 'https://sharegy.de/app/status' },
  { name: '21_app_profile', url: 'https://sharegy.de/app/profile' },
  { name: '22_app_billing', url: 'https://sharegy.de/app/billing' },
  { name: '23_app_help', url: 'https://sharegy.de/app/help' },
  { name: '24_app_support', url: 'https://sharegy.de/app/support' },
  { name: '25_app_communities', url: 'https://sharegy.de/app/communities' },
  { name: '26_app_tenant', url: 'https://sharegy.de/app/tenant' },
  { name: '27_app_admin_dashboard', url: 'https://sharegy.de/app/admin/dashboard' },
  { name: '28_app_admin_tracking', url: 'https://sharegy.de/app/admin/tracking' },
  { name: '29_app_admin_communities', url: 'https://sharegy.de/app/admin/communities' },
];

async function inspectAll() {
  console.log('Starting full UI inspection...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    ignoreHTTPSErrors: true
  });
  const page = await context.newPage();

  const report = [];

  page.on('pageerror', err => {
    console.error(`[Page Error] ${page.url()}:`, err.message);
    report.push({ url: page.url(), type: 'PAGE_ERROR', message: err.message, stack: err.stack });
  });

  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.warn(`[Console Error] ${page.url()}:`, msg.text());
      report.push({ url: page.url(), type: 'CONSOLE_ERROR', message: msg.text() });
    }
  });

  // 1. Inspect Public Pages
  console.log('--- Inspecting Public Pages ---');
  for (const item of PUBLIC_PAGES) {
    try {
      console.log(`Navigating to ${item.name} (${item.url})...`);
      await page.goto(item.url, { waitUntil: 'networkidle', timeout: 20000 });
      await page.waitForTimeout(1000);
      const filePath = path.join(SCREENSHOT_DIR, `${item.name}.png`);
      await page.screenshot({ path: filePath, fullPage: true });
      console.log(`  Saved screenshot: ${item.name}.png`);
    } catch (e) {
      console.error(`  Failed on ${item.name}:`, e.message);
      report.push({ url: item.url, type: 'NAVIGATION_ERROR', message: e.message });
    }
  }

  // 2. Perform Demo Login
  console.log('--- Logging in via Demo endpoint ---');
  try {
    await page.goto('https://sharegy.de/api/demo/', { waitUntil: 'networkidle', timeout: 20000 });
    console.log('Logged in successfully. Current URL:', page.url());
  } catch (e) {
    console.error('Demo login failed:', e.message);
  }

  // 3. Inspect App Pages
  console.log('--- Inspecting App Pages ---');
  for (const item of APP_PAGES) {
    try {
      console.log(`Navigating to ${item.name} (${item.url})...`);
      await page.goto(item.url, { waitUntil: 'networkidle', timeout: 20000 });
      await page.waitForTimeout(1500); // Allow charts/animations to settle
      const filePath = path.join(SCREENSHOT_DIR, `${item.name}.png`);
      await page.screenshot({ path: filePath, fullPage: true });
      console.log(`  Saved screenshot: ${item.name}.png`);
    } catch (e) {
      console.error(`  Failed on ${item.name}:`, e.message);
      report.push({ url: item.url, type: 'NAVIGATION_ERROR', message: e.message });
    }
  }

  // Write report JSON
  fs.writeFileSync(
    path.join(ARTIFACT_DIR, 'ui_inspection_report.json'),
    JSON.stringify(report, null, 2),
    'utf-8'
  );

  await browser.close();
  console.log('Full UI Inspection completed!');
}

inspectAll().catch(err => {
  console.error('Fatal inspection error:', err);
  process.exit(1);
});
