import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import '../src/aaasm-docs-utils.js';
import { matchesAll, queryTermsFor } from '../src/aaasm-search-worker.js';

// Exercise the helpers actually loaded by the hub and module Worker; no
// generated template text is dynamically executed in this source test.
const template = readFileSync(new URL('../theme/head.hbs', import.meta.url), 'utf8');
assert.match(template, /src="{{ path_to_root }}aaasm-docs-utils\.js"/);
assert.match(template, /AADocsUtils\.canonical\(raw, location\.href, location\.origin\)/);
assert.match(template, /AADocsUtils\.scope\(url\)/);
const location = {
  href: 'https://docs.agent-assembly.com/docs/guides.html',
  origin: 'https://docs.agent-assembly.com',
};
const canonical = (raw) => AADocsUtils.canonical(raw, location.href, location.origin);
const scope = AADocsUtils.scope;
const matches = (query, result) => matchesAll(result, queryTermsFor(query));

assert.equal(matches('network.allowlist', {
  content: 'An empty network.allowlist is deny-all.', meta: { title: 'Policy YAML Reference' },
}), true, 'technical dotted key remains literal');
assert.equal(matches('POLICY network.allowlist', {
  content: 'An empty network.allowlist is deny-all.', meta: { title: 'Policy YAML Reference' },
}), true, 'all literal terms may occur in title and page content');
assert.equal(matches('zzzauditnomatchqzx', {
  content: 'import { z } from "zod"', meta: { title: 'Mastra' },
}), false, 'a single highlighted z is not a full query match');
assert.equal(matches('policy gateway', {
  content: 'The gateway uses a policy.', meta: { title: 'Guide' },
}), true, 'multiword label means all terms, not exact phrase');
assert.equal(matches('policy gateway', {
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
