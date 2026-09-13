import assert from 'node:assert/strict';
import { realpath, stat } from 'node:fs/promises';
import { isAbsolute, relative, resolve, sep } from 'node:path';

// Only read existing files inside the caller's selected local aggregate. In
// particular, neither a crafted Pagefind URL nor an archive manifest may
// traverse out of that tree, including through a symlink.
export async function aggregateRoot(argument) {
  assert.ok(argument, 'usage: node verify_full_aggregate_search.mjs <aggregate-public-dir>');
  const root = await realpath(resolve(argument));
  assert.ok((await stat(root)).isDirectory(), 'aggregate public path must be a directory');
  return root;
}

export async function existingAggregatePath(root, ...segments) {
  for (const segment of segments) {
    assert.ok(typeof segment === 'string' && segment !== '' && segment !== '.' && segment !== '..'
      && !segment.includes('/') && !segment.includes('\\') && !segment.includes('\0'),
    `unsafe aggregate path segment: ${segment}`);
  }
  const file = await realpath(resolve(root, ...segments));
  const relation = relative(root, file);
  assert.ok(relation !== '..' && !relation.startsWith('..' + sep) && !isAbsolute(relation),
    `aggregate path escapes public root: ${file}`);
  return file;
}
