import type { SkillSummary } from './api.js';
import type { ManifestEntry } from './manifest.js';

export type SyncOp =
  | { kind: 'write'; id: string; name: string; reason: 'new' | 'changed' | 'renamed' | 'missing-locally' }
  | { kind: 'remove'; id: string; name: string; reason: 'renamed' | 'pruned' }
  | { kind: 'skip'; id: string; name: string; reason: 'unchanged' | 'foreign-folder' | 'local-edits' | 'kept' };

export interface LocalState {
  /** Names of the folders in the directory, symlinks included. */
  dirs: Set<string>;
  /** sha256 of `<folder>/SKILL.md` for the folders that have one. */
  hashes: Map<string, string>;
}

/**
 * Decides what a sync does, from the remote list, the manifest and what is on disk. Pure, so the
 * cases are testable without a filesystem. Removals must run before writes: a renamed skill
 * frees its old folder and may take a name another entry just freed.
 */
export function computeSyncPlan(input: {
  remote: SkillSummary[];
  manifest: Record<string, ManifestEntry>;
  local: LocalState;
  prune: boolean;
  force: boolean;
}): SyncOp[] {
  const { remote, manifest, local, prune, force } = input;
  const ops: SyncOp[] = [];
  const ownedNames = new Set(Object.values(manifest).map(entry => entry.name));
  // A folder we did not create, and no manifest entry is about to free it.
  const isForeign = (name: string) => local.dirs.has(name) && !ownedNames.has(name);

  const remoteIds = new Set<string>();
  for (const skill of remote) {
    remoteIds.add(skill.id);
    const entry = manifest[skill.id];
    const updatedAt = new Date(skill.updatedAt as unknown as string).toISOString();

    if (!entry) {
      if (isForeign(skill.name) && !force) {
        ops.push({ kind: 'skip', id: skill.id, name: skill.name, reason: 'foreign-folder' });
      } else {
        ops.push({ kind: 'write', id: skill.id, name: skill.name, reason: 'new' });
      }
      continue;
    }

    if (entry.name !== skill.name) {
      ops.push({ kind: 'remove', id: skill.id, name: entry.name, reason: 'renamed' });
      if (isForeign(skill.name) && !force) {
        ops.push({ kind: 'skip', id: skill.id, name: skill.name, reason: 'foreign-folder' });
      } else {
        ops.push({ kind: 'write', id: skill.id, name: skill.name, reason: 'renamed' });
      }
      continue;
    }

    if (!local.dirs.has(skill.name) || !local.hashes.has(skill.name)) {
      ops.push({ kind: 'write', id: skill.id, name: skill.name, reason: 'missing-locally' });
      continue;
    }

    if (local.hashes.get(skill.name) !== entry.hash) {
      if (force) {
        ops.push({ kind: 'write', id: skill.id, name: skill.name, reason: 'changed' });
      } else {
        ops.push({ kind: 'skip', id: skill.id, name: skill.name, reason: 'local-edits' });
      }
      continue;
    }

    if (entry.updatedAt !== updatedAt) {
      ops.push({ kind: 'write', id: skill.id, name: skill.name, reason: 'changed' });
    } else {
      ops.push({ kind: 'skip', id: skill.id, name: skill.name, reason: 'unchanged' });
    }
  }

  // Deleted, unshared, made private, or filtered out by a query: no longer listed.
  for (const [id, entry] of Object.entries(manifest)) {
    if (!remoteIds.has(id)) {
      ops.push(
        prune
          ? { kind: 'remove', id, name: entry.name, reason: 'pruned' }
          : { kind: 'skip', id, name: entry.name, reason: 'kept' }
      );
    }
  }

  return ops;
}
