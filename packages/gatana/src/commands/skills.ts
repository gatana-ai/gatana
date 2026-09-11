import { Command, InvalidArgumentError } from 'commander';
import { Gatana } from 'gatana-sdk';
import { getOutputOptions, output, outputError, TableColumn } from '../output.js';
import { resolveSkillsContext } from '../actions/skills/context.js';
import { HOOK_AGENTS, renderHookSnippet, type HookAgent } from '../actions/skills/hooks.js';
import { pushSkills, type PushResult } from '../actions/skills/push.js';
import { getSkillResource } from '../actions/skills/resource.js';
import { syncTargets, watchSync, type SyncSummary } from '../actions/skills/sync.js';
import { DEFAULT_TARGETS, prepareTargets, presetHelp, resolveTargets } from '../actions/skills/targets.js';

const MIN_WATCH_SECONDS = 5;
const DEFAULT_WATCH_SECONDS = 60;

interface SyncCommandOptions {
  watch?: true | string;
  dryRun?: boolean;
  prune: boolean;
  force?: boolean;
  query?: string;
  quiet?: boolean;
  org?: string;
}

const opColumns: TableColumn[] = [
  { title: 'Action', valueGet: row => row.kind },
  { title: 'Skill', name: 'name' },
  { title: 'Reason', name: 'reason' },
];

const pushColumns: TableColumn[] = [
  { title: 'Skill', name: 'name' },
  { title: 'Action', name: 'action' },
  { title: 'Detail', valueGet: row => row.detail || '' },
];

function reportSummaries(summaries: SyncSummary[], options: { dryRun: boolean; quiet: boolean }): void {
  for (const summary of summaries) {
    for (const warning of summary.warnings) {
      console.error(`warning: ${warning}`);
    }
  }
  if (options.quiet) {
    return;
  }
  const { format, formatExplicit } = getOutputOptions();
  if (formatExplicit && (format === 'json' || format === 'yaml')) {
    output(summaries.map(({ ops, ...rest }) => ({ ...rest, ops: options.dryRun ? ops : undefined })));
    return;
  }
  for (const summary of summaries) {
    if (options.dryRun) {
      const changes = summary.ops.filter(op => op.kind !== 'skip' || op.reason !== 'unchanged');
      console.log(`${summary.dir}: ${changes.length === 0 ? 'nothing to do' : 'would apply'}`);
      if (changes.length > 0) {
        output(changes, { tableColumns: opColumns });
      }
      continue;
    }
    console.log(
      `${summary.dir}: ${summary.written} written, ${summary.removed} removed, ${summary.skipped} skipped, ${summary.total} skills`
    );
  }
}

function parseWatch(value: string): string {
  const seconds = Number(value);
  if (!Number.isInteger(seconds) || seconds < MIN_WATCH_SECONDS) {
    throw new InvalidArgumentError(`Give a whole number of seconds, at least ${MIN_WATCH_SECONDS}`);
  }
  return value;
}

export function createSkillsCommand(gatana: Gatana): Command {
  const cmd = new Command('skills').description(
    'Sync the skills of your organization into the folders AI agents read, and push local changes back'
  );

  cmd.addCommand(
    new Command('sync')
      .description(
        `Write every skill you can read as <dir>/<name>/SKILL.md. Targets are paths or presets: ${presetHelp()}. Default: ${DEFAULT_TARGETS.join(' and ')}. Folders the sync did not create are never touched; a locally edited SKILL.md is not overwritten until it is pushed.`
      )
      .argument('[target...]', 'Directories or preset names')
      .option(
        '-w, --watch [seconds]',
        `Keep running and re-sync at this interval (default ${DEFAULT_WATCH_SECONDS}, minimum ${MIN_WATCH_SECONDS})`,
        parseWatch
      )
      .option('--dry-run', 'Show what would change without writing')
      .option('--no-prune', 'Keep folders of skills that are no longer listed for you')
      .option(
        '--force',
        'Take over foreign folders, overwrite local edits, and allow switching a directory to another organization'
      )
      .option('-q, --query <text>', 'Only skills whose name or description contains the text (implies --no-prune)')
      .option('--quiet', 'Print nothing on success; warnings and errors still go to stderr')
      .option('--org <id>', 'Organization from the config file, instead of the default')
      .action(async (targets: string[], options: SyncCommandOptions) => {
        try {
          const { api, orgId, baseUrl } = resolveSkillsContext(gatana, options.org);
          const dirs = await prepareTargets(resolveTargets(targets));
          const syncOptions = {
            dryRun: Boolean(options.dryRun),
            prune: options.prune && !options.query,
            force: Boolean(options.force),
            query: options.query,
          };
          const reportOptions = { dryRun: syncOptions.dryRun, quiet: Boolean(options.quiet) };

          if (options.watch !== undefined) {
            const seconds = options.watch === true ? DEFAULT_WATCH_SECONDS : Number(options.watch);
            const controller = new AbortController();
            process.on('SIGINT', () => controller.abort());
            process.on('SIGTERM', () => controller.abort());
            if (!options.quiet) {
              console.log(`Syncing every ${seconds}s into ${dirs.join(', ')}. Press Ctrl-C to stop.`);
            }
            await watchSync(
              api,
              { orgId, baseUrl },
              dirs,
              syncOptions,
              seconds,
              controller.signal,
              summaries => reportSummaries(summaries, reportOptions),
              error => console.error(`sync failed: ${(error as Error).message ?? error}`)
            );
            return;
          }

          reportSummaries(await syncTargets(api, { orgId, baseUrl }, dirs, syncOptions), reportOptions);
        } catch (error) {
          outputError(error);
          process.exitCode = 1;
        }
      })
  );

  cmd.addCommand(
    new Command('push')
      .description(
        'Create or update skills from a SKILL.md, a skill folder, or a directory of skill folders. A file that came from a sync updates its skill; a new file creates one, or updates the skill of the same name. Refuses when the server copy changed after yours.'
      )
      .argument('<path>', 'SKILL.md, skill folder, or directory of skill folders')
      .option('--force', 'Overwrite the server copy even when it changed after yours')
      .option('--dry-run', 'Show what would be created or updated without writing')
      .option('--org <id>', 'Organization from the config file, instead of the default')
      .action(async (path: string, options: { force?: boolean; dryRun?: boolean; org?: string }) => {
        try {
          const { api, orgId, baseUrl } = resolveSkillsContext(gatana, options.org);
          const results: PushResult[] = await pushSkills(api, { orgId, baseUrl }, path, {
            force: Boolean(options.force),
            dryRun: Boolean(options.dryRun),
          });
          output(results, { tableColumns: pushColumns, defaultFormat: 'table' });
          if (results.some(result => result.action === 'conflict' || result.action === 'error')) {
            process.exitCode = 1;
          }
        } catch (error) {
          outputError(error);
          process.exitCode = 1;
        }
      })
  );

  cmd.addCommand(
    new Command('ls')
      .description('List the skills you can read')
      .option('-q, --query <text>', 'Only skills whose name or description contains the text')
      .option('--org <id>', 'Organization from the config file, instead of the default')
      .action(async (options: { query?: string; org?: string }) => {
        try {
          const { api } = resolveSkillsContext(gatana, options.org);
          await getSkillResource(api, undefined, options.query);
        } catch (error) {
          outputError(error);
          process.exitCode = 1;
        }
      })
  );

  cmd.addCommand(
    new Command('hook')
      .description('Print the configuration that runs a quiet sync when an agent session starts')
      .argument('<agent>', `One of: ${HOOK_AGENTS.join(', ')}`, (value: string) => {
        if (!HOOK_AGENTS.includes(value as HookAgent)) {
          throw new InvalidArgumentError(`One of: ${HOOK_AGENTS.join(', ')}`);
        }
        return value as HookAgent;
      })
      .action((agent: HookAgent) => {
        const { snippet, note } = renderHookSnippet(agent);
        console.log(snippet);
        console.error(`\n${note}`);
      })
  );

  return cmd;
}
