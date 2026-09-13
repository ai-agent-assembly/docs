import assert from 'node:assert/strict';
import { rename, writeFile } from 'node:fs/promises';
import { openSearchVariant, startSearchRun } from './search_browser_setup.mjs';

// Exercise the actual generated local aggregate, never a five-page fixture or
// production deployment. The source commits are recorded in its evidence note.
const { chromium, url: SEARCH_AGGREGATE_URL, evidenceDir: SEARCH_EVIDENCE_DIR } =
  await startSearchRun('SEARCH_AGGREGATE_URL');
const browser = await chromium.launch({ headless: true });
const results = [];

try {
  for (const variant of [
    { name: 'desktop-light-normal', width: 1280, height: 800, theme: 'light', motion: 'no-preference' },
    { name: 'mobile-navy-reduced', width: 390, height: 844, theme: 'navy', motion: 'reduce' },
  ]) {
    const { context, page } = await openSearchVariant(
      browser, SEARCH_AGGREGATE_URL, SEARCH_EVIDENCE_DIR, variant);
    const trigger = page.getByRole('button', { name: 'Search all docs…' });
    await trigger.waitFor();
    await trigger.click();
    const modal = page.locator('dialog.aa-search__modal');
    const input = modal.getByRole('searchbox', { name: 'Search all docs' });
    assert.equal(await input.evaluate((el) => document.activeElement === el), true);

    await input.fill('network.allowlist');
    await modal.getByText('Matches all search terms: 3.', { exact: true }).waitFor();
    const literalUrl = await modal.locator('.aa-search__group > a').first().getAttribute('href');
    assert.match(literalUrl, /\/core\/latest\/policy-reference\.html$/);
    assert.match(await modal.locator('.aa-search__scope').first().innerText(), /Core · latest/);
    assert.equal(await modal.locator('details.aa-search__related').evaluate((el) => el.open), false);
    await page.waitForTimeout(550); // recording dwell, not a product loading delay
    await page.screenshot({ path: `${SEARCH_EVIDENCE_DIR}/${variant.name}-identifier.png` });

    await input.fill('zzzauditnomatchqzx');
    await modal.getByText('No results match all search terms.', { exact: true }).waitFor();
    const related = modal.locator('details.aa-search__related');
    assert.equal(await related.isVisible(), true);
    assert.equal(await related.evaluate((el) => el.open), false);
    await related.locator('summary').click();
    assert.match(await related.innerText(), /Related suggestions/);
    await page.waitForTimeout(550);
    await page.screenshot({ path: `${SEARCH_EVIDENCE_DIR}/${variant.name}-related.png` });

    await input.fill('policy gateway');
    await modal.locator('.aa-search__group > a').first().waitFor();
    assert.match(await modal.getByRole('status').innerText(), /found so far.*Still checking/);
    assert.ok(await modal.locator('.aa-search__group > a').count() > 0);
    await input.fill('Mastra');
    await modal.locator('.aa-search__group > a[href*="/node-sdk/examples/mastra/"]').first().waitFor();
    assert.equal(await modal.locator('.aa-search__group > a[href*="/node-sdk/next/"]').count(), 0);
    await page.waitForTimeout(450);
    await page.screenshot({ path: `${SEARCH_EVIDENCE_DIR}/${variant.name}-mastra.png` });

    await modal.getByRole('button', { name: 'Clear query' }).click();
    assert.equal(await input.inputValue(), '');
    assert.equal(await modal.getByRole('status').innerText(), 'Enter search terms.');
    assert.equal(await input.evaluate((el) => document.activeElement === el), true);
    for (let i = 0; i < 8; i++) {
      await page.keyboard.press('Tab');
      assert.equal(await modal.evaluate((el) => el.contains(document.activeElement)), true);
    }
    await input.focus();
    await page.keyboard.press('Escape');
    assert.equal(await modal.evaluate((el) => el.open), false);
    assert.equal(await trigger.evaluate((el) => document.activeElement === el), true);
    await trigger.click();
    await modal.getByRole('button', { name: 'Close search' }).click();
    assert.equal(await trigger.evaluate((el) => document.activeElement === el), true);

    await trigger.click();
    await input.fill('network.allowlist');
    await modal.getByText('Matches all search terms: 3.', { exact: true }).waitFor();
    await modal.locator('.aa-search__group > a').first().click();
    assert.match(page.url(), /\/core\/latest\/policy-reference\.html$/);
    assert.equal(await page.locator('main').isVisible(), true, 'actual published article renders');
    await page.waitForTimeout(550);
    await page.screenshot({ path: `${SEARCH_EVIDENCE_DIR}/${variant.name}-destination.png` });

    results.push({ variant: variant.name, identifier: true, related: true, multiword: true,
      nodeDefaultNoNextDuplicate: true, clear: true, focusReturn: true, destination: true });
    await context.close();
    await rename(await page.video().path(), `${SEARCH_EVIDENCE_DIR}/${variant.name}-sequence.webm`);
  }

  const context = await browser.newContext({ viewport: { width: 390, height: 844 },
    recordVideo: { dir: SEARCH_EVIDENCE_DIR, size: { width: 390, height: 844 } } });
  const page = await context.newPage();
  await context.route('**/pagefind/pagefind.js*', (route) => route.abort());
  await page.goto(SEARCH_AGGREGATE_URL);
  await page.getByRole('button', { name: 'Search all docs…' }).click();
  const modal = page.locator('dialog.aa-search__modal');
  const input = modal.getByRole('searchbox', { name: 'Search all docs' });
  await input.fill('network.allowlist');
  await modal.getByText('Search is unavailable. Retry this query.', { exact: true }).waitFor();
  await page.waitForTimeout(550);
  await page.screenshot({ path: `${SEARCH_EVIDENCE_DIR}/mobile-asset-error.png` });
  await context.unroute('**/pagefind/pagefind.js*');
  const retry = modal.getByRole('button', { name: 'Retry this query' });
  await retry.click();
  assert.equal(await input.inputValue(), 'network.allowlist', 'unchanged query survives retry');
  await modal.getByText('Matches all search terms: 3.', { exact: true }).waitFor();
  assert.equal(await input.evaluate((el) => document.activeElement === el), true);
  assert.match(await modal.locator('.aa-search__group > a').first().getAttribute('href'),
    /\/core\/latest\/policy-reference\.html$/);
  await page.waitForTimeout(550);
  await page.screenshot({ path: `${SEARCH_EVIDENCE_DIR}/mobile-same-query-retry.png` });
  results.push({ variant: 'mobile-asset-error-retry', unchangedQuery: true, focus: true, recovered: true });
  await context.close();
  await rename(await page.video().path(), `${SEARCH_EVIDENCE_DIR}/mobile-asset-error-retry.webm`);
} finally {
  await browser.close();
}

await writeFile(`${SEARCH_EVIDENCE_DIR}/results.json`, JSON.stringify({
  kind: 'isolated-full-aggregate', pagefindVersion: '1.4.0', sourceUrl: SEARCH_AGGREGATE_URL, results,
}, null, 2));
console.log(`PASS: ${results.length} full-aggregate rendered search variants; ${SEARCH_EVIDENCE_DIR}`);
