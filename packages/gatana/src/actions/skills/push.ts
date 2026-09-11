import { readdir, readFile, stat, writeFile } from 'fs/promises';
import { basename, dirname, join, resolve } from 'path';
import { SkillNotFoundError, type SkillsApi, type SkillSummary, type SkillWithContent } from './api.js';
import { frontmatterFor, META_ID, META_ORG, META_UPDATED_AT, parseSkillMd, renderSkillMd } from './frontmatter.js';
import { readManifest, sha256, writeManifest } from './manifest.js';
import type { SkillsIdentity } from './sync.js';

const SKILL_FILE = 'SKILL.md';

export interface PushOptions {
  force: boolean;
  dryRun: boolean;
}

export type PushAction = 'created' | 'updated' | 'unchanged' | 'conflict' | 'error';

export interface PushResult {
  file: string;
  name: string;
  action: PushAction;
  detail: string;
}

/** A SKILL.md, a folder holding one, or a directory of such folders. */
export async function discoverSkillFiles(path: string): Promise<string[]> {
  const target = resolve(path);
  const info = await stat(target);
  if (info.isFile()) {
    return [target];
  }
  const own = join(target, SKILL_FILE);
  try {
    if ((await stat(own)).isFile()) {
      return [own];
    }
  } catch {
    // Not a skill folder itself; look one level down.
  }
  const files: string[] = [];
  for (const entry of await readdir(target, { withFileTypes: true })) {
    if (!entry.isDirectory() && !entry.isSymbolicLink()) {
      continue;
    }
    const candidate = join(target, entry.name, SKILL_FILE);
    try {
      if ((await stat(candidate)).isFile()) {
        files.push(candidate);
      }
    } catch {
      // A folder without a SKILL.md is not a skill.
    }
  }
  if (files.length === 0) {
    throw new Error(`No SKILL.md found at ${target}, in it, or in its sub-folders`);
  }
  return files.sort();
}

function sameText(a: string, b: string): boolean {
  return a.replace(/\s+$/, '') === b.replace(/\s+$/, '');
}

export async function pushSkills(
  api: SkillsApi,
  identity: SkillsIdentity,
  path: string,
  options: PushOptions
): Promise<PushResult[]> {
  const files = await discoverSkillFiles(path);
  let listing: Promise<SkillSummary[]> | undefined;
  const list = () => (listing ??= api.list());

  const results: PushResult[] = [];
  for (const file of files) {
    results.push(await pushOne(api, identity, file, options, list));
  }
  return results;
}

async function pushOne(
  api: SkillsApi,
  identity: SkillsIdentity,
  file: string,
  options: PushOptions,
  list: () => Promise<SkillSummary[]>
): Promise<PushResult> {
  let parsed;
  try {
    parsed = parseSkillMd(await readFile(file, 'utf8'));
  } catch (error) {
    return { file, name: basename(dirname(file)), action: 'error', detail: (error as Error).message };
  }
  const { frontmatter, body } = parsed;
  const name = frontmatter.name;
  const notes: string[] = [];
  if (basename(dirname(file)) !== name) {
    notes.push(`folder is named ${basename(dirname(file))}, the skill ${name}`);
  }

  const metaOrg = frontmatter.metadata[META_ORG];
  if (metaOrg && metaOrg !== identity.orgId && !options.force) {
    return {
      file,
      name,
      action: 'error',
      detail: `belongs to organization ${metaOrg}, not ${identity.orgId}; use --org ${metaOrg} or --force to create a copy here`,
    };
  }
  const metaId = metaOrg === identity.orgId || !metaOrg ? frontmatter.metadata[META_ID] : undefined;

  // The manifest of the directory the folder sits in, when the folder came from a sync.
  const manifestDir = dirname(dirname(file));
  const manifest = await readManifest(manifestDir).catch(() => undefined);

  let remote: SkillWithContent | undefined;
  if (metaId) {
    try {
      remote = await api.get(metaId);
    } catch (error) {
      if (!(error instanceof SkillNotFoundError)) {
        throw error;
      }
    }
  }
  if (!remote) {
    const byName = (await list()).find(skill => skill.name === name);
    if (byName) {
      remote = await api.get(byName.id);
    }
  }

  let result: SkillSummary;
  let action: PushAction;
  if (remote) {
    const remoteUpdatedAt = new Date(remote.updatedAt as unknown as string).toISOString();
    const baseline = manifest?.skills[remote.id]?.updatedAt ?? frontmatter.metadata[META_UPDATED_AT];
    if (!options.force) {
      if (!baseline) {
        return {
          file,
          name,
          action: 'conflict',
          detail: `a skill named ${name} exists and this file has no sync baseline; run "gatana skills sync" first, or --force to overwrite`,
        };
      }
      if (remoteUpdatedAt > baseline) {
        return {
          file,
          name,
          action: 'conflict',
          detail: `changed on the server at ${remoteUpdatedAt}, after your copy (${baseline}); sync first, or --force to overwrite`,
        };
      }
    }
    const unchanged =
      remote.name === name && sameText(remote.description, frontmatter.description) && sameText(remote.content, body);
    if (unchanged) {
      result = remote;
      action = 'unchanged';
    } else if (options.dryRun) {
      return { file, name, action: 'updated', detail: ['would update', ...notes].join('; ') };
    } else {
      result = await api.update(remote.id, { name, description: frontmatter.description, content: body });
      action = 'updated';
    }
  } else if (options.dryRun) {
    return { file, name, action: 'created', detail: ['would create', ...notes].join('; ') };
  } else {
    result = await api.create({ name, description: frontmatter.description, content: body });
    action = 'created';
  }

  // Stamp the file with the revision it now matches, keeping any other frontmatter untouched.
  const text = renderSkillMd(frontmatterFor(result, identity.orgId, frontmatter.extra, frontmatter.metadata), body);
  if (!options.dryRun) {
    await writeFile(file, text, 'utf8');
    if (manifest && manifest.orgId === identity.orgId) {
      manifest.skills[result.id] = {
        name: result.name,
        updatedAt: new Date(result.updatedAt as unknown as string).toISOString(),
        hash: sha256(text),
      };
      await writeManifest(manifestDir, manifest);
    }
  }

  return { file, name, action, detail: notes.join('; ') };
}
