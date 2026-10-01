import { output, outputError, TableColumn } from '../../output.js';
import { formatAge } from '../../utils/utils.js';
import type { SkillsApi } from './api.js';

function formatBytes(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes}B`;
  }
  return `${Math.round(bytes / 1024)}K`;
}

const skillTableColumns: TableColumn[] = [
  { name: 'name', title: 'Name', alignment: 'left' },
  { title: 'Collection', valueGet: row => row.collectionName ?? '', alignment: 'left' },
  { name: 'visibility', title: 'Visibility', alignment: 'left' },
  { title: 'Size', valueGet: row => formatBytes(row.contentBytes), alignment: 'left' },
  { name: 'createdByUserEmail', title: 'Owner', alignment: 'left' },
  { title: 'Updated', valueGet: row => formatAge(row.updatedAt) },
  { title: 'Age', valueGet: row => formatAge(row.createdAt) },
];

const collectionTableColumns: TableColumn[] = [
  { name: 'name', title: 'Name', alignment: 'left' },
  { name: 'description', title: 'Description', alignment: 'left' },
  { name: 'visibility', title: 'Visibility', alignment: 'left' },
  { title: 'Skills', valueGet: row => String(row.skillCount) },
  { name: 'createdByUserEmail', title: 'Owner', alignment: 'left' },
  { title: 'Updated', valueGet: row => formatAge(row.updatedAt) },
];

/**
 * List the skills the caller can read, or show one by name with its instructions.
 * `gatana get skills [name]`, `gatana skills ls`
 */
export async function getSkillResource(
  api: SkillsApi,
  name?: string,
  query?: string,
  collection?: string
): Promise<void> {
  try {
    if (name) {
      const match = (await api.list()).find(skill => skill.name === name);
      if (!match) {
        outputError(`Skill '${name}' not found.`);
        process.exitCode = 1;
        return;
      }
      output(await api.get(match.id), { defaultFormat: 'yaml' });
    } else {
      const skills = await api.list(query, collection);
      output({ skills }, { tableColumns: skillTableColumns, defaultFormat: 'table' });
    }
  } catch (error) {
    outputError(error);
    process.exitCode = 1;
  }
}

/** List the collections the caller can see, with how many of their skills the caller can read. `gatana skills ls --collections` */
export async function getSkillCollectionResource(api: SkillsApi): Promise<void> {
  try {
    const collections = await api.listCollections();
    output({ collections }, { tableColumns: collectionTableColumns, defaultFormat: 'table' });
  } catch (error) {
    outputError(error);
    process.exitCode = 1;
  }
}
