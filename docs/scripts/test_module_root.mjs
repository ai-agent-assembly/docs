// Check the exact helper used by the mdBook template without executing a
// string of generated inline JavaScript in a separate VM.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
import '../src/aaasm-docs-utils.js';

const template = readFileSync(new URL('../theme/head.hbs', import.meta.url), 'utf8');
assert.match(template, /AADocsUtils\.moduleRoot\(document\.baseURI, '{{ path_to_root }}', '{{ language }}'\)/);
const resolvedRoot = AADocsUtils.moduleRoot;

test('module root is the containing book, not a root-level HTML filename', () => {
  for (const page of ['index.html', 'sitemaps.html', '404.html']) {
    assert.equal(resolvedRoot(`https://docs.example/${page}`, '', 'en'), 'https://docs.example/');
  }
  assert.equal(
    resolvedRoot('https://example.github.io/docs/index.html', '', 'en'),
    'https://example.github.io/docs/',
  );
});

test('localized and nested pages resolve the shared module registry root', () => {
  assert.equal(
    resolvedRoot('https://docs.example/zh-Hant/index.html', '', 'zh-Hant'),
    'https://docs.example/',
  );
  assert.equal(
    resolvedRoot('https://example.github.io/docs/zh-Hant/index.html', '', 'zh-Hant'),
    'https://example.github.io/docs/',
  );
  assert.equal(
    resolvedRoot('https://docs.example/architecture/foo.html', '../', 'en'),
    'https://docs.example/',
  );
  assert.equal(
    resolvedRoot('https://example.github.io/docs/architecture/foo.html', '../', 'en'),
    'https://example.github.io/docs/',
  );
});

test('missing version manifest offers a short module-home option and separate status', () => {
  assert.match(template, /verSel\.appendChild\(option\('', 'Module home'\)\)/);
  assert.match(template, /versionStatus\.textContent = 'Version list unavailable\.'/);
  assert.match(template, /verSel\.setAttribute\('aria-describedby', versionStatus\.id\)/);
  assert.match(template, /var ver = verSel\.value;\s*return ROOT \+ sub \+ '\/' \+ \(ver \? ver \+ '\/' : ''\);/);
});
