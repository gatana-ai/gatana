import { lstat, mkdir, readdir, readFile, rename, rm, rmdir, writeFile } from 'fs/promises';
import { join } from 'path';
import { SkillNotFoundError, type SkillsApi, type SkillSummary } from './api.js';
import { frontmatterFor, renderSkillMd } from './frontmatter.js';
import {
  emptyManifest,
  readManifest,
  sha256,
  writeManifest,
  type SkillsManifest,
  type Subscription,
} from './manifest.js';
import { computeSyncPlan, type LocalState, type SyncOp } from './plan.js';

export interface SkillsIdentity {
  orgId: string;
  baseUrl: string;
}

export interface SyncOptions {
  dryRun: boolean;
  prune: boolean;
  force: boolean;
  query?: string;
  /** Add this collection or skill to the directory's subscriptions before syncing. */
  subscribe?: Subscription;
  /** Forget the subscriptions first: the directory takes every readable skill again. */
  everything?: boolean;
}

export interface SyncSummary {
  dir: string;
  ops: SyncOp[];
  written: number;
  removed: number;
  skipped: number;
  /** Skills the manifest owns after the run. */
  total: number;
  /** The collections the directory follows, or null when it takes every readable skill. */
  subscriptions: Subscription[] | null;
  warnings: string[];
}

/**
 * What the directory should hold. Without subscriptions: every skill the user can read. With
 * them: the skills of the subscribed collections and the subscribed skills themselves, from the one
 * list the server gives, matched by id, so a rename on the server is followed and reported rather
 * than breaking the sync. A collection or skill that is gone, or no longer shared with the user,
 * contributes nothing and is reported; its entry stays so the user sees it in the next message and
 * can be reset with --everything.
 */
async function listRemote(
  api: SkillsApi,
  manifest: SkillsManifest,
  options: SyncOptions,
  warnings: string[]
): Promise<{ remote: SkillSummary[]; subscriptions: Subscription[] | null }> {
  const all = await api.list(options.query);
  if (manifest.subscriptions === null) {
    return { remote: all, subscriptions: null };
  }
  const collections = new Map((await api.listCollections()).map(collection => [collection.id, collection]));
  const skills = new Map(all.map(skill => [skill.id, skill]));
  const subscriptions: Subscription[] = [];
  const wanted = new Set<string>();
  const wantedSkills = new Set<string>();
  for (const subscription of manifest.subscriptions) {
    const current = subscription.kind === 'skill' ? skills.get(subscription.id) : collections.get(subscription.id);
    if (!current) {
      warnings.push(
        `${subscription.kind} "${subscription.name}" is gone or no longer shared with you; ${subscription.kind === 'skill' ? 'it is' : 'its skills are'} removed. Run "gatana skills install --everything" to reset what the directory follows`
      );
      subscriptions.push(subscription);
      continue;
    }
    if (current.name !== subscription.name) {
      warnings.push(`${subscription.kind} "${subscription.name}" is now named "${current.name}"`);
    }
    subscriptions.push({ kind: subscription.kind, id: current.id, name: current.name });
    (subscription.kind === 'skill' ? wantedSkills : wanted).add(current.id);
  }
  return {
    remote: all.filter(
      skill => wantedSkills.has(skill.id) || (skill.collectionId !== null && wanted.has(skill.collectionId))
    ),
    subscriptions,
  };
}

const SKILL_FILE = 'SKILL.md';
const FETCH_CONCURRENCY = 4;

async function readLocalState(dir: string): Promise<LocalState> {
  const dirs = new Set<string>();
  const hashes = new Map<string, string>();
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    if (!entry.isDirectory() && !entry.isSymbolicLink()) {
      continue;
    }
    dirs.add(entry.name);
    try {
      hashes.set(entry.name, sha256(await readFile(join(dir, entry.name, SKILL_FILE), 'utf8')));
    } catch {
      // A folder without a SKILL.md, or one we may not read: known as a folder, unknown as a skill.
    }
  }
  return { dirs, hashes };
}

async function writeAtomic(path: string, text: string): Promise<void> {
  const tmp = `${path}.${process.pid}.tmp`;
  await writeFile(tmp, text, 'utf8');
  await rename(tmp, path);
}

/** Removes the SKILL.md and the folder when nothing else is in it. Never follows a symlink. */
async function removeSkillFolder(dir: string, name: string, warnings: string[]): Promise<void> {
  const folder = join(dir, name);
  let stat;
  try {
    stat = await lstat(folder);
  } catch {
    return;
  }
  if (stat.isSymbolicLink()) {
    warnings.push(`${folder} is a symlink; left in place`);
    return;
  }
  await rm(join(folder, SKILL_FILE), { force: true });
  try {
    await rmdir(folder);
  } catch {
    warnings.push(`${folder} kept: it holds files the sync did not write`);
  }
}

async function mapLimit<T, R>(items: T[], limit: number, fn: (item: T) => Promise<R>): Promise<R[]> {
  const results: R[] = new Array(items.length);
  let next = 0;
  const workers = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (next < items.length) {
      const index = next++;
      results[index] = await fn(items[index]);
    }
  });
  await Promise.all(workers);
  return results;
}

export async function syncDirectory(
  api: SkillsApi,
  identity: SkillsIdentity,
  dir: string,
  options: SyncOptions
): Promise<SyncSummary> {
  await mkdir(dir, { recursive: true });
  const warnings: string[] = [];

  let manifest = (await readManifest(dir)) ?? emptyManifest(identity.orgId, identity.baseUrl);
  if (manifest.orgId !== identity.orgId || manifest.baseUrl !== identity.baseUrl) {
    if (!options.force) {
      throw new Error(
        `${dir} is synced from ${manifest.orgId} (${manifest.baseUrl}). Pass --force to switch it to ${identity.orgId} (${identity.baseUrl}); the old folders stay and become foreign`
      );
    }
    warnings.push(
      `${dir}: switched from ${manifest.orgId} to ${identity.orgId}; the earlier folders are no longer owned`
    );
    manifest = emptyManifest(identity.orgId, identity.baseUrl);
  }

  // Subscription changes ride on the sync so a dry run previews them without writing anything:
  // the changed list only reaches the manifest through the write at the end.
  if (options.everything) {
    manifest = { ...manifest, subscriptions: null };
  }
  if (options.subscribe) {
    const current = manifest.subscriptions ?? [];
    if (!current.some(subscription => subscription.id === options.subscribe!.id)) {
      manifest = { ...manifest, subscriptions: [...current, options.subscribe] };
    }
  }

  const { remote, subscriptions } = await listRemote(api, manifest, options, warnings);
  const local = await readLocalState(dir);
  const ops = computeSyncPlan({
    remote,
    manifest: manifest.skills,
    local,
    prune: options.prune,
    force: options.force,
  });

  const summary = (total: number): SyncSummary => ({
    dir,
    ops,
    written: ops.filter(op => op.kind === 'write').length,
    removed: ops.filter(op => op.kind === 'remove').length,
    skipped: ops.filter(op => op.kind === 'skip').length,
    total,
    subscriptions,
    warnings,
  });

  for (const op of ops) {
    if (op.kind === 'skip' && op.reason === 'foreign-folder') {
      warnings.push(
        `${join(dir, op.name)} exists but was not created by this sync; skipped (use --force to take it over)`
      );
    }
    if (op.kind === 'skip' && op.reason === 'local-edits') {
      warnings.push(
        `${join(dir, op.name, SKILL_FILE)} was edited locally; skipped (push it, or use --force to overwrite)`
      );
    }
  }

  if (options.dryRun) {
    return summary(Object.keys(manifest.skills).length);
  }

  for (const op of ops) {
    if (op.kind === 'remove') {
      await removeSkillFolder(dir, op.name, warnings);
    }
  }

  const next: SkillsManifest = {
    ...manifest,
    syncedAt: new Date().toISOString(),
    skills: {},
    subscriptions,
  };
  for (const op of ops) {
    if (op.kind === 'skip' && op.reason !== 'foreign-folder' && manifest.skills[op.id]) {
      next.skills[op.id] = manifest.skills[op.id];
    }
  }

  const writes = ops.filter((op): op is Extract<SyncOp, { kind: 'write' }> => op.kind === 'write');
  await mapLimit(writes, FETCH_CONCURRENCY, async op => {
    let skill;
    try {
      skill = await api.get(op.id);
    } catch (error) {
      if (error instanceof SkillNotFoundError) {
        warnings.push(`${op.name} disappeared between listing and reading; skipped`);
        if (manifest.skills[op.id]) {
          next.skills[op.id] = manifest.skills[op.id];
        }
        return;
      }
      throw error;
    }
    const text = renderSkillMd(frontmatterFor(skill, identity.orgId), skill.content);
    const folder = join(dir, skill.name);
    await mkdir(folder, { recursive: true });
    await writeAtomic(join(folder, SKILL_FILE), text);
    next.skills[skill.id] = {
      name: skill.name,
      updatedAt: new Date(skill.updatedAt as unknown as string).toISOString(),
      hash: sha256(text),
    };
  });

  await writeManifest(dir, next);
  return summary(Object.keys(next.skills).length);
}

export async function syncTargets(
  api: SkillsApi,
  identity: SkillsIdentity,
  dirs: string[],
  options: SyncOptions
): Promise<SyncSummary[]> {
  const summaries: SyncSummary[] = [];
  for (const dir of dirs) {
    summaries.push(await syncDirectory(api, identity, dir, options));
  }
  return summaries;
}

function sleep(ms: number, signal: AbortSignal): Promise<void> {
  return new Promise(resolve => {
    if (signal.aborted) {
      return resolve();
    }
    const timer = setTimeout(resolve, ms);
    signal.addEventListener(
      'abort',
      () => {
        clearTimeout(timer);
        resolve();
      },
      { once: true }
    );
  });
}

/** Re-syncs every interval until the signal aborts. A failed pass is reported and the next one still runs. */
export async function watchSync(
  api: SkillsApi,
  identity: SkillsIdentity,
  dirs: string[],
  options: SyncOptions,
  intervalSeconds: number,
  signal: AbortSignal,
  report: (summaries: SyncSummary[]) => void,
  reportError: (error: unknown) => void
): Promise<void> {
  while (!signal.aborted) {
    try {
      report(await syncTargets(api, identity, dirs, options));
    } catch (error) {
      reportError(error);
    }
    await sleep(intervalSeconds * 1000, signal);
  }
}
