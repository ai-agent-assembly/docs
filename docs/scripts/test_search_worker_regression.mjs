import assert from 'node:assert/strict';
import { mkdir, rename, writeFile } from 'node:fs/promises';

const { PLAYWRIGHT_MODULE, SEARCH_AGGREGATE_URL, SEARCH_EVIDENCE_DIR } = process.env;
if (!PLAYWRIGHT_MODULE || !SEARCH_AGGREGATE_URL || !SEARCH_EVIDENCE_DIR) {
  throw new Error('Set PLAYWRIGHT_MODULE, SEARCH_AGGREGATE_URL, SEARCH_EVIDENCE_DIR');
}
const { chromium, firefox, webkit } = await import(PLAYWRIGHT_MODULE);
await mkdir(SEARCH_EVIDENCE_DIR, { recursive: true });
const results = [];

for (const [engineName, engine] of [['chromium', chromium], ['firefox', firefox], ['webkit', webkit]]) {
  const browser = await engine.launch({ headless: true });
  try {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 },
      reducedMotion: 'reduce', recordVideo: { dir: SEARCH_EVIDENCE_DIR, size: { width: 390, height: 844 } } });
    const page = await context.newPage();
    await page.goto(SEARCH_AGGREGATE_URL);
    const trigger = page.getByRole('button', { name: 'Search all docs…' });
    await trigger.click();
    const dialog = page.locator('dialog.aa-search__modal');
    const input = dialog.getByRole('searchbox', { name: 'Search all docs' });
    await input.fill('network.allowlist');
    await dialog.getByText('Matches all search terms: 3.', { exact: true }).waitFor({ timeout: 30000 });
    assert.match(await dialog.locator('.aa-search__group > a').first().getAttribute('href'),
      /\/core\/latest\/policy-reference\.html$/);
    await page.waitForTimeout(350);
    await page.screenshot({ path: `${SEARCH_EVIDENCE_DIR}/${engineName}-identifier.png` });
    await page.keyboard.press('Escape');
    assert.equal(await dialog.evaluate((element) => element.open), false);
    assert.equal(await trigger.evaluate((element) => document.activeElement === element), true);
    results.push({ engine: engineName, identifier: true, escapeFocus: true });
    await context.close();
    await rename(await page.video().path(), `${SEARCH_EVIDENCE_DIR}/${engineName}-mobile-sequence.webm`);
  } finally { await browser.close(); }
}

const browser = await chromium.launch({ headless: true });
try {
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 },
    recordVideo: { dir: SEARCH_EVIDENCE_DIR, size: { width: 1280, height: 800 } } });
  const page = await context.newPage();
  let largeFragmentSeen = false;
  context.on('response', (response) => {
    if (response.url().includes('/pagefind/fragment/')
      && Number(response.headers()['content-length'] || 0) > 500000) largeFragmentSeen = true;
  });
  await page.goto(SEARCH_AGGREGATE_URL);
  const trigger = page.getByRole('button', { name: 'Search all docs…' });
  await trigger.click();
  const dialog = page.locator('dialog.aa-search__modal');
  const input = dialog.getByRole('searchbox', { name: 'Search all docs' });
  const firstLink = dialog.locator('.aa-search__group > a').first();
  const largeFragment = (response) => response.url().includes('/pagefind/fragment/')
    && Number(response.headers()['content-length'] || 0) > 500000;

  const firstLarge = context.waitForEvent('response', { predicate: largeFragment, timeout: 30000 });
  await input.fill('policy gateway');
  await firstLink.waitFor({ timeout: 30000 });
  await firstLarge;
  await page.waitForFunction(() => {
    const status = document.querySelector('.aa-search__status')?.textContent || '';
    return status.includes('found so far') && status.includes('Still checking');
  });
  await page.waitForTimeout(150);
  assert.equal(largeFragmentSeen, true, 'the giant combined-book fragment was actually requested');
  await firstLink.focus();
  const firstHref = await firstLink.getAttribute('href');
  await dialog.getByText('More results remain to check.', { exact: false }).waitFor({ timeout: 60000 });
  assert.equal(await firstLink.getAttribute('href'), firstHref);
  assert.equal(await firstLink.evaluate((element) => document.activeElement === element), true);
  const beforeMore = await dialog.locator('.aa-search__group > a').count();
  await dialog.getByRole('button', { name: 'Load more matches' }).click();
  await page.waitForFunction((prior) => document.querySelectorAll('.aa-search__group > a').length > prior,
    beforeMore, { timeout: 60000 });
  assert.equal(await firstLink.evaluate((element) => document.activeElement === element), true);
  await page.screenshot({ path: `${SEARCH_EVIDENCE_DIR}/chromium-desktop-more.png` });

  // This is a new decode, not an already-settled response: interrupt as soon
  // as the large print fragment request begins and prove the next query wins.
  const secondLarge = context.waitForEvent('response', { predicate: largeFragment, timeout: 30000 });
  await input.fill('policy gateway');
  await firstLink.waitFor({ timeout: 30000 });
  await secondLarge;
  await input.fill('network.allowlist');
  await dialog.getByText('Matches all search terms: 3.', { exact: true }).waitFor({ timeout: 30000 });
  await page.waitForTimeout(500);
  assert.equal(await input.inputValue(), 'network.allowlist');
  assert.equal(await dialog.locator('.aa-search__group > a').count(), 3);
  assert.equal(await input.evaluate((element) => document.activeElement === element), true);
  const thirdLarge = context.waitForEvent('response', { predicate: largeFragment, timeout: 30000 });
  await input.fill('policy gateway');
  await firstLink.waitFor({ timeout: 30000 });
  await thirdLarge;
  await page.keyboard.press('Escape');
  assert.equal(await dialog.evaluate((element) => element.open), false);
  assert.equal(await trigger.evaluate((element) => document.activeElement === element), true);
  await page.waitForTimeout(500);
  await trigger.click();
  await input.fill('network.allowlist');
  await dialog.getByText('Matches all search terms: 3.', { exact: true }).waitFor({ timeout: 30000 });
  results.push({ engine: 'chromium-desktop', largeFragmentSeen, focusedAnchorRetained: true,
    loadMore: true, interruptedQuery: true, interruptedClose: true });
  await context.close();
  await rename(await page.video().path(), `${SEARCH_EVIDENCE_DIR}/chromium-desktop-sequence.webm`);
} finally { await browser.close(); }

await writeFile(`${SEARCH_EVIDENCE_DIR}/results.json`, JSON.stringify({
  kind: 'isolated-full-aggregate-worker-regression', sourceUrl: SEARCH_AGGREGATE_URL,
  pagefindVersion: '1.4.0', results,
}, null, 2));
console.log(`PASS: ${results.length} worker regression contexts; ${SEARCH_EVIDENCE_DIR}`);
