import assert from 'node:assert/strict';
import { rename, writeFile } from 'node:fs/promises';
import { openSearchVariant, startSearchRun } from './search_browser_setup.mjs';

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
    await page.getByRole('button', { name: 'Search all docs…' }).click();
    const modal = page.locator('dialog.aa-search__modal');
    const input = modal.getByRole('searchbox', { name: 'Search all docs' });
    const started = performance.now();
    await input.fill('policy gateway');
    const firstMatch = modal.locator('.aa-search__group > a').first();
    await firstMatch.waitFor({ timeout: 30000 });
    const firstMatchMs = Math.round(performance.now() - started);
    console.log(`${variant.name}: first usable match ${firstMatchMs}ms`);
    const firstHref = await firstMatch.getAttribute('href');
    assert.match(await modal.getByRole('status').innerText(), /found so far.*Still checking/);
    await firstMatch.focus();
    assert.equal(await firstMatch.evaluate((el) => document.activeElement === el), true);
    await page.waitForTimeout(550); // evidence dwell, not a product loading delay
    await page.screenshot({ path: `${SEARCH_EVIDENCE_DIR}/${variant.name}-progressive.png` });

    await modal.getByText('More results remain to check.', { exact: false })
      .waitFor({ timeout: 30000 }); // the known 19s combined-book fragment finishes
    assert.equal(await firstMatch.getAttribute('href'), firstHref);
    assert.equal(await firstMatch.evaluate((el) => document.activeElement === el), true,
      'late result insertion must retain the same focused anchor');
    assert.ok(await modal.locator('.aa-search__group > a').count() >= 10);
    await page.waitForTimeout(550);
    await page.screenshot({ path: `${SEARCH_EVIDENCE_DIR}/${variant.name}-later.png` });

    await input.fill('network.allowlist');
    await modal.getByText('Matches all search terms: 3.', { exact: true }).waitFor();
    assert.match(await modal.locator('.aa-search__group > a').first().getAttribute('href'),
      /\/core\/latest\/policy-reference\.html$/);
    results.push({ variant: variant.name, firstMatchMs, provisional: true,
      focusedAnchorRetained: true, laterResultsReadable: true, newQueryReplacesOld: true });
    await context.close();
    await rename(await page.video().path(), `${SEARCH_EVIDENCE_DIR}/${variant.name}-sequence.webm`);
  }
} finally {
  await browser.close();
}
await writeFile(`${SEARCH_EVIDENCE_DIR}/results.json`, JSON.stringify({
  kind: 'isolated-full-aggregate-progressive-search', sourceUrl: SEARCH_AGGREGATE_URL,
  pagefindVersion: '1.4.0', results,
}, null, 2));
assert.ok(results.every((result) => result.firstMatchMs <= 1000),
  `first match exceeded 1s local target: ${results.map((result) => result.firstMatchMs).join(', ')}ms`);
console.log(`PASS: ${results.length} progressive search variants; ${SEARCH_EVIDENCE_DIR}`);
