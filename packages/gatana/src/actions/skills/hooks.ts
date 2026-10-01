import { mkdir, readFile, rm, stat, writeFile } from 'fs/promises';
import yaml from 'js-yaml';
import os from 'os';
import { join } from 'path';

export type HookAgent = 'claude' | 'codex' | 'hermes' | 'openclaw';

export const HOOK_AGENTS: HookAgent[] = ['claude', 'codex', 'hermes', 'openclaw'];

/**
 * What every hook runs. Claude Code, Codex and OpenClaw read the default targets (~/.claude/skills
 * and ~/.agents/skills), so their hooks install those; Hermes reads its own folder. Claude Code and
 * Codex add the stdout of a SessionStart hook to the model's context, hence --quiet everywhere.
 */
const INSTALL_DEFAULT = 'gatana skills install --quiet';
const INSTALL_HERMES = 'gatana skills install hermes --quiet';
const INSTALL_MARKER = 'gatana skills install';
const OPENCLAW_HOOK = 'gatana-skills';

/** The agent's home directory; its presence is how we tell the agent is installed on this machine. */
export function agentHome(agent: HookAgent, home = os.homedir()): string {
  return join(home, `.${agent}`);
}

const claudeEntry = { matcher: 'startup|resume', hooks: [{ type: 'command', command: INSTALL_DEFAULT }] };
const codexEntry = {
  matcher: 'startup|resume',
  hooks: [{ type: 'command', command: INSTALL_DEFAULT, statusMessage: 'Installing Gatana skills', timeout: 60 }],
};
const hermesLines = [
  'hooks:',
  '  on_session_start:',
  `    - command: "${INSTALL_HERMES}"`,
  '      timeout: 60',
  '  on_session_reset:',
  `    - command: "${INSTALL_HERMES}"`,
  '      timeout: 60',
];
const openclawConfig = { hooks: { internal: { enabled: true, entries: { [OPENCLAW_HOOK]: { enabled: true } } } } };

const OPENCLAW_HOOK_MD = `---
name: ${OPENCLAW_HOOK}
description: "Install the skills of your Gatana organization when the gateway starts and on /new and /reset"
metadata:
  { "openclaw": { "events": ["gateway:startup", "command:new", "command:reset"] } }
---

# Gatana skills

Runs \`${INSTALL_DEFAULT}\` so the skills folders OpenClaw reads follow the organization.
Installed by \`gatana skills install\`; run \`gatana skills remove-hooks openclaw\` to stop.
`;

const OPENCLAW_HANDLER = `import { execFile } from 'node:child_process';

// Written by "gatana skills install". Installs the Gatana skills folders; failures are logged, never thrown,
// so a missing CLI or a network problem cannot break the gateway.
export default async function handler() {
  await new Promise(resolve => {
    execFile('gatana', ['skills', 'install', '--quiet'], { timeout: 60_000 }, error => {
      if (error) {
        console.error(\`gatana skills install failed: \${error.message}\`);
      }
      resolve(undefined);
    });
  });
}
`;

/** Configuration that runs a quiet install when an agent session starts, for pasting by hand. */
export function renderHookSnippet(agent: HookAgent): { snippet: string; note: string } {
  switch (agent) {
    case 'claude':
      return {
        snippet: JSON.stringify({ hooks: { SessionStart: [claudeEntry] } }, null, 2),
        note: 'Merge into ~/.claude/settings.json (every project) or .claude/settings.json (one project).',
      };
    case 'codex':
      return {
        snippet: JSON.stringify({ hooks: { SessionStart: [codexEntry] } }, null, 2),
        note: 'Merge into ~/.codex/hooks.json (every project) or .codex/hooks.json (one project).',
      };
    case 'hermes':
      return { snippet: hermesLines.join('\n'), note: 'Merge into ~/.hermes/config.yaml.' };
    case 'openclaw':
      return {
        snippet: [
          `# ~/.openclaw/hooks/${OPENCLAW_HOOK}/HOOK.md`,
          OPENCLAW_HOOK_MD,
          `# ~/.openclaw/hooks/${OPENCLAW_HOOK}/handler.ts`,
          OPENCLAW_HANDLER,
          '# merge into ~/.openclaw/openclaw.json',
          JSON.stringify(openclawConfig, null, 2),
        ].join('\n'),
        note: 'Write the two files, merge the config, then restart the gateway.',
      };
  }
}

export type HookStatus =
  /** Written now. */
  | 'installed'
  /** Was already there. */
  | 'present'
  /** The agent is not on this machine: its home directory does not exist. */
  | 'skipped'
  /** The config file could not be edited safely; the snippet must be merged by hand. */
  | 'manual';

export interface HookInstall {
  agent: HookAgent;
  file: string;
  status: HookStatus;
  note?: string;
}

async function exists(path: string): Promise<boolean> {
  try {
    await stat(path);
    return true;
  } catch {
    return false;
  }
}

/** Strict JSON only. A file with comments or trailing commas is not rewritten: a round trip would drop them. */
async function readJsonObject(path: string): Promise<Record<string, unknown> | undefined | 'unparseable'> {
  let text: string;
  try {
    text = await readFile(path, 'utf8');
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
      return undefined;
    }
    throw error;
  }
  if (text.trim() === '') {
    return undefined;
  }
  try {
    const json: unknown = JSON.parse(text);
    return json !== null && typeof json === 'object' && !Array.isArray(json)
      ? (json as Record<string, unknown>)
      : 'unparseable';
  } catch {
    return 'unparseable';
  }
}

async function writeJson(path: string, json: unknown): Promise<void> {
  await mkdir(join(path, '..'), { recursive: true });
  await writeFile(path, `${JSON.stringify(json, null, 2)}\n`, 'utf8');
}

/** True when any command hook under SessionStart already runs a gatana install. */
function hasInstallHook(sessionStart: unknown): boolean {
  if (!Array.isArray(sessionStart)) {
    return false;
  }
  return sessionStart.some(entry => {
    const hooks = (entry as { hooks?: unknown })?.hooks;
    return (
      Array.isArray(hooks) &&
      hooks.some(
        hook =>
          typeof (hook as { command?: unknown })?.command === 'string' &&
          (hook as { command: string }).command.includes(INSTALL_MARKER)
      )
    );
  });
}

/** Claude Code and Codex share one shape: {hooks: {SessionStart: [entry]}} in a JSON file. */
async function installJsonHook(agent: 'claude' | 'codex', file: string, entry: unknown): Promise<HookInstall> {
  const json = await readJsonObject(file);
  if (json === 'unparseable') {
    return {
      agent,
      file,
      status: 'manual',
      note: 'not plain JSON; merge the output of "gatana skills hook ' + agent + '" by hand',
    };
  }
  const settings = json ?? {};
  const hooks = (settings.hooks && typeof settings.hooks === 'object' ? settings.hooks : {}) as Record<string, unknown>;
  if (hasInstallHook(hooks.SessionStart)) {
    return { agent, file, status: 'present' };
  }
  hooks.SessionStart = [...(Array.isArray(hooks.SessionStart) ? hooks.SessionStart : []), entry];
  await writeJson(file, { ...settings, hooks });
  return { agent, file, status: 'installed' };
}

/**
 * Hermes keeps its configuration in YAML that people edit by hand, and a parse-and-dump would drop
 * their comments. So: no hooks key yet, append ours as text; hooks present and ours among them,
 * done; hooks present without ours, leave the file alone and ask for a manual merge.
 */
async function installHermesHook(file: string): Promise<HookInstall> {
  const agent = 'hermes';
  let text = '';
  try {
    text = await readFile(file, 'utf8');
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== 'ENOENT') {
      throw error;
    }
  }
  if (text.includes(INSTALL_MARKER)) {
    return { agent, file, status: 'present' };
  }
  let config: unknown;
  try {
    config = yaml.load(text);
  } catch {
    return {
      agent,
      file,
      status: 'manual',
      note: 'not valid YAML; merge the output of "gatana skills hook hermes" by hand',
    };
  }
  if (config !== null && config !== undefined && typeof config === 'object' && 'hooks' in (config as object)) {
    return {
      agent,
      file,
      status: 'manual',
      note: 'already has a hooks section; merge the output of "gatana skills hook hermes" by hand',
    };
  }
  const separator = text === '' || text.endsWith('\n') ? '' : '\n';
  await mkdir(join(file, '..'), { recursive: true });
  await writeFile(file, `${text}${separator}${text === '' ? '' : '\n'}${hermesLines.join('\n')}\n`, 'utf8');
  return { agent, file, status: 'installed' };
}

/**
 * OpenClaw hooks are code, not commands: a folder with a HOOK.md and a handler, enabled per name in
 * openclaw.json. The files are always written (they are ours); the config is edited only when it
 * is plain JSON. The gateway loads hooks at start, so a restart is part of the note either way.
 */
async function installOpenclawHook(home: string): Promise<HookInstall> {
  const agent = 'openclaw';
  const dir = join(home, 'hooks', OPENCLAW_HOOK);
  const configFile = join(home, 'openclaw.json');
  const filesWereThere = await exists(join(dir, 'HOOK.md'));
  await mkdir(dir, { recursive: true });
  await writeFile(join(dir, 'HOOK.md'), OPENCLAW_HOOK_MD, 'utf8');
  await writeFile(join(dir, 'handler.ts'), OPENCLAW_HANDLER, 'utf8');

  const json = await readJsonObject(configFile);
  if (json === 'unparseable') {
    return {
      agent,
      file: configFile,
      status: 'manual',
      note: `hook written to ${dir}; the config is not plain JSON, enable it by hand and restart the gateway`,
    };
  }
  const config = json ?? {};
  const hooks = (config.hooks && typeof config.hooks === 'object' ? config.hooks : {}) as Record<string, unknown>;
  const internal = (hooks.internal && typeof hooks.internal === 'object' ? hooks.internal : {}) as Record<
    string,
    unknown
  >;
  const entries = (internal.entries && typeof internal.entries === 'object' ? internal.entries : {}) as Record<
    string,
    unknown
  >;
  const enabled =
    internal.enabled === true && (entries[OPENCLAW_HOOK] as { enabled?: unknown } | undefined)?.enabled === true;
  if (enabled && filesWereThere) {
    return { agent, file: configFile, status: 'present' };
  }
  await writeJson(configFile, {
    ...config,
    hooks: {
      ...hooks,
      internal: { ...internal, enabled: true, entries: { ...entries, [OPENCLAW_HOOK]: { enabled: true } } },
    },
  });
  return { agent, file: configFile, status: 'installed', note: 'restart the gateway to load it' };
}

/** Installs the hook of one agent; skipped when the agent is not on this machine. */
export async function installHook(agent: HookAgent, home = os.homedir()): Promise<HookInstall> {
  const base = agentHome(agent, home);
  if (!(await exists(base))) {
    return { agent, file: base, status: 'skipped' };
  }
  switch (agent) {
    case 'claude':
      return installJsonHook(agent, join(base, 'settings.json'), claudeEntry);
    case 'codex':
      return installJsonHook(agent, join(base, 'hooks.json'), codexEntry);
    case 'hermes':
      return installHermesHook(join(base, 'config.yaml'));
    case 'openclaw':
      return installOpenclawHook(base);
  }
}

/** Every agent found on this machine gets its hook. */
export async function installHooks(home = os.homedir()): Promise<HookInstall[]> {
  const results: HookInstall[] = [];
  for (const agent of HOOK_AGENTS) {
    results.push(await installHook(agent, home));
  }
  return results;
}

/** The agents on this machine, by the presence of their home directory; the ones a hook can reach. */
export async function findHookAgents(home = os.homedir()): Promise<HookAgent[]> {
  const found: HookAgent[] = [];
  for (const agent of HOOK_AGENTS) {
    if (await exists(agentHome(agent, home))) {
      found.push(agent);
    }
  }
  return found;
}

export type HookRemovalStatus =
  /** Removed now. */
  | 'removed'
  /** There was no hook of ours to remove. */
  | 'absent'
  /** The agent is not on this machine: its home directory does not exist. */
  | 'skipped'
  /** The config file could not be edited safely; the hook must be removed by hand. */
  | 'manual';

export interface HookRemoval {
  agent: HookAgent;
  file: string;
  status: HookRemovalStatus;
  note?: string;
}

/** Removes our commands from the SessionStart entries; entries and keys that empty out disappear with them. */
async function removeJsonHook(agent: 'claude' | 'codex', file: string): Promise<HookRemoval> {
  const json = await readJsonObject(file);
  if (json === undefined) {
    return { agent, file, status: 'absent' };
  }
  if (json === 'unparseable') {
    return { agent, file, status: 'manual', note: `not plain JSON; remove the "${INSTALL_MARKER}" hook by hand` };
  }
  const hooks = (json.hooks && typeof json.hooks === 'object' ? json.hooks : {}) as Record<string, unknown>;
  if (!hasInstallHook(hooks.SessionStart)) {
    return { agent, file, status: 'absent' };
  }
  const kept = (hooks.SessionStart as unknown[])
    .map(entry => {
      const commands = (entry as { hooks?: unknown })?.hooks;
      if (!Array.isArray(commands)) {
        return entry;
      }
      const remaining = commands.filter(
        hook =>
          !(
            typeof (hook as { command?: unknown })?.command === 'string' &&
            (hook as { command: string }).command.includes(INSTALL_MARKER)
          )
      );
      return remaining.length === commands.length ? entry : { ...(entry as object), hooks: remaining };
    })
    .filter(entry => {
      const commands = (entry as { hooks?: unknown })?.hooks;
      return !(Array.isArray(commands) && commands.length === 0);
    });
  const nextHooks: Record<string, unknown> = { ...hooks, SessionStart: kept };
  if (kept.length === 0) {
    delete nextHooks.SessionStart;
  }
  const next: Record<string, unknown> = { ...json, hooks: nextHooks };
  if (Object.keys(nextHooks).length === 0) {
    delete next.hooks;
  }
  await writeJson(file, next);
  return { agent, file, status: 'removed' };
}

/**
 * Only the exact block the installer appended is removed; a hand-edited hooks section stays, because
 * cutting lines out of someone's YAML risks breaking what they wrote around it.
 */
async function removeHermesHook(file: string): Promise<HookRemoval> {
  const agent = 'hermes';
  let text: string;
  try {
    text = await readFile(file, 'utf8');
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
      return { agent, file, status: 'absent' };
    }
    throw error;
  }
  if (!text.includes(INSTALL_MARKER)) {
    return { agent, file, status: 'absent' };
  }
  const block = hermesLines.join('\n');
  const index = text.indexOf(block);
  if (index === -1) {
    return {
      agent,
      file,
      status: 'manual',
      note: `the hooks were edited; remove the "${INSTALL_MARKER}" lines by hand`,
    };
  }
  let next = (text.slice(0, index) + text.slice(index + block.length)).replace(/\n{3,}/g, '\n\n').replace(/\n+$/, '\n');
  if (next.trim() === '') {
    next = '';
  }
  await writeFile(file, next, 'utf8');
  return { agent, file, status: 'removed' };
}

/** The hook folder is ours and is deleted outright; the config entry goes when the file is plain JSON. */
async function removeOpenclawHook(home: string): Promise<HookRemoval> {
  const agent = 'openclaw';
  const dir = join(home, 'hooks', OPENCLAW_HOOK);
  const configFile = join(home, 'openclaw.json');
  const hadFiles = await exists(dir);
  await rm(dir, { recursive: true, force: true });

  const json = await readJsonObject(configFile);
  if (json === 'unparseable') {
    return {
      agent,
      file: configFile,
      status: 'manual',
      note: `hook folder ${dir} removed; the config is not plain JSON, remove the "${OPENCLAW_HOOK}" entry by hand and restart the gateway`,
    };
  }
  const config = json ?? {};
  const hooks = (config.hooks && typeof config.hooks === 'object' ? config.hooks : {}) as Record<string, unknown>;
  const internal = (hooks.internal && typeof hooks.internal === 'object' ? hooks.internal : {}) as Record<
    string,
    unknown
  >;
  const entries = (internal.entries && typeof internal.entries === 'object' ? internal.entries : {}) as Record<
    string,
    unknown
  >;
  if (!(OPENCLAW_HOOK in entries)) {
    return { agent, file: configFile, status: hadFiles ? 'removed' : 'absent' };
  }
  const nextEntries = { ...entries };
  delete nextEntries[OPENCLAW_HOOK];
  await writeJson(configFile, {
    ...config,
    hooks: { ...hooks, internal: { ...internal, entries: nextEntries } },
  });
  return { agent, file: configFile, status: 'removed', note: 'restart the gateway to drop it' };
}

/** Removes the hook of one agent; skipped when the agent is not on this machine. */
export async function removeHook(agent: HookAgent, home = os.homedir()): Promise<HookRemoval> {
  const base = agentHome(agent, home);
  if (!(await exists(base))) {
    return { agent, file: base, status: 'skipped' };
  }
  switch (agent) {
    case 'claude':
      return removeJsonHook(agent, join(base, 'settings.json'));
    case 'codex':
      return removeJsonHook(agent, join(base, 'hooks.json'));
    case 'hermes':
      return removeHermesHook(join(base, 'config.yaml'));
    case 'openclaw':
      return removeOpenclawHook(base);
  }
}

/** Removes the hook from every agent found on this machine. */
export async function removeHooks(home = os.homedir()): Promise<HookRemoval[]> {
  const results: HookRemoval[] = [];
  for (const agent of HOOK_AGENTS) {
    results.push(await removeHook(agent, home));
  }
  return results;
}
