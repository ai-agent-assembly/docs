import { mkdir, writeFile } from 'node:fs/promises';

const { PLAYWRIGHT_MODULE, SEARCH_AGGREGATE_URL, SEARCH_EVIDENCE_DIR } = process.env;
if (!PLAYWRIGHT_MODULE || !SEARCH_AGGREGATE_URL || !SEARCH_EVIDENCE_DIR) {
  throw new Error('Set PLAYWRIGHT_MODULE, SEARCH_AGGREGATE_URL, SEARCH_EVIDENCE_DIR');
}
const { chromium } = await import(PLAYWRIGHT_MODULE);
await mkdir(SEARCH_EVIDENCE_DIR, { recursive: true });
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
const page = await context.newPage();
const requests = [];
let origin;
for (const name of ['request', 'response', 'requestfinished']) {
  page.on(name, (event) => {
    const url = event.url();
    if (origin && url.includes('/pagefind/')) {
      requests.push({ ms: Math.round(performance.now() - origin), event: name,
        asset: url.replace(/^.*\/pagefind\//, '') });
    }
  });
}
await page.addInitScript(() => {
  window.__searchTrace = [];
  document.addEventListener('DOMContentLoaded', () => {
    let previous = '';
    setInterval(() => {
      const status = document.querySelector('.aa-search__status')?.textContent || '';
      const count = document.querySelectorAll('.aa-search__group > a').length;
      const value = `${status}|${count}`;
      if (value !== previous) {
        previous = value;
        window.__searchTrace.push({ ms: Math.round(performance.now()), status, count });
      }
    }, 50);
  });
});
try {
  await page.goto(SEARCH_AGGREGATE_URL);
  await page.getByRole('button', { name: 'Search all docs…' }).click();
  const modal = page.locator('dialog.aa-search__modal');
  const input = modal.getByRole('searchbox', { name: 'Search all docs' });
  origin = performance.now();
  const browserOrigin = await page.evaluate(() => performance.now());
  await input.fill('policy gateway');
  await modal.locator('.aa-search__group > a').first().waitFor({ timeout: 30000 });
  const firstMatchMs = Math.round(performance.now() - origin);
  await page.screenshot({ path: `${SEARCH_EVIDENCE_DIR}/first-match.png` });
  const pageEvents = await page.evaluate(() => window.__searchTrace);
  const result = { firstMatchMs, browserOrigin: Math.round(browserOrigin), requests, pageEvents };
  await writeFile(`${SEARCH_EVIDENCE_DIR}/timing.json`, JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result, null, 2));
} finally {
  await context.close();
  await browser.close();
}
