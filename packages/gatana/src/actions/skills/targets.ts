import { mkdir, realpath } from 'fs/promises';
import os from 'os';
import { isAbsolute, resolve } from 'path';

/** Where the agent frameworks look for user-level skills. */
export const PRESETS: Record<string, { dir: string; readers: string }> = {
  claude: { dir: '~/.claude/skills', readers: 'Claude Code' },
  agents: { dir: '~/.agents/skills', readers: 'Codex, Cursor, Gemini CLI, OpenCode, Copilot, Amp' },
  hermes: { dir: '~/.hermes/skills', readers: 'Hermes Agent' },
};

export const DEFAULT_TARGETS = ['claude', 'agents'];

export function presetHelp(): string {
  return Object.entries(PRESETS)
    .map(([name, p]) => `${name} (${p.dir}, read by ${p.readers})`)
    .join('; ');
}

export function expandHome(path: string, home = os.homedir()): string {
  if (path === '~') {
    return home;
  }
  if (path.startsWith('~/')) {
    return resolve(home, path.slice(2));
  }
  return isAbsolute(path) ? path : resolve(path);
}

/** Presets become their directory; anything else is a path. */
export function resolveTargets(args: string[], home = os.homedir()): string[] {
  const names = args.length > 0 ? args : DEFAULT_TARGETS;
  return names.map(name => expandHome(PRESETS[name]?.dir ?? name, home));
}

/**
 * Creates the directories and collapses aliases: `~/.agents/skills` is often a symlink to
 * `~/.claude/skills`, and syncing the same folder twice would make the second pass see the first
 * pass's folders as foreign.
 */
export async function prepareTargets(dirs: string[]): Promise<string[]> {
  const seen = new Set<string>();
  const result: string[] = [];
  for (const dir of dirs) {
    await mkdir(dir, { recursive: true });
    const real = await realpath(dir);
    if (!seen.has(real)) {
      seen.add(real);
      result.push(real);
    }
  }
  return result;
}

/**
 * Collapses aliases like prepareTargets, but creates nothing: a folder that does not exist is kept
 * under its given path, so the caller can report it as not installed.
 */
export async function collapseTargets(dirs: string[]): Promise<string[]> {
  const seen = new Set<string>();
  const result: string[] = [];
  for (const dir of dirs) {
    let real = dir;
    try {
      real = await realpath(dir);
    } catch {
      // Not there: nothing to collapse.
    }
    if (!seen.has(real)) {
      seen.add(real);
      result.push(real);
    }
  }
  return result;
}
