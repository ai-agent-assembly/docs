import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';

// Exercise the actual inline search helpers without a browser or full aggregate.
// UI interaction is covered separately against the rendered Pagefind bundle.
const source = readFileSync(new URL('../theme/head.hbs', import.meta.url), 'utf8');
const script = source.match(/<!-- Unified Pagefind index[\s\S]*?<script>([\s\S]*?)<\/script>/)?.[1];
assert.ok(script, 'global Pagefind adapter exists');
const instrumented = script.replace(
  'function init() {',
  'globalThis.searchHelpers = { terms, matchesAll, canonical, scope };\n    function init() {',
);
assert.notEqual(instrumented, script, 'helper boundary found');
const location = {
  href: 'https://docs.agent-assembly.com/docs/guides.html',
  origin: 'https://docs.agent-assembly.com',
};
const context = {
  URL,
  location,
  document: { readyState: 'loading', addEventListener() {} },
};
runInNewContext(instrumented.replaceAll('{{ path_to_root }}', '../'), context);
const { terms, matchesAll, canonical, scope } = context.searchHelpers;

assert.deepEqual(Array.from(terms('  Network.Allowlist  policy  ')), ['network.allowlist', 'policy']);
assert.equal(matchesAll(terms('network.allowlist'), {
  content: 'An empty network.allowlist is deny-all.', meta: { title: 'Policy YAML Reference' },
}), true, 'technical dotted key remains literal');
assert.equal(matchesAll(terms('POLICY network.allowlist'), {
  content: 'An empty network.allowlist is deny-all.', meta: { title: 'Policy YAML Reference' },
}), true, 'all literal terms may occur in title and page content');
assert.equal(matchesAll(terms('zzzauditnomatchqzx'), {
  content: 'import { z } from "zod"', meta: { title: 'Mastra' },
}), false, 'a single highlighted z is not a full query match');
assert.equal(matchesAll(terms('policy gateway'), {
  content: 'The gateway uses a policy.', meta: { title: 'Guide' },
}), true, 'multiword label means all terms, not exact phrase');
assert.equal(matchesAll(terms('policy gateway'), {
  content: 'The gateway uses a rule.', meta: { title: 'Guide' },
}), false);

assert.equal(canonical('/core/latest/index.html#usage').href,
  'https://docs.agent-assembly.com/core/latest/#usage');
assert.equal(canonical('https://unrelated.example/docs/'), null, 'cross-origin result omitted');
assert.equal(scope(canonical('/core/latest/policy-reference.html')), 'Core · latest');
assert.equal(scope(canonical('/python-sdk/latest/')), 'Python SDK · latest');
assert.equal(scope(canonical('/arena/latest/')), 'Arena · latest');
assert.equal(scope(canonical('/node-sdk/examples/mastra/')), 'Node SDK · default');
assert.equal(scope(canonical('/node-sdk/next/examples/mastra/')), 'Node SDK · latest (main)');
assert.equal(scope(canonical('/node-sdk/0.0.1-rc.4/examples/mastra/')),
  'Node SDK · 0.0.1-rc.4');
assert.equal(scope(canonical('/docs/guides.html')), 'Hub · English');

console.log('PASS: literal-term classification, identifier preservation, canonical routes and scope labels');
