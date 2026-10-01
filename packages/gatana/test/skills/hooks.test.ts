import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdir, mkdtemp, readFile, writeFile } from 'fs/promises';
import { tmpdir } from 'os';
import { join } from 'path';
import yaml from 'js-yaml';
import { findHookAgents, installHook, installHooks, removeHook, removeHooks } from '../../src/actions/skills/hooks.js';

const tmp = () => mkdtemp(join(tmpdir(), 'gatana-hooks-'));

test('agents that are not on the machine are skipped; the ones that are get a hook once', async () => {
  const home = await tmp();
  await mkdir(join(home, '.claude'));
  await mkdir(join(home, '.codex'));

  const first = await installHooks(home);
  assert.deepEqual(
    first.map(r => `${r.agent}:${r.status}`),
    ['claude:installed', 'codex:installed', 'hermes:skipped', 'openclaw:skipped']
  );
  const claude = JSON.parse(await readFile(join(home, '.claude', 'settings.json'), 'utf8'));
  assert.equal(claude.hooks.SessionStart[0].hooks[0].command, 'gatana skills install --quiet');
  const codex = JSON.parse(await readFile(join(home, '.codex', 'hooks.json'), 'utf8'));
  assert.equal(codex.hooks.SessionStart[0].hooks[0].command, 'gatana skills install --quiet');
  assert.equal(codex.hooks.SessionStart[0].hooks[0].timeout, 60);

  const second = await installHooks(home);
  assert.deepEqual(
    second.map(r => `${r.agent}:${r.status}`),
    ['claude:present', 'codex:present', 'hermes:skipped', 'openclaw:skipped']
  );
});

test('existing Claude settings and other SessionStart hooks are kept', async () => {
  const home = await tmp();
  await mkdir(join(home, '.claude'));
  const file = join(home, '.claude', 'settings.json');
  await writeFile(
    file,
    JSON.stringify({
      model: 'opus',
      hooks: { SessionStart: [{ hooks: [{ type: 'command', command: 'echo hi' }] }], Stop: [] },
    })
  );
  assert.equal((await installHook('claude', home)).status, 'installed');
  const settings = JSON.parse(await readFile(file, 'utf8'));
  assert.equal(settings.model, 'opus');
  assert.deepEqual(settings.hooks.Stop, []);
  assert.equal(settings.hooks.SessionStart.length, 2);
  assert.equal(settings.hooks.SessionStart[0].hooks[0].command, 'echo hi');
});

test('a settings file that is not plain JSON is left alone and reported', async () => {
  const home = await tmp();
  await mkdir(join(home, '.claude'));
  const file = join(home, '.claude', 'settings.json');
  const text = '{\n  // my comment\n  "model": "opus"\n}\n';
  await writeFile(file, text);
  const result = await installHook('claude', home);
  assert.equal(result.status, 'manual');
  assert.equal(await readFile(file, 'utf8'), text);
});

test('Hermes: the hooks block is appended to a config without one, comments intact; a config with hooks is not rewritten', async () => {
  const home = await tmp();
  await mkdir(join(home, '.hermes'));
  const file = join(home, '.hermes', 'config.yaml');
  await writeFile(file, '# my hermes config\nmodel: gpt\n');
  assert.equal((await installHook('hermes', home)).status, 'installed');
  const text = await readFile(file, 'utf8');
  assert.ok(text.startsWith('# my hermes config\nmodel: gpt\n'));
  const config = yaml.load(text) as { model: string; hooks: { on_session_start: { command: string }[] } };
  assert.equal(config.model, 'gpt');
  assert.equal(config.hooks.on_session_start[0].command, 'gatana skills install hermes --quiet');
  assert.equal((await installHook('hermes', home)).status, 'present');

  await writeFile(file, 'hooks:\n  on_session_start:\n    - command: "echo hi"\n');
  const manual = await installHook('hermes', home);
  assert.equal(manual.status, 'manual');
  assert.equal(await readFile(file, 'utf8'), 'hooks:\n  on_session_start:\n    - command: "echo hi"\n');
});

test('OpenClaw: the hook folder is written and enabled in the config; other config is kept', async () => {
  const home = await tmp();
  await mkdir(join(home, '.openclaw'));
  await writeFile(
    join(home, '.openclaw', 'openclaw.json'),
    JSON.stringify({ agents: { list: [] }, hooks: { internal: { entries: { other: { enabled: true } } } } })
  );
  const result = await installHook('openclaw', home);
  assert.equal(result.status, 'installed');
  const hookMd = await readFile(join(home, '.openclaw', 'hooks', 'gatana-skills', 'HOOK.md'), 'utf8');
  assert.ok(hookMd.includes('"events": ["gateway:startup", "command:new", "command:reset"]'));
  const handler = await readFile(join(home, '.openclaw', 'hooks', 'gatana-skills', 'handler.ts'), 'utf8');
  assert.ok(handler.includes("execFile('gatana', ['skills', 'install', '--quiet']"));
  const config = JSON.parse(await readFile(join(home, '.openclaw', 'openclaw.json'), 'utf8'));
  assert.deepEqual(config.agents, { list: [] });
  assert.equal(config.hooks.internal.enabled, true);
  assert.deepEqual(config.hooks.internal.entries, { other: { enabled: true }, 'gatana-skills': { enabled: true } });
  assert.equal((await installHook('openclaw', home)).status, 'present');
});

test('remove-hooks takes our hook out of every agent and keeps the rest of the config', async () => {
  const home = await tmp();
  await mkdir(join(home, '.claude'));
  await mkdir(join(home, '.codex'));
  const claudeFile = join(home, '.claude', 'settings.json');
  await writeFile(
    claudeFile,
    JSON.stringify({
      model: 'opus',
      hooks: { SessionStart: [{ hooks: [{ type: 'command', command: 'echo hi' }] }], Stop: [] },
    })
  );
  await installHooks(home);

  const results = await removeHooks(home);
  assert.deepEqual(
    results.map(r => `${r.agent}:${r.status}`),
    ['claude:removed', 'codex:removed', 'hermes:skipped', 'openclaw:skipped']
  );
  const claude = JSON.parse(await readFile(claudeFile, 'utf8'));
  assert.equal(claude.model, 'opus');
  assert.deepEqual(claude.hooks.Stop, []);
  assert.equal(claude.hooks.SessionStart.length, 1);
  assert.equal(claude.hooks.SessionStart[0].hooks[0].command, 'echo hi');
  // Codex had only our hook: the emptied keys disappear with it.
  const codex = JSON.parse(await readFile(join(home, '.codex', 'hooks.json'), 'utf8'));
  assert.equal(codex.hooks, undefined);

  // A second removal finds nothing, and the hooks can come back.
  assert.equal((await removeHook('claude', home)).status, 'absent');
  assert.equal((await installHook('claude', home)).status, 'installed');
});

test('remove-hooks Hermes: only the exact block we appended is cut out; edited hooks are left for the hand', async () => {
  const home = await tmp();
  await mkdir(join(home, '.hermes'));
  const file = join(home, '.hermes', 'config.yaml');
  await writeFile(file, '# my hermes config\nmodel: gpt\n');
  await installHook('hermes', home);

  assert.equal((await removeHook('hermes', home)).status, 'removed');
  assert.equal(await readFile(file, 'utf8'), '# my hermes config\nmodel: gpt\n');
  assert.equal((await removeHook('hermes', home)).status, 'absent');

  await writeFile(file, 'hooks:\n  on_session_start:\n    - command: "gatana skills install hermes --quiet"\n');
  const manual = await removeHook('hermes', home);
  assert.equal(manual.status, 'manual');
  assert.ok((await readFile(file, 'utf8')).includes('gatana skills install hermes'));
});

test('remove-hooks OpenClaw: the hook folder goes, the config entry goes, other entries stay', async () => {
  const home = await tmp();
  await mkdir(join(home, '.openclaw'));
  await writeFile(
    join(home, '.openclaw', 'openclaw.json'),
    JSON.stringify({ hooks: { internal: { entries: { other: { enabled: true } } } } })
  );
  await installHook('openclaw', home);

  const result = await removeHook('openclaw', home);
  assert.equal(result.status, 'removed');
  assert.deepEqual(await findHookAgents(home), ['openclaw']);
  await assert.rejects(readFile(join(home, '.openclaw', 'hooks', 'gatana-skills', 'HOOK.md'), 'utf8'));
  const config = JSON.parse(await readFile(join(home, '.openclaw', 'openclaw.json'), 'utf8'));
  assert.deepEqual(config.hooks.internal.entries, { other: { enabled: true } });

  assert.equal((await removeHook('openclaw', home)).status, 'absent');
});

test('the agents on the machine are named for the hook question; an empty machine names none', async () => {
  const home = await tmp();
  assert.deepEqual(await findHookAgents(home), []);
  await mkdir(join(home, '.codex'));
  await mkdir(join(home, '.openclaw'));
  assert.deepEqual(await findHookAgents(home), ['codex', 'openclaw']);
});
