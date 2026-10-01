import {
  SkillNotFoundError,
  SkillsApiError,
  type SkillCollectionSummary,
  type SkillsApi,
  type SkillSummary,
  type SkillWithContent,
} from '../../src/actions/skills/api.js';

/** In-memory skills registry with the same rules as the backend that matter to sync, push and subscribe. */
export class FakeSkillsApi implements SkillsApi {
  private skills = new Map<string, SkillWithContent>();
  private collections = new Map<string, SkillCollectionSummary>();
  private counter = 0;
  public calls: string[] = [];
  private clock = Date.parse('2026-09-10T08:00:00.000Z');

  tick(): string {
    this.clock += 60_000;
    return new Date(this.clock).toISOString();
  }

  seedCollection(collection: { name: string; id?: string; description?: string }): SkillCollectionSummary {
    const now = this.tick();
    const full = {
      id: collection.id ?? `coll_${++this.counter}`,
      name: collection.name,
      description: collection.description ?? '',
      visibility: 'organization',
      createdByUserId: 'user_1',
      createdByUserName: 'Tester',
      createdByUserEmail: 'tester@example.com',
      sharedWithUserIds: [],
      sharedWithTeamIds: [],
      maintainerUserIds: [],
      maintainerTeamIds: [],
      skillCount: 0,
      createdAt: now,
      updatedAt: now,
    } as unknown as SkillCollectionSummary;
    this.collections.set(full.id, full);
    return full;
  }

  renameCollection(id: string, name: string): void {
    const collection = this.collections.get(id)!;
    this.collections.set(id, { ...collection, name, updatedAt: this.tick() } as SkillCollectionSummary);
    for (const [skillId, skill] of this.skills) {
      if (skill.collectionId === id) {
        this.skills.set(skillId, { ...skill, collectionName: name } as SkillWithContent);
      }
    }
  }

  removeCollection(id: string): void {
    this.collections.delete(id);
    for (const [skillId, skill] of this.skills) {
      if (skill.collectionId === id) {
        this.skills.set(skillId, { ...skill, collectionId: null, collectionName: null } as SkillWithContent);
      }
    }
  }

  seed(
    skill: Partial<SkillWithContent> & { name: string; content: string; collectionId?: string | null }
  ): SkillWithContent {
    const now = this.tick();
    const collection = skill.collectionId ? this.collections.get(skill.collectionId) : undefined;
    const full: SkillWithContent = {
      id: skill.id ?? `skill_${++this.counter}`,
      name: skill.name,
      description: skill.description ?? `Use for ${skill.name}`,
      visibility: skill.visibility ?? 'organization',
      collectionId: collection?.id ?? null,
      collectionName: collection?.name ?? null,
      contentBytes: Buffer.byteLength(skill.content),
      createdByUserId: 'user_1',
      createdByUserName: 'Tester',
      createdByUserEmail: 'tester@example.com',
      sharedWithUserIds: [],
      sharedWithTeamIds: [],
      maintainerUserIds: [],
      maintainerTeamIds: [],
      collectionVisibility: collection ? 'organization' : null,
      collectionSharedWithUserIds: [],
      collectionSharedWithTeamIds: [],
      collectionMaintainerUserIds: [],
      collectionMaintainerTeamIds: [],
      createdAt: now,
      updatedAt: skill.updatedAt ?? now,
      content: skill.content,
      markdown: `---\nname: ${skill.name}\ndescription: ${JSON.stringify(skill.description ?? `Use for ${skill.name}`)}\n---\n\n${skill.content}`,
      createdByName: 'Tester',
    } as unknown as SkillWithContent;
    this.skills.set(full.id, full);
    return full;
  }

  /** Simulates a change made elsewhere. */
  change(
    id: string,
    patch: Partial<Pick<SkillWithContent, 'name' | 'description' | 'content'>> & { collectionId?: string | null }
  ): SkillWithContent {
    const skill = this.skills.get(id)!;
    const { collectionId, ...rest } = patch;
    let placement = {};
    if (collectionId !== undefined) {
      const collection = collectionId ? this.collections.get(collectionId) : undefined;
      if (collectionId && !collection) {
        throw new SkillsApiError(400, 'Collection not found');
      }
      placement = { collectionId: collection?.id ?? null, collectionName: collection?.name ?? null };
    }
    const next = { ...skill, ...rest, ...placement, updatedAt: this.tick() } as SkillWithContent;
    this.skills.set(id, next);
    return next;
  }

  remove(id: string): void {
    this.skills.delete(id);
  }

  async list(query?: string, collection?: string): Promise<SkillSummary[]> {
    this.calls.push('list');
    const needle = query?.toLowerCase();
    return [...this.skills.values()]
      .filter(s => !needle || s.name.includes(needle) || s.description.toLowerCase().includes(needle))
      .filter(s => !collection || s.collectionName === collection)
      .sort((a, b) => a.name.localeCompare(b.name))
      .map(({ content, createdByName, markdown, ...summary }) => summary as SkillSummary);
  }

  async listCollections(): Promise<SkillCollectionSummary[]> {
    this.calls.push('listCollections');
    return [...this.collections.values()].sort((a, b) => a.name.localeCompare(b.name));
  }

  async get(id: string): Promise<SkillWithContent> {
    this.calls.push(`get ${id}`);
    const skill = this.skills.get(id);
    if (!skill) {
      throw new SkillNotFoundError(id);
    }
    return skill;
  }

  async create(body: {
    name: string;
    description: string;
    content: string;
    collectionId?: string | null;
  }): Promise<SkillSummary> {
    this.calls.push(`create ${body.name}`);
    if ([...this.skills.values()].some(s => s.name === body.name)) {
      throw new SkillsApiError(400, 'A skill with this name exists');
    }
    if (body.collectionId && !this.collections.has(body.collectionId)) {
      throw new SkillsApiError(400, 'Collection not found');
    }
    const { content, createdByName, markdown, ...summary } = this.seed(body);
    return summary as SkillSummary;
  }

  async update(
    id: string,
    body: { name?: string; description?: string; content?: string; collectionId?: string | null }
  ): Promise<SkillSummary> {
    this.calls.push(`update ${id}`);
    if (!this.skills.has(id)) {
      throw new SkillsApiError(400, 'Skill not found');
    }
    const { content, createdByName, markdown, ...summary } = this.change(id, body);
    return summary as SkillSummary;
  }
}
