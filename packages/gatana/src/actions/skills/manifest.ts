import { createHash } from 'crypto';
import { mkdir, readFile, rename, writeFile } from 'fs/promises';
import { join } from 'path';
import { z } from 'zod';

/**
 * Sits in every synced directory and records which skill folders the sync owns, and which
 * collections and skills the directory is subscribed to. Everything not in it is somebody else's and is never
 * touched. One directory serves one organization.
 */
export const MANIFEST_FILE = '.gatana-skills.json';

const ManifestEntrySchema = z.object({
  name: z.string(),
  updatedAt: z.string(),
  /** sha256 of the SKILL.md as written, to notice local edits before overwriting them. */
  hash: z.string(),
});
export type ManifestEntry = z.infer<typeof ManifestEntrySchema>;

/**
 * A collection or a single skill the directory follows. The id is what is followed; the name is
 * what was last seen, for messages. Manifests written before skills could be followed carry no
 * kind: they followed collections only.
 */
const SubscriptionSchema = z.object({
  kind: z.enum(['collection', 'skill']).default('collection'),
  id: z.string(),
  name: z.string(),
});
export type Subscription = z.infer<typeof SubscriptionSchema>;

const ManifestV1Schema = z.object({
  version: z.literal(1),
  orgId: z.string(),
  baseUrl: z.string(),
  syncedAt: z.string(),
  skills: z.record(z.string(), ManifestEntrySchema),
});

/**
 * Version 2 adds the subscriptions. Null means the directory takes every skill the user can read
 * (what version 1 always did); a list, even an empty one, means only the skills of those
 * collections. The distinction matters when the list is empty: the directory must not flip to
 * everything on its own.
 */
const ManifestSchema = ManifestV1Schema.extend({
  version: z.literal(2),
  subscriptions: z.array(SubscriptionSchema).nullable(),
});
export type SkillsManifest = z.infer<typeof ManifestSchema>;

export class ManifestError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ManifestError';
  }
}

export function emptyManifest(orgId: string, baseUrl: string): SkillsManifest {
  return { version: 2, orgId, baseUrl, syncedAt: new Date(0).toISOString(), skills: {}, subscriptions: null };
}

/**
 * Missing file: undefined. A version 1 file is read as version 2 without subscriptions. Unreadable
 * content: an error, on purpose. Treating a broken manifest as empty would make every owned folder
 * foreign, or with --force deletable.
 */
export async function readManifest(dir: string): Promise<SkillsManifest | undefined> {
  const path = join(dir, MANIFEST_FILE);
  let text: string;
  try {
    text = await readFile(path, 'utf8');
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
      return undefined;
    }
    throw error;
  }
  let json: unknown;
  try {
    json = JSON.parse(text);
  } catch {
    throw new ManifestError(`${path} is not valid JSON. Fix or delete it, then sync again`);
  }
  const parsed = ManifestSchema.safeParse(json);
  if (parsed.success) {
    return parsed.data;
  }
  const v1 = ManifestV1Schema.safeParse(json);
  if (v1.success) {
    return { ...v1.data, version: 2, subscriptions: null };
  }
  throw new ManifestError(`${path} has an unexpected shape. Fix or delete it, then sync again`);
}

export async function writeManifest(dir: string, manifest: SkillsManifest): Promise<void> {
  await mkdir(dir, { recursive: true });
  const path = join(dir, MANIFEST_FILE);
  const tmp = `${path}.${process.pid}.tmp`;
  await writeFile(tmp, `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');
  await rename(tmp, path);
}

export function sha256(text: string): string {
  return createHash('sha256').update(text, 'utf8').digest('hex');
}
