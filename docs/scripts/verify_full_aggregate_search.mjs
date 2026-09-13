import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import { readFile, readdir } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import { join, resolve } from 'node:path';

// Run only against an isolated, already-built local aggregate. No publisher
// fetch, archive rebuild, or deployed write is needed for this read-only check.
const publicDir = process.argv[2] && resolve(process.argv[2]);
assert.ok(publicDir, 'usage: node verify_full_aggregate_search.mjs <aggregate-public-dir>');
const index = join(publicDir, 'pagefind/pagefind.js');
assert.ok(existsSync(index), `missing generated Pagefind index: ${index}`);

// Pagefind 1.4.0 fetches relative index fragments even when imported in Node.
// Resolve only those generated files from the supplied local aggregate.
globalThis.fetch = async (input) => {
  const url = new URL(String(input), 'http://local.test');
  assert.equal(url.origin, 'http://local.test');
  assert.ok(url.pathname.startsWith('/pagefind/'), `unexpected Pagefind request: ${url.pathname}`);
  const file = join(publicDir, url.pathname);
  try { return new Response(await readFile(file), { status: 200 }); }
  catch { return new Response('missing local fragment', { status: 404 }); }
};

const pagefind = await import(pathToFileURL(index).href);
const search = async (query) => {
  const response = await pagefind.search(query);
  const data = await Promise.all(response.results.map((ref) => ref.data()));
  return { count: response.results.length, data };
};

for (const route of [
  'core/latest/policy-reference.html',
  'node-sdk/next/examples/mastra/', 'node-sdk/examples/mastra/',
  'python-sdk/latest/', 'go-sdk/latest/', 'arena/latest/',
]) {
  assert.ok(existsSync(join(publicDir, route)), `served route/ancestor missing: ${route}`);
}
const coreManifest = JSON.parse(await readFile(join(publicDir, 'core/versions.json')));
assert.ok(coreManifest.archived.length > 0, 'Core archive manifest empty');
for (const version of coreManifest.archived) {
  assert.ok(existsSync(join(publicDir, 'core', version.id)), `Core archive missing: ${version.id}`);
}
const goArchives = (await readdir(join(publicDir, 'go-sdk'))).filter((name) => /^v\d/.test(name));
assert.ok(goArchives.length > 0, 'Go archived tag directories missing');

const mastra = await search('Mastra');
assert.ok(mastra.data.some((hit) => hit.url === '/node-sdk/examples/mastra/'),
  'Node default-channel Mastra must remain searchable');
assert.ok(mastra.data.every((hit) => !hit.url.startsWith('/node-sdk/next/')),
  'Node current/main channel must remain served but not duplicate default-channel search hits');

const identifier = await search('network.allowlist');
const exact = identifier.data.filter((hit) =>
  `${hit.content} ${hit.meta?.title || ''}`.toLowerCase().includes('network.allowlist'));
assert.ok(exact.some((hit) => hit.url === '/core/latest/policy-reference.html'),
  'the literal dotted policy key must survive Pagefind retrieval');

const multiword = await search('policy gateway');
assert.ok(multiword.data.some((hit) => {
  const text = `${hit.content} ${hit.meta?.title || ''}`.toLowerCase();
  return text.includes('policy') && text.includes('gateway');
}), 'ordinary multiword query must retrieve at least one all-term page');

const nonsense = await search('zzzauditnomatchqzx');
assert.ok(nonsense.data.every((hit) =>
  !`${hit.content} ${hit.meta?.title || ''}`.toLowerCase().includes('zzzauditnomatchqzx')),
'Pagefind fuzzy suggestions must not be called literal matches');

console.log(JSON.stringify({
  kind: 'isolated-full-aggregate-pagefind-1.4.0',
  publicDir,
  queries: {
    Mastra: { count: mastra.count, defaultNodeHit: true, nextNodeHits: 0 },
    'network.allowlist': { count: identifier.count, literalHits: exact.length },
    'policy gateway': { count: multiword.count },
    zzzauditnomatchqzx: { count: nonsense.count, literalHits: 0 },
  },
}, null, 2));
