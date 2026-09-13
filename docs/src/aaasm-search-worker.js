// Keep Pagefind's fragment decoding off the page's main thread. In particular,
// a combined-book print fragment must not freeze an already visible result.
let refs = [];
let next = 0;
let closeCount = 0;
let queryTerms = [];
let scanning = false;

export function queryTermsFor(query) {
  return query.trim().normalize('NFKC').toLocaleLowerCase('en').split(/\s+/).filter(Boolean);
}

export function matchesAll(result, terms) {
  const text = ((result.content || '') + ' ' + (result.meta?.title || ''))
    .normalize('NFKC').toLocaleLowerCase('en');
  return terms.every((term) => text.includes(term));
}

async function scan(targetCount) {
  if (scanning) return;
  scanning = true;
  try {
    while (next < refs.length && closeCount < targetCount) {
      const batchStart = next;
      const batch = refs.slice(next, next + 4);
      next += batch.length;
      // Bounded concurrency avoids starting many expensive fragments together.
      await Promise.all(batch.map(async (ref, offset) => {
        const result = await ref.data();
        const literal = matchesAll(result, queryTerms);
        if (literal) closeCount++;
        // Full combined-book content is useful for classification, but the
        // dialog only needs these display fields. Do not clone megabytes of
        // print-view text back onto the main thread.
        const { url, meta, excerpt, anchors, sub_results } = result;
        postMessage({ type: 'item', rank: batchStart + offset, literal,
          result: { url, meta, excerpt, anchors, sub_results } });
      }));
    }
    postMessage({ type: 'settled', next, total: refs.length });
  } catch (error) {
    postMessage({ type: 'error', phase: 'data', message: String(error) });
  } finally {
    scanning = false;
  }
}

globalThis.onmessage = async ({ data }) => {
  try {
    if (data.type === 'search') {
      const api = await import(data.moduleUrl);
      await api.options({ basePath: data.base });
      const found = await api.search(data.query);
      refs = found.results;
      next = 0;
      closeCount = 0;
      queryTerms = queryTermsFor(data.query);
      postMessage({ type: 'found', total: refs.length });
      await scan(10);
    } else if (data.type === 'more') {
      await scan(data.targetCount);
    }
  } catch (error) {
    postMessage({ type: 'error', phase: 'load', message: String(error) });
  }
};
