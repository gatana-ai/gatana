import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdir, mkdtemp, readFile, writeFile } from 'fs/promises';
import { tmpdir } from 'os';
import { join } from 'path';
import { FakeSkillsApi } from './fakeApi.js';
import { pushSkills } from '../../src/actions/skills/push.js';
import { syncDirectory } from '../../src/actions/skills/sync.js';
import { parseSkillMd } from '../../src/actions/skills/frontmatter.js';
import { readManifest } from '../../src/actions/skills/manifest.js';

const identity = { orgId: 'acme', baseUrl: 'https://acme.example' };
const syncDefaults = { dryRun: false, prune: true, force: false };
const pushDefaults = { force: false, dryRun: false };
const tmp = () => mkdtemp(join(tmpdir(), 'gatana-push-'));

async function writeSkill(
  dir: string,
  name: string,
  body: string,
  front = `name: ${name}\ndescription: Use for ${name}\nlicense: MIT`
) {
  await mkdir(join(dir, name), { recursive: true });
  const file = join(dir, name, 'SKILL.md');
  await writeFile(file, `---\n${front}\n---\n\n${body}`);
  return file;
}

test('a new hand-written skill is created, stamped, and pushing again is unchanged', async () => {
  const api = new FakeSkillsApi();
  const dir = await tmp();
  const file = await writeSkill(dir, 'fresh', 'Do the thing.\n');

  const [created] = await pushSkills(api, identity, file, pushDefaults);
  assert.equal(created.action, 'created');
  const stamped = parseSkillMd(await readFile(file, 'utf8'));
  assert.equal(stamped.frontmatter.metadata['gatana-org'], 'acme');
  assert.ok(stamped.frontmatter.metadata['gatana-id']);
  assert.deepEqual(stamped.frontmatter.extra, { license: 'MIT' });
  assert.equal(stamped.body, 'Do the thing.\n');

  const [again] = await pushSkills(api, identity, file, pushDefaults);
  assert.equal(again.action, 'unchanged');
  assert.ok(!api.calls.some(c => c.startsWith('update')));
});

test('a synced file that was edited updates its skill and the manifest, so the next sync is clean', async () => {
  const api = new FakeSkillsApi();
  const a = api.seed({ name: 'alpha', content: 'v1\n' });
  const dir = await tmp();
  await syncDirectory(api, identity, dir, syncDefaults);
  const file = join(dir, 'alpha', 'SKILL.md');
  const text = await readFile(file, 'utf8');
  await writeFile(file, text.replace('v1', 'v2'));

  const [updated] = await pushSkills(api, identity, join(dir, 'alpha'), pushDefaults);
  assert.equal(updated.action, 'updated');
  assert.equal((await api.get(a.id)).content, 'v2\n');
  const manifest = (await readManifest(dir))!;
  assert.equal(
    manifest.skills[a.id].updatedAt,
    new Date((await api.get(a.id)).updatedAt as unknown as string).toISOString()
  );

  const summary = await syncDirectory(api, identity, dir, syncDefaults);
  assert.equal(summary.written, 0);
  assert.equal(summary.warnings.length, 0);
});

test('a server-side change after the local copy is a conflict unless forced', async () => {
  const api = new FakeSkillsApi();
  const a = api.seed({ name: 'alpha', content: 'v1\n' });
  const dir = await tmp();
  await syncDirectory(api, identity, dir, syncDefaults);
  const file = join(dir, 'alpha', 'SKILL.md');
  await writeFile(file, (await readFile(file, 'utf8')).replace('v1', 'mine'));
  api.change(a.id, { content: 'theirs\n' });

  const [conflict] = await pushSkills(api, identity, file, pushDefaults);
  assert.equal(conflict.action, 'conflict');
  assert.equal((await api.get(a.id)).content, 'theirs\n');

  const [forced] = await pushSkills(api, identity, file, { ...pushDefaults, force: true });
  assert.equal(forced.action, 'updated');
  assert.equal((await api.get(a.id)).content, 'mine\n');
});

test('a new file whose name exists on the server needs a baseline; a stale name resolves through the list', async () => {
  const api = new FakeSkillsApi();
  api.seed({ name: 'taken', content: 'server\n' });
  const dir = await tmp();
  const file = await writeSkill(dir, 'taken', 'local\n');
  const [conflict] = await pushSkills(api, identity, file, pushDefaults);
  assert.equal(conflict.action, 'conflict');
  assert.match(conflict.detail, /no sync baseline/);
  const [forced] = await pushSkills(api, identity, file, { ...pushDefaults, force: true });
  assert.equal(forced.action, 'updated');
});

test('a directory of skill folders pushes each; bad files are reported and do not stop the rest', async () => {
  const api = new FakeSkillsApi();
  const dir = await tmp();
  await writeSkill(dir, 'good-one', 'A\n');
  await writeSkill(dir, 'bad-one', 'B\n', 'name: Bad Name\ndescription: x');
  await writeSkill(dir, 'good-two', 'C\n');
  const results = await pushSkills(api, identity, dir, pushDefaults);
  assert.deepEqual(
    results.map(r => `${r.name}:${r.action}`),
    ['bad-one:error', 'good-one:created', 'good-two:created']
  );
});

test('a file from another organization is refused without --force', async () => {
  const api = new FakeSkillsApi();
  const dir = await tmp();
  const file = await writeSkill(
    dir,
    'foreign',
    'X\n',
    'name: foreign\ndescription: x\nmetadata:\n  gatana-id: skill_9\n  gatana-org: other'
  );
  const [refused] = await pushSkills(api, identity, file, pushDefaults);
  assert.equal(refused.action, 'error');
  assert.match(refused.detail, /organization other/);
  const [created] = await pushSkills(api, identity, file, { ...pushDefaults, force: true });
  assert.equal(created.action, 'created');
});

test('dry run reports without writing', async () => {
  const api = new FakeSkillsApi();
  const dir = await tmp();
  const file = await writeSkill(dir, 'fresh', 'A\n');
  const [result] = await pushSkills(api, identity, file, { ...pushDefaults, dryRun: true });
  assert.equal(result.action, 'created');
  assert.deepEqual(await api.list(), []);
  assert.equal(parseSkillMd(await readFile(file, 'utf8')).frontmatter.metadata['gatana-id'], undefined);
});
