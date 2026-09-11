import { Gatana } from 'gatana-sdk';
import { listSandboxes, getSandbox, createSandbox, deleteSandbox } from 'gatana-sdk/api';
import { output, outputError, outputSuccess, TableColumn } from '../../output.js';
import { formatAge } from '../../utils/utils.js';

const sandboxTableColumns: TableColumn[] = [
  { name: 'id', title: 'ID', alignment: 'left' },
  { title: 'User', valueGet: row => row.user?.email ?? '<unknown>', alignment: 'left' },
  { name: 'isArchived', title: 'Archived', alignment: 'center' },
  { title: 'Last Activity', valueGet: row => formatAge(row.lastActivityAt) },
  { title: 'Age', valueGet: row => formatAge(row.createdAt) },
];

/**
 * List all sandboxes, or get a single sandbox by ID.
 * `gatana get sandbox [id]`
 */
export async function getSandboxResource(gatana: Gatana, id?: string, all?: boolean): Promise<void> {
  try {
    if (id) {
      const { data } = await getSandbox({ path: { sandboxId: id } });
      output(data, { defaultFormat: 'yaml' });
    } else {
      const { data } = await listSandboxes({ query: { all: all ? 'true' : 'false' } });
      output({ sandboxes: data.sandboxes || [] }, { tableColumns: sandboxTableColumns, defaultFormat: 'table' });
    }
  } catch (error) {
    outputError(error);
  }
}

/**
 * Create a new sandbox.
 * `gatana create sandbox`
 */
export async function createSandboxResource(gatana: Gatana): Promise<void> {
  try {
    const { data } = await createSandbox();
    if (!data) {
      outputError('Failed to create sandbox.');
      return;
    }
    output(data.sandbox, { defaultFormat: 'yaml' });
  } catch (error) {
    outputError(error);
  }
}

/**
 * Delete a sandbox by ID.
 * `gatana delete sandbox <id>`
 */
export async function deleteSandboxResource(gatana: Gatana, sandboxId: string): Promise<void> {
  try {
    await deleteSandbox({ path: { sandboxId } });
    outputSuccess(`Sandbox '${sandboxId}' deleted successfully.`);
  } catch (error) {
    outputError(error);
  }
}
