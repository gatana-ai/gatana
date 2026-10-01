import { readdir, readFile, realpath, stat, writeFile } from 'fs/promises';
import { basename, dirname, join, resolve } from 'path';
import { SkillNotFoundError, type SkillsApi, type SkillSummary, type SkillWithContent } from './api.js';
import {
  frontmatterFor,
  META_COLLECTION,
  META_ID,
  META_ORG,
  META_UPDATED_AT,
  parseSkillMd,
  renderSkillMd,
} from './frontmatter.js';
import { readManifest, sha256, writeManifest } from './manifest.js';
import type { SkillsIdentity } from './sync.js';

const SKILL_FILE = 'SKILL.md';

export interface PushOptions {
  force: boolean;
  dryRun: boolean;
  /**
   * Name of the collection to put the pushed skills in. Without it, a file that names one in its
   * `gatana-collection` metadata goes there, so a synced file stays in its collection; a file
   * naming none is created at root and an existing skill keeps its place.
   */
  collection?: string;
  /**
   * A path holding no skill is skipped instead of refused. Set when the paths are the default
   * sync targets rather than something the user typed: an agent folder that does not exist yet, or
   * holds nothing, is no mistake then.
   */
  skipEmpty?: boolean;
}

/** Collection ids by name, fetched once per push and only when a file or the option asks for one. */
class CollectionResolver {
  private byName: Promise<Map<string, string>> | undefined;
  constructor(private readonly api: SkillsApi) {}

  async idOf(name: string): Promise<string | undefined> {
    this.byName ??= this.api
      .listCollections()
      .then(collections => new Map(collections.map(collection => [collection.name, collection.id])));
    return (await this.byName).get(name);
  }
}

export type PushAction = 'created' | 'updated' | 'unchanged' | 'conflict' | 'error';

export interface PushResult {
  file: string;
  name: string;
  action: PushAction;
  detail: string;
}

/** A SKILL.md, a folder holding one, or a directory of such folders. */
export async function discoverSkillFiles(path: string, skipEmpty = false): Promise<string[]> {
  const target = resolve(path);
  let info;
  try {
    info = await stat(target);
  } catch (error) {
    if (skipEmpty) {
      return [];
    }
    throw error;
  }
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
  if (files.length === 0 && !skipEmpty) {
    throw new Error(`No SKILL.md found at ${target}, in it, or in its sub-folders`);
  }
  return files.sort();
}

/**
 * The files of every path, each once. Two paths may be the same folder under two names
 * (`~/.agents/skills` is often a symlink to `~/.claude/skills`), and pushing a file twice would
 * report the second pass as unchanged at best.
 */
async function discoverAll(paths: string[], skipEmpty: boolean): Promise<string[]> {
  const seen = new Set<string>();
  const files: string[] = [];
  for (const path of paths) {
    for (const file of await discoverSkillFiles(path, skipEmpty)) {
      const real = await realpath(file);
      if (!seen.has(real)) {
        seen.add(real);
        files.push(file);
      }
    }
  }
  return files;
}

function sameText(a: string, b: string): boolean {
  return a.replace(/\s+$/, '') === b.replace(/\s+$/, '');
}

export async function pushSkills(
  api: SkillsApi,
  identity: SkillsIdentity,
  paths: string[],
  options: PushOptions
): Promise<PushResult[]> {
  const files = await discoverAll(paths, Boolean(options.skipEmpty));
  let listing: Promise<SkillSummary[]> | undefined;
  const list = () => (listing ??= api.list());
  const collections = new CollectionResolver(api);
  if (options.collection !== undefined && (await collections.idOf(options.collection)) === undefined) {
    throw new Error(`No collection named "${options.collection}" that you can see`);
  }

  const results: PushResult[] = [];
  for (const file of files) {
    results.push(await pushOne(api, identity, file, options, list, collections));
  }
  return results;
}

async function pushOne(
  api: SkillsApi,
  identity: SkillsIdentity,
  file: string,
  options: PushOptions,
  list: () => Promise<SkillSummary[]>,
  collections: CollectionResolver
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

  // Where the skill goes: the option first, else the collection the file names. Undefined leaves an
  // existing skill where it is and creates a new one at root.
  let collectionId: string | undefined;
  const collectionName = options.collection ?? frontmatter.metadata[META_COLLECTION];
  if (collectionName !== undefined) {
    collectionId = await collections.idOf(collectionName);
    if (collectionId === undefined) {
      notes.push(`collection "${collectionName}" not found; left where it is`);
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
          detail: `a skill named ${name} exists and this file has no install baseline; run "gatana skills install" first, or --force to overwrite`,
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
    const moves = collectionId !== undefined && collectionId !== remote.collectionId;
    const unchanged =
      remote.name === name &&
      sameText(remote.description, frontmatter.description) &&
      sameText(remote.content, body) &&
      !moves;
    if (unchanged) {
      result = remote;
      action = 'unchanged';
    } else if (options.dryRun) {
      return { file, name, action: 'updated', detail: ['would update', ...notes].join('; ') };
    } else {
      result = await api.update(remote.id, {
        name,
        description: frontmatter.description,
        content: body,
        ...(moves ? { collectionId } : {}),
      });
      action = 'updated';
    }
  } else if (options.dryRun) {
    return { file, name, action: 'created', detail: ['would create', ...notes].join('; ') };
  } else {
    result = await api.create({
      name,
      description: frontmatter.description,
      content: body,
      ...(collectionId !== undefined ? { collectionId } : {}),
    });
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
