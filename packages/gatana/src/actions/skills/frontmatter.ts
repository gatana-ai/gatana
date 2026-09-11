import yaml from 'js-yaml';
import { z } from 'zod';
import type { SkillSummary } from './api.js';

/** Metadata keys the sync writes so a file can be traced back to its skill, organization and revision. */
export const META_ID = 'gatana-id';
export const META_ORG = 'gatana-org';
export const META_UPDATED_AT = 'gatana-updated-at';

/** The same rule as the backend and the agentskills.io specification. */
export const SKILL_NAME_PATTERN = /^[a-z0-9]+(-[a-z0-9]+)*$/;

export interface SkillFrontmatter {
  name: string;
  description: string;
  /** String-to-string map per the specification. */
  metadata: Record<string, string>;
  /** Frontmatter keys this tool does not know (`license`, `allowed-tools`, ...), kept so a rewrite does not drop them. */
  extra: Record<string, unknown>;
}

export class SkillMdError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'SkillMdError';
  }
}

const KNOWN_KEYS = new Set(['name', 'description', 'metadata']);

const FrontmatterSchema = z.object({
  name: z
    .string()
    .min(1)
    .max(64)
    .regex(SKILL_NAME_PATTERN, 'lowercase letters, digits and single dashes, 1-64 characters'),
  description: z.string().min(1).max(1024),
  metadata: z
    .record(
      z.string(),
      z.union([z.string(), z.number(), z.boolean()]).transform(v => String(v))
    )
    .optional(),
});

/** One line: the backend treats the description as a one-liner and a multi-line scalar trips simple parsers. */
function collapse(text: string): string {
  return text.replace(/\s*\r?\n\s*/g, ' ').trim();
}

export function frontmatterFor(
  skill: Pick<SkillSummary, 'id' | 'name' | 'description' | 'updatedAt'>,
  orgId: string,
  extra: Record<string, unknown> = {},
  otherMetadata: Record<string, string> = {}
): SkillFrontmatter {
  const metadata: Record<string, string> = {};
  for (const [key, value] of Object.entries(otherMetadata)) {
    if (key !== META_ID && key !== META_ORG && key !== META_UPDATED_AT) {
      metadata[key] = value;
    }
  }
  metadata[META_ID] = skill.id;
  metadata[META_ORG] = orgId;
  metadata[META_UPDATED_AT] = new Date(skill.updatedAt as unknown as string).toISOString();
  return { name: skill.name, description: skill.description, metadata, extra };
}

/**
 * Renders a SKILL.md. The name is emitted bare because its pattern never needs quoting; every other
 * string is double-quoted on one line, so colons, `#`, quotes and angle brackets are safe for any
 * frontmatter parser. The body is written verbatim with one trailing newline.
 */
export function renderSkillMd(fm: SkillFrontmatter, body: string): string {
  const fields: Record<string, unknown> = { description: collapse(fm.description), ...fm.extra };
  if (Object.keys(fm.metadata).length > 0) {
    fields.metadata = fm.metadata;
  }
  const rest = yaml.dump(fields, { lineWidth: -1, quotingType: '"', forceQuotes: true, noRefs: true });
  const content = body.endsWith('\n') ? body : `${body}\n`;
  return `---\nname: ${fm.name}\n${rest}---\n\n${content}`;
}

const FRONTMATTER_RE = /^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)([\s\S]*)$/;

export function parseSkillMd(text: string): { frontmatter: SkillFrontmatter; body: string } {
  const match = FRONTMATTER_RE.exec(text);
  if (!match) {
    throw new SkillMdError('No frontmatter: the file must start with a --- block holding name and description');
  }
  let loaded: unknown;
  try {
    loaded = yaml.load(match[1], { schema: yaml.CORE_SCHEMA });
  } catch (error) {
    throw new SkillMdError(`Invalid frontmatter YAML: ${(error as Error).message}`);
  }
  if (typeof loaded !== 'object' || loaded === null || Array.isArray(loaded)) {
    throw new SkillMdError('Frontmatter must be a YAML mapping');
  }
  const parsed = FrontmatterSchema.safeParse(loaded);
  if (!parsed.success) {
    const issue = parsed.error.issues[0];
    throw new SkillMdError(`Invalid frontmatter: ${issue.path.join('.') || 'frontmatter'} ${issue.message}`);
  }
  const extra: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(loaded as Record<string, unknown>)) {
    if (!KNOWN_KEYS.has(key)) {
      extra[key] = value;
    }
  }
  // The render puts one blank line between the frontmatter and the body; take exactly that back.
  const body = match[2].replace(/^\r?\n/, '');
  if (body.trim().length === 0) {
    throw new SkillMdError('The skill has no instructions below the frontmatter');
  }
  return {
    frontmatter: {
      name: parsed.data.name,
      description: parsed.data.description,
      metadata: parsed.data.metadata ?? {},
      extra,
    },
    body,
  };
}
