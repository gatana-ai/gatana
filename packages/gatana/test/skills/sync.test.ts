import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdir, mkdtemp, readdir, readFile, stat, symlink, writeFile } from 'fs/promises';
import { tmpdir } from 'os';
import { join } from 'path';
import { FakeSkillsApi } from './fakeApi.js';
import { syncDirectory } from '../../src/actions/skills/sync.js';
import { readManifest } from '../../src/actions/skills/manifest.js';
import { parseSkillMd } from '../../src/actions/skills/frontmatter.js';
import { prepareTargets } from '../../src/actions/skills/targets.js';

const identity = { orgId: 'acme', baseUrl: 'https://acme.example' };
const defaults = { dryRun: false, prune: true, force: false };
const tmp = () => mkdtemp(join(tmpdir(), 'gatana-sync-'));
const exists = (p: string) =>
  stat(p).then(
    () => true,
    () => false
  );

test('first sync writes every skill and the manifest; second sync fetches nothing', async () => {
  const api = new FakeSkillsApi();
  const a = api.seed({ name: 'alpha', content: '# Alpha\n' });
  api.seed({ name: 'beta', content: '# Beta\n' });
  const dir = await tmp();

  const first = await syncDirectory(api, identity, dir, defaults);
  assert.equal(first.written, 2);
  assert.equal(first.total, 2);
  const text = await readFile(join(dir, 'alpha', 'SKILL.md'), 'utf8');
  const parsed = parseSkillMd(text);
  assert.equal(parsed.frontmatter.metadata['gatana-id'], a.id);
  assert.equal(parsed.body, '# Alpha\n');
  const manifest = (await readManifest(dir))!;
  assert.equal(manifest.orgId, 'acme');
  assert.equal(manifest.skills[a.id].name, 'alpha');

  api.calls.length = 0;
  const second = await syncDirectory(api, identity, dir, defaults);
  assert.equal(second.written, 0);
  assert.deepEqual(api.calls, ['list']);
});

test('remote rename moves the folder, remote delete prunes it, --no-prune keeps it', async () => {
  const api = new FakeSkillsApi();
  const a = api.seed({ name: 'alpha', content: 'A\n' });
  const b = api.seed({ name: 'beta', content: 'B\n' });
  const dir = await tmp();
  await syncDirectory(api, identity, dir, defaults);

  api.change(a.id, { name: 'alpha-two' });
  await syncDirectory(api, identity, dir, defaults);
  assert.equal(await exists(join(dir, 'alpha')), false);
  assert.equal(await exists(join(dir, 'alpha-two', 'SKILL.md')), true);

  api.remove(b.id);
  const kept = await syncDirectory(api, identity, dir, { ...defaults, prune: false });
  assert.equal(kept.removed, 0);
  assert.equal(await exists(join(dir, 'beta', 'SKILL.md')), true);
  assert.ok((await readManifest(dir))!.skills[b.id]);

  const pruned = await syncDirectory(api, identity, dir, defaults);
  assert.equal(pruned.removed, 1);
  assert.equal(await exists(join(dir, 'beta')), false);
  assert.equal((await readManifest(dir))!.skills[b.id], undefined);
});

test('a foreign folder is left alone and reported; --force adopts it', async () => {
  const api = new FakeSkillsApi();
  api.seed({ name: 'mine', content: 'remote\n' });
  const dir = await tmp();
  await mkdir(join(dir, 'mine'));
  await writeFile(join(dir, 'mine', 'SKILL.md'), 'hand written\n');

  const summary = await syncDirectory(api, identity, dir, defaults);
  assert.equal(summary.written, 0);
  assert.equal(await readFile(join(dir, 'mine', 'SKILL.md'), 'utf8'), 'hand written\n');
  assert.match(summary.warnings[0], /not created by this sync/);

  await syncDirectory(api, identity, dir, { ...defaults, force: true });
  assert.equal(parseSkillMd(await readFile(join(dir, 'mine', 'SKILL.md'), 'utf8')).body, 'remote\n');
});

test('local edits are kept until --force; a managed folder with extra files is kept on prune', async () => {
  const api = new FakeSkillsApi();
  const a = api.seed({ name: 'alpha', content: 'v1\n' });
  const dir = await tmp();
  await syncDirectory(api, identity, dir, defaults);
  await writeFile(join(dir, 'alpha', 'SKILL.md'), 'edited locally\n');
  api.change(a.id, { content: 'v2\n' });

  const skipped = await syncDirectory(api, identity, dir, defaults);
  assert.equal(skipped.written, 0);
  assert.match(skipped.warnings[0], /edited locally/);
  assert.equal(await readFile(join(dir, 'alpha', 'SKILL.md'), 'utf8'), 'edited locally\n');

  await syncDirectory(api, identity, dir, { ...defaults, force: true });
  assert.equal(parseSkillMd(await readFile(join(dir, 'alpha', 'SKILL.md'), 'utf8')).body, 'v2\n');

  await writeFile(join(dir, 'alpha', 'notes.txt'), 'keep me');
  api.remove(a.id);
  const pruned = await syncDirectory(api, identity, dir, defaults);
  assert.equal(await exists(join(dir, 'alpha', 'SKILL.md')), false);
  assert.equal(await exists(join(dir, 'alpha', 'notes.txt')), true);
  assert.match(pruned.warnings[0], /kept/);
});

test('a directory synced from another organization is refused without --force', async () => {
  const api = new FakeSkillsApi();
  api.seed({ name: 'alpha', content: 'A\n' });
  const dir = await tmp();
  await syncDirectory(api, identity, dir, defaults);
  await assert.rejects(
    syncDirectory(api, { orgId: 'other', baseUrl: 'https://other.example' }, dir, defaults),
    /synced from acme/
  );
  const switched = await syncDirectory(api, { orgId: 'other', baseUrl: 'https://other.example' }, dir, {
    ...defaults,
    force: true,
  });
  assert.equal((await readManifest(dir))!.orgId, 'other');
  assert.ok(switched.warnings.some(w => /switched/.test(w)));
});

test('dry run touches nothing', async () => {
  const api = new FakeSkillsApi();
  api.seed({ name: 'alpha', content: 'A\n' });
  const dir = await tmp();
  const summary = await syncDirectory(api, identity, dir, { ...defaults, dryRun: true });
  assert.equal(summary.written, 1);
  assert.deepEqual(await readdir(dir), []);
});

test('a skill that disappears between list and get is skipped with a warning', async () => {
  const api = new FakeSkillsApi();
  const a = api.seed({ name: 'alpha', content: 'A\n' });
  const dir = await tmp();
  const originalList = api.list.bind(api);
  api.list = async q => {
    const result = await originalList(q);
    api.remove(a.id);
    return result;
  };
  const summary = await syncDirectory(api, identity, dir, defaults);
  assert.match(summary.warnings[0], /disappeared/);
  assert.equal(await exists(join(dir, 'alpha')), false);
});

test('prepareTargets creates directories and collapses symlinked aliases', async () => {
  const base = await tmp();
  const real = join(base, 'real');
  const alias = join(base, 'alias');
  await mkdir(real);
  await symlink(real, alias);
  const dirs = await prepareTargets([alias, real, join(base, 'new')]);
  assert.equal(dirs.length, 2);
  assert.equal(await exists(join(base, 'new')), true);
});
