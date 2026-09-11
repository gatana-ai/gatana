import {
  SkillNotFoundError,
  SkillsApiError,
  type SkillsApi,
  type SkillSummary,
  type SkillWithContent,
} from '../../src/actions/skills/api.js';

/** In-memory skills registry with the same rules as the backend that matter to sync and push. */
export class FakeSkillsApi implements SkillsApi {
  private skills = new Map<string, SkillWithContent>();
  private counter = 0;
  public calls: string[] = [];
  private clock = Date.parse('2026-09-10T08:00:00.000Z');

  tick(): string {
    this.clock += 60_000;
    return new Date(this.clock).toISOString();
  }

  seed(skill: Partial<SkillWithContent> & { name: string; content: string }): SkillWithContent {
    const now = this.tick();
    const full: SkillWithContent = {
      id: skill.id ?? `skill_${++this.counter}`,
      name: skill.name,
      description: skill.description ?? `Use for ${skill.name}`,
      visibility: skill.visibility ?? 'organization',
      contentBytes: Buffer.byteLength(skill.content),
      createdByUserId: 'user_1',
      createdByUserName: 'Tester',
      createdByUserEmail: 'tester@example.com',
      sharedWithUserIds: [],
      sharedWithTeamIds: [],
      createdAt: now,
      updatedAt: skill.updatedAt ?? now,
      content: skill.content,
      createdByName: 'Tester',
    } as SkillWithContent;
    this.skills.set(full.id, full);
    return full;
  }

  /** Simulates a change made elsewhere. */
  change(id: string, patch: Partial<Pick<SkillWithContent, 'name' | 'description' | 'content'>>): SkillWithContent {
    const skill = this.skills.get(id)!;
    const next = { ...skill, ...patch, updatedAt: this.tick() } as SkillWithContent;
    this.skills.set(id, next);
    return next;
  }

  remove(id: string): void {
    this.skills.delete(id);
  }

  async list(query?: string): Promise<SkillSummary[]> {
    this.calls.push('list');
    const needle = query?.toLowerCase();
    return [...this.skills.values()]
      .filter(s => !needle || s.name.includes(needle) || s.description.toLowerCase().includes(needle))
      .sort((a, b) => a.name.localeCompare(b.name))
      .map(({ content, createdByName, ...summary }) => summary as SkillSummary);
  }

  async get(id: string): Promise<SkillWithContent> {
    this.calls.push(`get ${id}`);
    const skill = this.skills.get(id);
    if (!skill) {
      throw new SkillNotFoundError(id);
    }
    return skill;
  }

  async create(body: { name: string; description: string; content: string }): Promise<SkillSummary> {
    this.calls.push(`create ${body.name}`);
    if ([...this.skills.values()].some(s => s.name === body.name)) {
      throw new SkillsApiError(400, 'A skill with this name exists');
    }
    const { content, createdByName, ...summary } = this.seed(body);
    return summary as SkillSummary;
  }

  async update(id: string, body: { name?: string; description?: string; content?: string }): Promise<SkillSummary> {
    this.calls.push(`update ${id}`);
    if (!this.skills.has(id)) {
      throw new SkillsApiError(400, 'Skill not found');
    }
    const { content, createdByName, ...summary } = this.change(id, body);
    return summary as SkillSummary;
  }
}
