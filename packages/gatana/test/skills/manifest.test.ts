import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readdir, readFile, writeFile } from 'fs/promises';
import { tmpdir } from 'os';
import { join } from 'path';
import {
  emptyManifest,
  MANIFEST_FILE,
  ManifestError,
  readManifest,
  writeManifest,
} from '../../src/actions/skills/manifest.js';

test('missing manifest reads as undefined; a written one reads back; no temp file remains', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'gatana-manifest-'));
  assert.equal(await readManifest(dir), undefined);
  const manifest = {
    ...emptyManifest('acme', 'https://acme.example'),
    skills: { s1: { name: 'a', updatedAt: 'x', hash: 'y' } },
  };
  await writeManifest(dir, manifest);
  assert.deepEqual(await readManifest(dir), manifest);
  assert.deepEqual(await readdir(dir), [MANIFEST_FILE]);
});

test('corrupt or misshapen manifests are errors, not empty manifests', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'gatana-manifest-'));
  await writeFile(join(dir, MANIFEST_FILE), '{not json');
  await assert.rejects(readManifest(dir), ManifestError);
  await writeFile(join(dir, MANIFEST_FILE), JSON.stringify({ version: 2, skills: {} }));
  await assert.rejects(readManifest(dir), ManifestError);
  assert.equal(typeof (await readFile(join(dir, MANIFEST_FILE), 'utf8')), 'string');
});

test('a version 1 manifest reads as version 2 without subscriptions', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'gatana-manifest-'));
  await writeFile(
    join(dir, MANIFEST_FILE),
    JSON.stringify({ version: 1, orgId: 'acme', baseUrl: 'https://acme.example', syncedAt: 'x', skills: {} })
  );
  const manifest = (await readManifest(dir))!;
  assert.equal(manifest.version, 2);
  assert.equal(manifest.subscriptions, null);
});
