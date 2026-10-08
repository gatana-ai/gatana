import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdir, mkdtemp, readdir, readFile, stat, symlink, writeFile } from 'fs/promises';
import { tmpdir } from 'os';
import { join } from 'path';
import { FakeSkillsApi } from './fakeApi.js';
import { syncDirectory, syncTargets } from '../../src/actions/skills/sync.js';
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

test('installing a name follows it: the sync is limited to it, a rename is followed, what leaves it is pruned', async () => {
  const api = new FakeSkillsApi();
  const release = api.seedCollection({ name: 'release' });
  const other = api.seedCollection({ name: 'other' });
  const inRelease = api.seed({ name: 'deploy', content: 'D\n', collectionId: release.id });
  api.seed({ name: 'review', content: 'R\n', collectionId: other.id });
  api.seed({ name: 'root-skill', content: 'S\n' });
  const dir = await tmp();

  const releaseSubscription = { kind: 'collection' as const, id: release.id, name: release.name };
  const first = await syncDirectory(api, identity, dir, { ...defaults, subscribe: releaseSubscription });
  assert.equal(first.written, 1);
  assert.deepEqual(first.subscriptions, [{ kind: 'collection', id: release.id, name: 'release' }]);
  assert.equal(await exists(join(dir, 'deploy', 'SKILL.md')), true);
  assert.equal(await exists(join(dir, 'review')), false);
  assert.equal(await exists(join(dir, 'root-skill')), false);
  assert.equal(
    parseSkillMd(await readFile(join(dir, 'deploy', 'SKILL.md'), 'utf8')).frontmatter.metadata['gatana-collection'],
    'release'
  );

  // Installing the same name again keeps one manifest entry.
  await syncDirectory(api, identity, dir, { ...defaults, subscribe: releaseSubscription });
  assert.deepEqual((await readManifest(dir))!.subscriptions, [{ kind: 'collection', id: release.id, name: 'release' }]);

  // A dry run with a name previews without writing the subscription.
  const preview = await syncDirectory(api, identity, dir, {
    ...defaults,
    dryRun: true,
    subscribe: { kind: 'collection', id: other.id, name: other.name },
  });
  assert.equal(preview.subscriptions!.length, 2);
  assert.deepEqual((await readManifest(dir))!.subscriptions, [{ kind: 'collection', id: release.id, name: 'release' }]);

  api.renameCollection(release.id, 'release-train');
  const renamed = await syncDirectory(api, identity, dir, defaults);
  assert.ok(renamed.warnings.some(w => /now named "release-train"/.test(w)));
  assert.deepEqual((await readManifest(dir))!.subscriptions, [
    { kind: 'collection', id: release.id, name: 'release-train' },
  ]);

  // A skill moved out of the collection is pruned like an unshared one.
  api.change(inRelease.id, { collectionId: null });
  const moved = await syncDirectory(api, identity, dir, defaults);
  assert.equal(moved.removed, 1);
  assert.equal(await exists(join(dir, 'deploy')), false);

  // --reset forgets the subscriptions and takes every readable skill again.
  const reset = await syncDirectory(api, identity, dir, { ...defaults, reset: true });
  assert.equal(reset.written, 3);
  assert.equal(reset.subscriptions, null);
  assert.equal((await readManifest(dir))!.subscriptions, null);
});

test('a subscribed collection that disappears is reported and its skills are pruned', async () => {
  const api = new FakeSkillsApi();
  const release = api.seedCollection({ name: 'release' });
  api.seed({ name: 'deploy', content: 'D\n', collectionId: release.id });
  const dir = await tmp();
  await syncDirectory(api, identity, dir, {
    ...defaults,
    subscribe: { kind: 'collection', id: release.id, name: release.name },
  });

  api.removeCollection(release.id);
  const summary = await syncDirectory(api, identity, dir, defaults);
  assert.equal(summary.removed, 1);
  assert.ok(summary.warnings.some(w => /gone or no longer shared/.test(w)));
  // The entry stays and is reported until the directory is reset with --reset.
  assert.deepEqual((await readManifest(dir))!.subscriptions, [{ kind: 'collection', id: release.id, name: 'release' }]);
});

test('a single skill can be followed next to a collection; a rename is followed, a removal reported, a name in both namespaces refused', async () => {
  const api = new FakeSkillsApi();
  const release = api.seedCollection({ name: 'release' });
  api.seed({ name: 'deploy', content: 'D\n', collectionId: release.id });
  const lone = api.seed({ name: 'triage', content: 'T\n' });
  api.seed({ name: 'other', content: 'O\n' });
  const dir = await tmp();

  const { resolveSubscription } = await import('../../src/actions/skills/subscriptions.js');
  const skill = await resolveSubscription(api, 'triage');
  assert.deepEqual(skill, { kind: 'skill', id: lone.id, name: 'triage' });
  assert.deepEqual(await resolveSubscription(api, 'release'), { kind: 'collection', id: release.id, name: 'release' });
  await assert.rejects(resolveSubscription(api, 'nothing-here'), /No collection or skill named "nothing-here"/);

  const first = await syncDirectory(api, identity, dir, { ...defaults, subscribe: skill });
  assert.equal(first.written, 1);
  assert.equal(await exists(join(dir, 'triage', 'SKILL.md')), true);
  assert.equal(await exists(join(dir, 'other')), false);

  const both = await syncDirectory(api, identity, dir, {
    ...defaults,
    subscribe: await resolveSubscription(api, 'release'),
  });
  assert.equal(both.written, 1);
  assert.equal(await exists(join(dir, 'deploy', 'SKILL.md')), true);

  api.change(lone.id, { name: 'incident-triage' });
  const renamed = await syncDirectory(api, identity, dir, defaults);
  assert.ok(renamed.warnings.some(w => /skill "triage" is now named "incident-triage"/.test(w)));
  assert.equal(await exists(join(dir, 'incident-triage', 'SKILL.md')), true);
  assert.equal(await exists(join(dir, 'triage')), false);

  api.remove(lone.id);
  const removed = await syncDirectory(api, identity, dir, defaults);
  assert.ok(removed.warnings.some(w => /skill "incident-triage" is gone/.test(w)));
  assert.equal(await exists(join(dir, 'incident-triage')), false);

  // A skill named like a collection needs the caller to say which.
  api.seed({ name: 'release', content: 'R\n' });
  await assert.rejects(resolveSubscription(api, 'release'), /both a collection and a skill/);
  assert.equal((await resolveSubscription(api, 'release', 'collection')).kind, 'collection');
  assert.equal((await resolveSubscription(api, 'release', 'skill')).kind, 'skill');
});

test('sync sets up a folder that was never installed into: it takes every readable skill', async () => {
  const api = new FakeSkillsApi();
  api.seed({ name: 'deploy', content: 'D\n' });
  const installed = await tmp();
  const fresh = await tmp();
  const missing = join(fresh, 'never-made');
  await syncDirectory(api, identity, installed, defaults);

  // The hook path: the same targets as install, nothing special for a first run.
  const dirs = await prepareTargets([installed, fresh, missing]);
  assert.equal(dirs.length, 3);
  const summaries = await syncTargets(api, identity, dirs, defaults);
  assert.equal(summaries.length, 3);
  assert.equal(summaries[0].skipped, 1);
  assert.equal(summaries[1].written, 1);
  assert.equal(summaries[2].written, 1);
  assert.equal((await readManifest(fresh))!.subscriptions, null);
  assert.equal(await exists(join(fresh, 'deploy', 'SKILL.md')), true);
  assert.equal(await exists(join(missing, 'deploy', 'SKILL.md')), true);
});
