import { createHash } from 'crypto';
import { mkdir, readFile, rename, writeFile } from 'fs/promises';
import { join } from 'path';
import { z } from 'zod';

/**
 * Sits in every synced directory and records which skill folders the sync owns. Everything not in
 * it is somebody else's and is never touched. One directory serves one organization.
 */
export const MANIFEST_FILE = '.gatana-skills.json';

const ManifestEntrySchema = z.object({
  name: z.string(),
  updatedAt: z.string(),
  /** sha256 of the SKILL.md as written, to notice local edits before overwriting them. */
  hash: z.string(),
});
export type ManifestEntry = z.infer<typeof ManifestEntrySchema>;

const ManifestSchema = z.object({
  version: z.literal(1),
  orgId: z.string(),
  baseUrl: z.string(),
  syncedAt: z.string(),
  skills: z.record(z.string(), ManifestEntrySchema),
});
export type SkillsManifest = z.infer<typeof ManifestSchema>;

export class ManifestError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ManifestError';
  }
}

export function emptyManifest(orgId: string, baseUrl: string): SkillsManifest {
  return { version: 1, orgId, baseUrl, syncedAt: new Date(0).toISOString(), skills: {} };
}

/**
 * Missing file: undefined. Unreadable content: an error, on purpose. Treating a broken manifest as
 * empty would make every owned folder foreign, or with --force deletable.
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
  if (!parsed.success) {
    throw new ManifestError(`${path} has an unexpected shape. Fix or delete it, then sync again`);
  }
  return parsed.data;
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
