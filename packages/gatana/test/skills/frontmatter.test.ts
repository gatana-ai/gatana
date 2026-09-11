import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  frontmatterFor,
  META_ID,
  META_ORG,
  META_UPDATED_AT,
  parseSkillMd,
  renderSkillMd,
  SkillMdError,
} from '../../src/actions/skills/frontmatter.js';

const skill = {
  id: 'skill_1',
  name: 'release-checklist',
  description: 'Use when deploying',
  updatedAt: '2026-09-10T08:00:00.000Z',
};

test('render then parse round-trips name, description, metadata and body byte for byte', () => {
  const body = '# Release\n\nStep 1: run `just deploy`.\n\n---\n\nNot frontmatter.\n';
  const text = renderSkillMd(frontmatterFor(skill, 'acme'), body);
  const parsed = parseSkillMd(text);
  assert.equal(parsed.frontmatter.name, 'release-checklist');
  assert.equal(parsed.frontmatter.description, 'Use when deploying');
  assert.deepEqual(parsed.frontmatter.metadata, {
    [META_ID]: 'skill_1',
    [META_ORG]: 'acme',
    [META_UPDATED_AT]: '2026-09-10T08:00:00.000Z',
  });
  assert.equal(parsed.body, body);
});

test('render quotes awkward descriptions on one line', () => {
  for (const description of [
    'Use when: x # not a comment',
    'Say "hi" to <b>them</b>',
    'Line one\nline two',
    "It's - a: list",
  ]) {
    const text = renderSkillMd(frontmatterFor({ ...skill, description }, 'acme'), 'body');
    const lines = text.split('\n');
    assert.equal(lines[1], 'name: release-checklist');
    assert.match(lines[2], /^description: ".*"$/);
    assert.equal(parseSkillMd(text).frontmatter.description, description.replace(/\s*\n\s*/g, ' '));
  }
});

test('render adds exactly one trailing newline to the body', () => {
  assert.ok(renderSkillMd(frontmatterFor(skill, 'acme'), 'body').endsWith('\n\nbody\n'));
  assert.ok(renderSkillMd(frontmatterFor(skill, 'acme'), 'body\n').endsWith('\n\nbody\n'));
});

test('parse accepts unknown keys, keeps them as extra, and coerces metadata values to strings', () => {
  const parsed = parseSkillMd(
    [
      '---',
      'name: my-skill',
      'description: Does things',
      'license: MIT',
      'allowed-tools: Bash(git:*) Read',
      'metadata:',
      '  version: 1.0',
      '  stable: true',
      '---',
      'Body',
      '',
    ].join('\n')
  );
  assert.deepEqual(parsed.frontmatter.extra, { license: 'MIT', 'allowed-tools': 'Bash(git:*) Read' });
  assert.deepEqual(parsed.frontmatter.metadata, { version: '1', stable: 'true' });
  assert.equal(parsed.body, 'Body\n');
});

test('parse keeps a body that starts without a blank line', () => {
  const parsed = parseSkillMd('---\nname: a\ndescription: b\n---\nBody line\n');
  assert.equal(parsed.body, 'Body line\n');
});

test('parse rejects missing frontmatter, bad names, empty bodies and non-mapping frontmatter', () => {
  assert.throws(() => parseSkillMd('# no frontmatter\n'), SkillMdError);
  assert.throws(() => parseSkillMd('---\nname: Bad Name\ndescription: x\n---\nbody\n'), /name/);
  assert.throws(() => parseSkillMd('---\nname: ok\ndescription: x\n---\n\n   \n'), /no instructions/);
  assert.throws(() => parseSkillMd('---\n- a\n- b\n---\nbody\n'), /mapping/);
  assert.throws(() => parseSkillMd('---\nname: ok\ndescription: x\nmetadata: [1]\n---\nbody\n'), SkillMdError);
});

test('frontmatterFor keeps foreign metadata keys and replaces the gatana ones', () => {
  const fm = frontmatterFor(skill, 'acme', { license: 'MIT' }, { author: 'me', [META_ID]: 'old', [META_ORG]: 'other' });
  assert.deepEqual(fm.extra, { license: 'MIT' });
  assert.equal(fm.metadata.author, 'me');
  assert.equal(fm.metadata[META_ID], 'skill_1');
  assert.equal(fm.metadata[META_ORG], 'acme');
});
