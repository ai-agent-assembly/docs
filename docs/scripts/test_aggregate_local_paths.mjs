import assert from 'node:assert/strict';
import { mkdtemp, mkdir, rm, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { aggregateRoot, existingAggregatePath } from './aggregate_local_paths.mjs';

test('aggregate reader stays inside a concrete local public tree', async () => {
  const fixture = await mkdtemp(join(tmpdir(), 'aaasm-aggregate-paths-'));
  try {
    const publicDir = join(fixture, 'public');
    await mkdir(join(publicDir, 'pagefind'), { recursive: true });
    await writeFile(join(publicDir, 'pagefind', 'pagefind.js'), 'local index');
    await writeFile(join(fixture, 'outside.txt'), 'private');
    await symlink(join(fixture, 'outside.txt'), join(publicDir, 'pagefind', 'escape.txt'));
    const root = await aggregateRoot(publicDir);
    assert.equal(await existingAggregatePath(root, 'pagefind', 'pagefind.js'),
      join(root, 'pagefind', 'pagefind.js'));
    await assert.rejects(existingAggregatePath(root, '..', 'outside.txt'), /unsafe aggregate path segment/);
    await assert.rejects(existingAggregatePath(root, '../outside.txt'), /unsafe aggregate path segment/);
    await assert.rejects(existingAggregatePath(root, 'pagefind', 'escape.txt'), /escapes public root/);
    await assert.rejects(existingAggregatePath(root, 'core', '../../outside.txt'), /unsafe aggregate path segment/);
    const rejectedCliPath = spawnSync(process.execPath,
      [fileURLToPath(new URL('./verify_full_aggregate_search.mjs', import.meta.url)), publicDir],
      { cwd: publicDir, encoding: 'utf8' });
    assert.notEqual(rejectedCliPath.status, 0);
    assert.match(rejectedCliPath.stderr, /without path arguments/);
  } finally {
    await rm(fixture, { recursive: true, force: true });
  }
});
