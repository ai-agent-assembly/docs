import assert from 'node:assert/strict';
import { mkdir, rename, writeFile } from 'node:fs/promises';

// Run against a locally served, aggregated-style mdBook + Pagefind fixture.
// Example: PLAYWRIGHT_MODULE=/path/to/@playwright/test/index.mjs \
//   SEARCH_FIXTURE_URL=http://127.0.0.1:3072/ \
//   SEARCH_EVIDENCE_DIR=/path/to/evidence node docs/scripts/test_global_search_browser.mjs
// The fixture is representative; it is not proof about the entire aggregate.
const modulePath = process.env.PLAYWRIGHT_MODULE;
const fixtureUrl = process.env.SEARCH_FIXTURE_URL;
const evidenceDir = process.env.SEARCH_EVIDENCE_DIR;
if (!modulePath || !fixtureUrl || !evidenceDir) {
  throw new Error('Set PLAYWRIGHT_MODULE, SEARCH_FIXTURE_URL and SEARCH_EVIDENCE_DIR');
}
const { chromium } = await import(modulePath);
await mkdir(evidenceDir, { recursive: true });
const browser = await chromium.launch({ headless: true });
const results = [];

try {
  for (const variant of [
    { name: 'desktop-light-normal', width: 1280, height: 800, theme: 'light', motion: 'no-preference' },
    { name: 'mobile-navy-reduced', width: 390, height: 844, theme: 'navy', motion: 'reduce' },
  ]) {
    const context = await browser.newContext({
      viewport: { width: variant.width, height: variant.height },
      colorScheme: variant.theme === 'light' ? 'light' : 'dark',
      reducedMotion: variant.motion,
      recordVideo: { dir: evidenceDir, size: { width: variant.width, height: variant.height } },
    });
    await context.addInitScript(theme => localStorage.setItem('mdbook-theme', theme), variant.theme);
    const page = await context.newPage();
    await page.goto(fixtureUrl);
    const trigger = page.getByRole('button', { name: 'Search all docs…' });
    await trigger.waitFor();
    await trigger.click();
    const dialog = page.locator('dialog.aa-search__modal');
    const input = page.getByRole('searchbox', { name: 'Search all docs' });
    assert.equal(await dialog.evaluate(el => el.open), true);
    assert.equal(await input.evaluate(el => document.activeElement === el), true);

    await input.fill('network.allowlist');
    await page.getByText('Matches all search terms: 1.', { exact: true }).waitFor();
    assert.match(await dialog.locator('.aa-search__group a').first().getAttribute('href'),
      /\/core\/latest\/policy-reference\.html$/);
    assert.match(await dialog.locator('.aa-search__scope').first().innerText(), /Core · latest/);
    await page.waitForTimeout(550); // evidence dwell, never product loading delay
    await page.screenshot({ path: `${evidenceDir}/${variant.name}-exact.png` });
    await dialog.locator('.aa-search__group > a').first().click();
    assert.match(page.url(), /\/core\/latest\/policy-reference\.html$/,
      'result activation reaches the published fixture article');
    await page.waitForTimeout(550);
    await page.goto(fixtureUrl);
    await trigger.waitFor();
    await trigger.click();

    await input.fill('zzzauditnomatchqzx');
    await page.getByText('No results match all search terms.', { exact: true }).waitFor();
    assert.equal(await dialog.locator('.aa-search__group').count(), 2,
      'only the two known Mastra archive/current fixture pages remain as suggestions');
    const related = dialog.locator('details.aa-search__related');
    assert.equal(await related.evaluate(el => el.open), false, 'related suggestions start collapsed');
    await related.locator('summary').click();
    assert.equal(await related.evaluate(el => el.open), true);
    assert.match(await related.innerText(), /Node SDK · default/);
    assert.match(await related.innerText(), /Node SDK · 0\.0\.1-rc\.4/);
    await page.waitForTimeout(550);
    await page.screenshot({ path: `${evidenceDir}/${variant.name}-related.png` });

    await input.fill('漢字');
    await page.getByText('No results match all search terms.', { exact: true }).waitFor();
    assert.equal(await related.isVisible(), false, 'zero-result query has no suggestion section');

    await input.fill('Mastra');
    await page.getByText('Matches all search terms: 2.', { exact: true }).waitFor();
    assert.ok((await dialog.locator('.aa-search__sub a[href*="#"]').count()) > 0,
      'heading anchors remain native links');
    await page.waitForTimeout(450);
    await input.fill('policy');
    await input.fill('network.allowlist');
    await page.getByText('Matches all search terms: 1.', { exact: true }).waitFor();
    assert.match(await dialog.locator('.aa-search__group a').first().getAttribute('href'),
      /\/core\/latest\/policy-reference\.html$/);
    await page.waitForTimeout(450);

    await dialog.getByRole('button', { name: 'Clear query' }).click();
    assert.equal(await input.inputValue(), '');
    assert.equal(await dialog.getByRole('status').innerText(), 'Enter search terms.');
    assert.equal(await input.evaluate(el => document.activeElement === el), true);
    await page.waitForTimeout(450);
    for (let i = 0; i < 8; i++) {
      await page.keyboard.press('Tab');
      assert.equal(await dialog.evaluate(el => el.contains(document.activeElement)), true,
        'native modal contains tab focus');
    }
    await input.focus();
    await input.fill('network.allowlist');
    await page.getByText('Matches all search terms: 1.', { exact: true }).waitFor();
    await page.keyboard.press('Escape');
    assert.equal(await dialog.evaluate(el => el.open), false);
    assert.equal(await trigger.evaluate(el => document.activeElement === el), true,
      'Escape returns to invoking trigger');
    await trigger.click();
    await dialog.getByRole('button', { name: 'Close search' }).click();
    assert.equal(await trigger.evaluate(el => document.activeElement === el), true,
      'explicit Close returns to invoking trigger');
    await page.waitForTimeout(450);

    results.push({ variant: variant.name, exact: true, related: true, zero: true, anchors: true,
      cleared: true, tabContained: true, escapeFocus: true, closeFocus: true });
    await context.close();
    await rename(await page.video().path(), `${evidenceDir}/${variant.name}-sequence.webm`);
  }

  const errorContext = await browser.newContext({ viewport: { width: 390, height: 844 },
    recordVideo: { dir: evidenceDir, size: { width: 390, height: 844 } } });
  const errorPage = await errorContext.newPage();
  await errorPage.route('**/pagefind/pagefind.js*', route => route.abort());
  await errorPage.goto(fixtureUrl);
  await errorPage.getByRole('button', { name: 'Search all docs…' }).click();
  const errorInput = errorPage.getByRole('searchbox', { name: 'Search all docs' });
  await errorInput.fill('network.allowlist');
  await errorPage.getByText('Search is unavailable. Edit the query to retry.', { exact: true }).waitFor();
  await errorPage.waitForTimeout(550);
  await errorPage.screenshot({ path: `${evidenceDir}/mobile-search-error.png` });
  await errorPage.unroute('**/pagefind/pagefind.js*');
  await errorInput.fill('policy');
  await errorPage.getByText('Matches all search terms:', { exact: false }).waitFor();
  assert.equal(await errorInput.evaluate(el => document.activeElement === el), true,
    'recovery keeps focus in the search input');
  await errorPage.waitForTimeout(550);
  results.push({ variant: 'mobile-retry', error: true, recovered: true });
  await errorContext.close();
  await rename(await errorPage.video().path(), `${evidenceDir}/mobile-error-retry-sequence.webm`);

  const raceContext = await browser.newContext({ viewport: { width: 1280, height: 800 },
    recordVideo: { dir: evidenceDir, size: { width: 1280, height: 800 } } });
  const racePage = await raceContext.newPage();
  await racePage.goto(fixtureUrl);
  await racePage.getByRole('button', { name: 'Search all docs…' }).click();
  const raceInput = racePage.getByRole('searchbox', { name: 'Search all docs' });
  await raceInput.fill('漢字'); // initialize the API without loading either result fragment
  await racePage.getByText('No results match all search terms.', { exact: true }).waitFor();
  let releaseOld;
  const oldGate = new Promise(resolve => { releaseOld = resolve; });
  let signalOld;
  const oldSeen = new Promise(resolve => { signalOld = resolve; });
  let oldUrl;
  await racePage.route('**/pagefind/fragment/*.pf_fragment', async route => {
    if (!oldUrl) {
      oldUrl = route.request().url();
      signalOld();
      await oldGate;
    }
    await route.continue();
  });
  await raceInput.fill('network.allowlist');
  await Promise.race([oldSeen, new Promise((_, reject) => setTimeout(() => reject(new Error('old fragment never requested')), 5000))]);
  await raceInput.fill('Mastra');
  await racePage.getByText('Matches all search terms: 2.', { exact: true }).waitFor();
  await racePage.waitForTimeout(550);
  const oldResponse = racePage.waitForResponse(response => response.url() === oldUrl);
  releaseOld();
  await oldResponse; // prove the superseded response actually completed
  await racePage.waitForTimeout(450);
  assert.equal(await raceInput.inputValue(), 'Mastra');
  assert.equal(await racePage.locator('.aa-search__status').innerText(), 'Matches all search terms: 2.');
  assert.equal(await raceInput.evaluate(el => document.activeElement === el), true);
  results.push({ variant: 'desktop-response-order', oldResponseCompleted: true, latestResultRetained: true });
  await raceContext.close();
  await rename(await racePage.video().path(), `${evidenceDir}/desktop-response-order-sequence.webm`);
} finally {
  await browser.close();
}
await writeFile(`${evidenceDir}/results.json`, JSON.stringify({
  kind: 'representative-local-fixture', pagefindVersion: '1.4.0',
  sourcePages: [
    '/core/latest/policy-reference.html', '/node-sdk/examples/mastra/',
    '/node-sdk/0.0.1-rc.4/examples/mastra/', '/python-sdk/latest/', '/arena/latest/',
  ], results,
}, null, 2));
console.log(`PASS: ${results.length} rendered search variants; ${evidenceDir}`);
