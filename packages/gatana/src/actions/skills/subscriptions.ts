import type { SkillsApi } from './api.js';
import type { Subscription } from './manifest.js';

export type SubscriptionKind = Subscription['kind'];

/** Describes a subscription for messages: `collection release`, `skill deploy`. */
export function describeSubscription(subscription: Subscription): string {
  return `${subscription.kind} ${subscription.name}`;
}

/**
 * What a name points at: a collection, or a skill. Collections and skills are named in separate
 * namespaces, so one name may exist in both; then the caller has to say which, rather than the CLI
 * guessing. `kind` narrows the search to one namespace.
 */
export async function resolveSubscription(
  api: SkillsApi,
  name: string,
  kind?: SubscriptionKind
): Promise<Subscription> {
  const wanted = name.trim();
  const collection =
    kind === 'skill' ? undefined : (await api.listCollections()).find(candidate => candidate.name === wanted);
  const skill = kind === 'collection' ? undefined : (await api.list()).find(candidate => candidate.name === wanted);
  if (collection && skill) {
    throw new Error(`"${wanted}" is both a collection and a skill. Say which: --collection or --skill`);
  }
  if (collection) {
    return { kind: 'collection', id: collection.id, name: collection.name };
  }
  if (skill) {
    return { kind: 'skill', id: skill.id, name: skill.name };
  }
  const collections = kind === 'skill' ? [] : (await api.listCollections()).map(candidate => candidate.name).sort();
  const what = kind ?? 'collection or skill';
  return Promise.reject(
    new Error(
      collections.length > 0
        ? `No ${what} named "${wanted}". Collections you can see: ${collections.join(', ')}. Skills: "gatana skills ls"`
        : `No ${what} named "${wanted}". See "gatana skills ls" and "gatana skills ls --collections"`
    )
  );
}
