import { mkdir } from 'node:fs/promises';

// Shared recording setup keeps the fixture and complete-aggregate runners on
// the same real browser, theme and motion matrix without duplicating harnesses.
export async function startSearchRun(urlVariable) {
  const { PLAYWRIGHT_MODULE, SEARCH_EVIDENCE_DIR } = process.env;
  const url = process.env[urlVariable];
  if (!PLAYWRIGHT_MODULE || !SEARCH_EVIDENCE_DIR || !url) {
    throw new Error(`Set PLAYWRIGHT_MODULE, ${urlVariable}, SEARCH_EVIDENCE_DIR`);
  }
  const { chromium } = await import(PLAYWRIGHT_MODULE);
  await mkdir(SEARCH_EVIDENCE_DIR, { recursive: true });
  return { chromium, url, evidenceDir: SEARCH_EVIDENCE_DIR };
}

export async function openSearchVariant(browser, url, evidenceDir, variant) {
  const context = await browser.newContext({
    viewport: { width: variant.width, height: variant.height },
    colorScheme: variant.theme === 'light' ? 'light' : 'dark',
    reducedMotion: variant.motion,
    recordVideo: { dir: evidenceDir, size: { width: variant.width, height: variant.height } },
  });
  await context.addInitScript((theme) => localStorage.setItem('mdbook-theme', theme), variant.theme);
  const page = await context.newPage();
  await page.goto(url);
  return { context, page };
}
