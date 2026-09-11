import { test } from 'node:test';
import assert from 'node:assert/strict';
import { computeSyncPlan, type LocalState } from '../../src/actions/skills/plan.js';
import type { SkillSummary } from '../../src/actions/skills/api.js';

const T1 = '2026-09-10T08:00:00.000Z';
const T2 = '2026-09-10T09:00:00.000Z';

function remote(id: string, name: string, updatedAt = T1): SkillSummary {
  return { id, name, updatedAt } as unknown as SkillSummary;
}
function local(entries: Record<string, string | null>): LocalState {
  const dirs = new Set(Object.keys(entries));
  const hashes = new Map(Object.entries(entries).filter(([, h]) => h !== null) as [string, string][]);
  return { dirs, hashes };
}
const entry = (name: string, hash = 'h', updatedAt = T1) => ({ name, updatedAt, hash });
const brief = (ops: ReturnType<typeof computeSyncPlan>) => ops.map(op => `${op.kind}:${op.name}:${op.reason}`);

test('new skill is written; a foreign folder of the same name is skipped unless forced', () => {
  const input = { remote: [remote('1', 'a')], manifest: {}, local: local({}), prune: true, force: false };
  assert.deepEqual(brief(computeSyncPlan(input)), ['write:a:new']);
  const occupied = { ...input, local: local({ a: 'x' }) };
  assert.deepEqual(brief(computeSyncPlan(occupied)), ['skip:a:foreign-folder']);
  assert.deepEqual(brief(computeSyncPlan({ ...occupied, force: true })), ['write:a:new']);
});

test('unchanged, changed, and missing-locally', () => {
  const manifest = { '1': entry('a') };
  assert.deepEqual(
    brief(
      computeSyncPlan({ remote: [remote('1', 'a')], manifest, local: local({ a: 'h' }), prune: true, force: false })
    ),
    ['skip:a:unchanged']
  );
  assert.deepEqual(
    brief(
      computeSyncPlan({ remote: [remote('1', 'a', T2)], manifest, local: local({ a: 'h' }), prune: true, force: false })
    ),
    ['write:a:changed']
  );
  assert.deepEqual(
    brief(computeSyncPlan({ remote: [remote('1', 'a')], manifest, local: local({}), prune: true, force: false })),
    ['write:a:missing-locally']
  );
  // Folder present but SKILL.md gone counts as missing.
  assert.deepEqual(
    brief(
      computeSyncPlan({ remote: [remote('1', 'a')], manifest, local: local({ a: null }), prune: true, force: false })
    ),
    ['write:a:missing-locally']
  );
});

test('local edits are never overwritten without --force', () => {
  const manifest = { '1': entry('a') };
  const edited = local({ a: 'different' });
  assert.deepEqual(
    brief(computeSyncPlan({ remote: [remote('1', 'a', T2)], manifest, local: edited, prune: true, force: false })),
    ['skip:a:local-edits']
  );
  assert.deepEqual(
    brief(computeSyncPlan({ remote: [remote('1', 'a')], manifest, local: edited, prune: true, force: true })),
    ['write:a:changed']
  );
});

test('rename removes the old folder then writes the new one; swapped names work because removes run first', () => {
  const manifest = { '1': entry('a') };
  assert.deepEqual(
    brief(
      computeSyncPlan({ remote: [remote('1', 'b', T2)], manifest, local: local({ a: 'h' }), prune: true, force: false })
    ),
    ['remove:a:renamed', 'write:b:renamed']
  );
  const swap = { '1': entry('a'), '2': entry('b') };
  assert.deepEqual(
    brief(
      computeSyncPlan({
        remote: [remote('1', 'b', T2), remote('2', 'a', T2)],
        manifest: swap,
        local: local({ a: 'h', b: 'h' }),
        prune: true,
        force: false,
      })
    ),
    ['remove:a:renamed', 'write:b:renamed', 'remove:b:renamed', 'write:a:renamed']
  );
});

test('rename onto a foreign folder is skipped', () => {
  const manifest = { '1': entry('a') };
  assert.deepEqual(
    brief(
      computeSyncPlan({
        remote: [remote('1', 'b')],
        manifest,
        local: local({ a: 'h', b: 'x' }),
        prune: true,
        force: false,
      })
    ),
    ['remove:a:renamed', 'skip:b:foreign-folder']
  );
});

test('a skill no longer listed is pruned, or kept with prune off', () => {
  const manifest = { '1': entry('a') };
  assert.deepEqual(
    brief(computeSyncPlan({ remote: [], manifest, local: local({ a: 'h' }), prune: true, force: false })),
    ['remove:a:pruned']
  );
  assert.deepEqual(
    brief(computeSyncPlan({ remote: [], manifest, local: local({ a: 'h' }), prune: false, force: false })),
    ['skip:a:kept']
  );
});
