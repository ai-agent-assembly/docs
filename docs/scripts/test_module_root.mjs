// Check the actual module-root expression embedded in the mdBook template.
// No browser, network, or alternate module-switcher implementation is involved.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
import {runInNewContext} from 'node:vm';

const template = readFileSync(new URL('../theme/head.hbs', import.meta.url), 'utf8');
const beginning = template.indexOf("var ROOT = '{{ path_to_root }}';", template.indexOf('<!-- Hub landing'));
assert.notEqual(beginning, -1, 'module switcher root expression exists');
const ending = template.indexOf('ROOT = ROOT.href;', beginning);
assert.notEqual(ending, -1, 'module switcher root expression ends');
const rootSource = template.slice(beginning, ending + 'ROOT = ROOT.href;'.length);

function resolvedRoot(baseURI, pathToRoot, language) {
  const context = {URL, document: {baseURI}};
  runInNewContext(
    rootSource.replaceAll('{{ path_to_root }}', pathToRoot).replaceAll('{{ language }}', language),
    context,
  );
  return context.ROOT;
}

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

test('missing version manifest offers module home without asserting latest', () => {
  assert.match(template, /verSel\.appendChild\(option\('', 'Module home \(version unavailable\)'\)\)/);
  assert.match(template, /var ver = verSel\.value;\s*return ROOT \+ sub \+ '\/' \+ \(ver \? ver \+ '\/' : ''\);/);
});
