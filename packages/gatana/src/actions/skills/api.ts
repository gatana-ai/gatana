import type { Gatana } from 'gatana-sdk';
import type { CreateSkillBody, GetSkillResponse, SkillCollectionDto, SkillDto, UpdateSkillBody } from 'gatana-sdk/api';

export type SkillSummary = SkillDto;
export type SkillWithContent = GetSkillResponse;
export type SkillCollectionSummary = SkillCollectionDto;

/**
 * The skill operations sync and push use. An interface rather than the generated client
 * so the tests run against an in-memory implementation; the real one is a thin wrapper over
 * `gatana.api`.
 */
export interface SkillsApi {
  /** Every skill the caller can read, without bodies; narrowed by a text and/or to one collection by name. */
  list(query?: string, collection?: string): Promise<SkillSummary[]>;
  /** Every collection the caller can see. */
  listCollections(): Promise<SkillCollectionSummary[]>;
  /** One skill with its Markdown body. Throws SkillNotFoundError when it is gone or not readable. */
  get(id: string): Promise<SkillWithContent>;
  create(body: CreateSkillBody): Promise<SkillSummary>;
  update(id: string, body: UpdateSkillBody): Promise<SkillSummary>;
}

export class SkillNotFoundError extends Error {
  constructor(public readonly skillId: string) {
    super(`Skill ${skillId} not found`);
    this.name = 'SkillNotFoundError';
  }
}

export class SkillsApiError extends Error {
  constructor(
    public readonly status: number,
    message: string
  ) {
    super(message);
    this.name = 'SkillsApiError';
  }
}

/** The backend answers errors as `{ message }`; older shapes used `error` or `detail`. */
function messageOf(error: unknown, response: Response): string {
  const body = (error ?? {}) as Record<string, unknown>;
  const text = [body.message, body.detail, body.error].find(v => typeof v === 'string' && v.length > 0);
  return typeof text === 'string' ? text : `${response.status} ${response.statusText}`;
}

export function createSkillsApi(gatana: Gatana): SkillsApi {
  const fail = (error: unknown, response: Response): never => {
    // A server without the skills routes answers 404 for the collection itself.
    const pathname = new URL(response.url).pathname;
    if (response.status === 404 && (pathname.endsWith('/skills') || pathname.endsWith('/skill-collections'))) {
      throw new SkillsApiError(404, `Skills are not available on ${gatana.config.baseUrl}: update the server`);
    }
    throw new SkillsApiError(response.status, messageOf(error, response));
  };

  return {
    async list(query, collection) {
      const trimmed = query?.trim();
      const params: { query?: string; collection?: string } = {};
      if (trimmed) {
        params.query = trimmed;
      }
      if (collection) {
        params.collection = collection;
      }
      const { data, error, response } = await gatana.api.listSkills({
        query: Object.keys(params).length > 0 ? params : undefined,
        throwOnError: false,
      });
      if (!response.ok || !data) {
        return fail(error, response);
      }
      return data.skills;
    },

    async listCollections() {
      const { data, error, response } = await gatana.api.listSkillCollections({ throwOnError: false });
      if (!response.ok || !data) {
        return fail(error, response);
      }
      return data.collections;
    },

    async get(id) {
      const { data, error, response } = await gatana.api.getSkill({ path: { skillId: id }, throwOnError: false });
      if (!response.ok || !data) {
        // The service reports a missing or unreadable skill as 400 "Skill not found".
        if (response.status === 404 || (response.status === 400 && messageOf(error, response) === 'Skill not found')) {
          throw new SkillNotFoundError(id);
        }
        return fail(error, response);
      }
      return data;
    },

    async create(body) {
      const { data, error, response } = await gatana.api.createSkill({ body, throwOnError: false });
      if (!response.ok || !data) {
        return fail(error, response);
      }
      return data;
    },

    async update(id, body) {
      const { data, error, response } = await gatana.api.updateSkill({
        path: { skillId: id },
        body,
        throwOnError: false,
      });
      if (!response.ok || !data) {
        return fail(error, response);
      }
      return data;
    },
  };
}
