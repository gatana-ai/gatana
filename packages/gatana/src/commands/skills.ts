import { confirm } from '@inquirer/prompts';
import { Command, InvalidArgumentError } from 'commander';
import { Gatana } from 'gatana-sdk';
import { getOutputOptions, output, outputError, TableColumn } from '../output.js';
import { resolveSkillsContext } from '../actions/skills/context.js';
import {
  findHookAgents,
  HOOK_AGENTS,
  installHook,
  installHooks,
  removeHook,
  removeHooks,
  renderHookSnippet,
  type HookAgent,
  type HookInstall,
  type HookRemoval,
} from '../actions/skills/hooks.js';
import { pushSkills, type PushAction, type PushResult } from '../actions/skills/push.js';
import { getSkillCollectionResource, getSkillResource } from '../actions/skills/resource.js';
import { describeSubscription, resolveSubscription } from '../actions/skills/subscriptions.js';
import { syncTargets, watchSync, type SyncSummary } from '../actions/skills/sync.js';
import { DEFAULT_TARGETS, prepareTargets, presetHelp, PRESETS, resolveTargets } from '../actions/skills/targets.js';
import { isAbsolute } from 'path';

const MIN_WATCH_SECONDS = 5;
const DEFAULT_WATCH_SECONDS = 60;

interface InstallCommandOptions {
  watch?: true | string;
  dryRun?: boolean;
  prune: boolean;
  force?: boolean;
  query?: string;
  quiet?: boolean;
  org?: string;
  reset?: boolean;
  collection?: boolean;
  skill?: boolean;
  hooks?: boolean;
}

/**
 * The first install argument may be a name or the first target. Presets and anything path-like keep
 * their old meaning, so "install hermes" still targets ~/.hermes/skills and "./release" is always a
 * directory; skill and collection names cannot contain a slash.
 */
function isTargetWord(word: string): boolean {
  return word in PRESETS || word.includes('/') || word.startsWith('.') || word.startsWith('~') || isAbsolute(word);
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

function describeSubscriptions(summary: SyncSummary): string {
  if (summary.subscriptions === null) {
    return '';
  }
  if (summary.subscriptions.length === 0) {
    return ' (no subscriptions: nothing is installed here until you install a collection or skill by name, or run "gatana skills install --everything")';
  }
  return ` (following: ${summary.subscriptions.map(describeSubscription).join(', ')})`;
}

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
      console.log(
        `${summary.dir}: ${changes.length === 0 ? 'nothing to do' : 'would apply'}${describeSubscriptions(summary)}`
      );
      if (changes.length > 0) {
        output(changes, { tableColumns: opColumns });
      }
      continue;
    }
    console.log(
      `${summary.dir}: ${summary.written} written, ${summary.removed} removed, ${summary.skipped} skipped, ${summary.total} skills${describeSubscriptions(summary)}`
    );
  }
}

/**
 * Unchanged skills are counted, not listed: a push of a whole agent folder is mostly skills nobody
 * touched, and the rows that matter are the updates and the conflicts. Machine-readable formats
 * still carry every result.
 */
function reportPush(results: PushResult[]): void {
  const { format, formatExplicit } = getOutputOptions();
  if (formatExplicit && (format === 'json' || format === 'yaml')) {
    output(results);
    return;
  }
  const shown = results.filter(result => result.action !== 'unchanged');
  if (shown.length > 0) {
    output(shown, { tableColumns: pushColumns, defaultFormat: 'table' });
  }
  const count = (action: PushAction) => results.filter(result => result.action === action).length;
  console.log(
    `${count('created')} created, ${count('updated')} updated, ${count('conflict')} conflicts, ${count('error')} errors, ${count('unchanged')} unchanged`
  );
}

function parseWatch(value: string): string {
  const seconds = Number(value);
  if (!Number.isInteger(seconds) || seconds < MIN_WATCH_SECONDS) {
    throw new InvalidArgumentError(`Give a whole number of seconds, at least ${MIN_WATCH_SECONDS}`);
  }
  return value;
}

/** One line per agent found on the machine; agents that are not installed are not mentioned. */
function reportHooks(results: HookInstall[]): void {
  for (const result of results) {
    switch (result.status) {
      case 'installed':
        console.log(`hook installed for ${result.agent}: ${result.file}${result.note ? ` (${result.note})` : ''}`);
        break;
      case 'present':
        console.log(`hook already installed for ${result.agent}: ${result.file}`);
        break;
      case 'manual':
        console.error(`warning: hook for ${result.agent} not installed: ${result.file} ${result.note ?? ''}`.trimEnd());
        break;
      case 'skipped':
        break;
    }
  }
}

/**
 * The hook is a change to the agent's own configuration, so it is asked for, not taken: a terminal
 * gets the question with yes as the default. Without a terminal, or with --quiet, there is nobody to
 * ask and nothing is written, so the hook's own quiet install cannot bring back a hook that
 * "gatana skills remove-hooks" removed. --hooks and --no-hooks answer the question ahead of time.
 */
async function offerHooks(options: { hooks?: boolean; quiet?: boolean }): Promise<void> {
  if (options.hooks === undefined && (!process.stdin.isTTY || options.quiet)) {
    return;
  }
  if (options.hooks === false) {
    return;
  }
  const agents = await findHookAgents();
  if (agents.length === 0) {
    return;
  }
  if (options.hooks === undefined) {
    let install: boolean;
    try {
      install = await confirm({
        message: `Install a session-start hook for ${agents.join(', ')} to keep skills up-to-date?`,
        default: true,
      });
    } catch {
      // Ctrl-C on the question: the skills are installed, the hook is simply not.
      install = false;
    }
    if (!install) {
      console.log('No hook installed. Pass --no-hooks to skip this question.');
      return;
    }
  }
  const results = await installHooks();
  reportHooks(options.quiet ? results.filter(result => result.status === 'manual') : results);
}

/** One line per agent; agents that are not on this machine are not mentioned. */
function reportHookRemovals(results: HookRemoval[]): void {
  for (const result of results) {
    switch (result.status) {
      case 'removed':
        console.log(`hook removed for ${result.agent}: ${result.file}${result.note ? ` (${result.note})` : ''}`);
        break;
      case 'absent':
        console.log(`no hook installed for ${result.agent}: ${result.file}`);
        break;
      case 'manual':
        console.error(`warning: hook for ${result.agent} not removed: ${result.file} ${result.note ?? ''}`.trimEnd());
        break;
      case 'skipped':
        break;
    }
  }
}

export function createSkillsCommand(gatana: Gatana): Command {
  const cmd = new Command('skills').description(
    'Install the skills of your organization into the folders AI agents read, follow collections, and push local changes back'
  );

  cmd.addCommand(
    new Command('install')
      .description(`Download and install one or more skills.`)
      .argument('[name]', 'Optional: The collection or skill name. Omit to install all.')
      .argument('[target...]', 'Optional: Directories or preset names. Omit to install into the default agent folders.')
      .option('--dry-run', 'Show what would change without writing')
      .option('--no-prune', 'Keep skills locally that are removed from Gatana')
      .option(
        '--force',
        'Skip safe-guards: overwrite non-Gatana skills, and install into a directory that is not empty or is synced from another organization'
      )
      .option('--reset', 'Forget any previous state. Download and re-install every skill you can read again')
      .option(
        '--collection',
        'Only if name is provided: If name collision between skill and collection, use the collection'
      )
      .option('--skill', 'Only if name is provided: If name collision between skill and collection, use the skill')
      .option('--no-hooks', 'Do not add the session-start hooks')
      .option('--quiet', 'Print nothing on success; warnings and errors still go to stderr')
      .option('--org <id>', 'Organization from the config file, instead of the default')
      .action(async (name: string | undefined, targets: string[], options: InstallCommandOptions) => {
        try {
          if (options.collection && options.skill) {
            throw new InvalidArgumentError('--collection and --skill exclude each other');
          }
          const named = Boolean(options.collection || options.skill);
          if (name !== undefined && !named && isTargetWord(name)) {
            targets = [name, ...targets];
            name = undefined;
          }
          if (named && name === undefined) {
            throw new InvalidArgumentError('--collection and --skill need a name');
          }
          if (name !== undefined && options.reset) {
            throw new InvalidArgumentError('--reset and a name exclude each other');
          }
          const { api, orgId, baseUrl } = resolveSkillsContext(gatana, options.org);
          const subscription =
            name === undefined
              ? undefined
              : await resolveSubscription(
                  api,
                  name,
                  options.collection ? 'collection' : options.skill ? 'skill' : undefined
                );
          const dirs = await prepareTargets(resolveTargets(targets));
          const syncOptions = {
            dryRun: Boolean(options.dryRun),
            prune: options.prune && !options.query,
            force: Boolean(options.force),
            query: options.query,
            subscribe: subscription,
            reset: Boolean(options.reset),
          };
          const reportOptions = { dryRun: syncOptions.dryRun, quiet: Boolean(options.quiet) };

          if (options.watch !== undefined) {
            const seconds = options.watch === true ? DEFAULT_WATCH_SECONDS : Number(options.watch);
            const controller = new AbortController();
            process.on('SIGINT', () => controller.abort());
            process.on('SIGTERM', () => controller.abort());
            if (!options.quiet) {
              console.log(`Installing every ${seconds}s into ${dirs.join(', ')}. Press Ctrl-C to stop.`);
            }
            // A watch keeps the folders fresh itself, so it never offers the hooks.
            await watchSync(
              api,
              { orgId, baseUrl },
              dirs,
              syncOptions,
              seconds,
              controller.signal,
              summaries => reportSummaries(summaries, reportOptions),
              error => console.error(`install failed: ${(error as Error).message ?? error}`)
            );
            return;
          }

          reportSummaries(await syncTargets(api, { orgId, baseUrl }, dirs, syncOptions), reportOptions);
          if (!syncOptions.dryRun) {
            await offerHooks(options);
          }
        } catch (error) {
          outputError(error);
          process.exitCode = 1;
        }
      })
  );

  cmd.addCommand(
    new Command('remove-hooks')
      .description('Uninstall any hooks that keep your local skills up-to-date.')
      .argument(
        '[agent]',
        `One of: ${HOOK_AGENTS.join(', ')}. Omit to remove the hook from every agent`,
        (value: string) => {
          if (!HOOK_AGENTS.includes(value as HookAgent)) {
            throw new InvalidArgumentError(`One of: ${HOOK_AGENTS.join(', ')}`);
          }
          return value as HookAgent;
        }
      )
      .action(async (agent: HookAgent | undefined) => {
        if (agent !== undefined) {
          const result = await removeHook(agent);
          if (result.status === 'skipped') {
            console.error(`${agent} is not installed on this machine: ${result.file} does not exist`);
            process.exitCode = 1;
            return;
          }
          reportHookRemovals([result]);
          if (result.status === 'manual') {
            process.exitCode = 1;
          }
          return;
        }
        const results = await removeHooks();
        reportHookRemovals(results);
        if (results.some(result => result.status === 'manual')) {
          process.exitCode = 1;
        }
      })
  );

  cmd.addCommand(
    new Command('push')
      .description(`Send local changes back to Gatana.`)
      .argument(
        '[path...]',
        `SKILL.md, skill folder, or directory of skill folders. Default: ${DEFAULT_TARGETS.join(' and ')}`
      )
      .option('-c, --collection <name>', 'Put the pushed skills in this collection')
      .option('--force', 'Overwrite the server copy even when it changed after yours')
      .option('--dry-run', 'Show what would be created or updated without writing')
      .option('--org <id>', 'Organization from the config file, instead of the default')
      .action(
        async (paths: string[], options: { collection?: string; force?: boolean; dryRun?: boolean; org?: string }) => {
          try {
            const { api, orgId, baseUrl } = resolveSkillsContext(gatana, options.org);
            // Typed paths must hold a skill; the default agent folders may not exist yet.
            const explicit = paths.length > 0;
            const results: PushResult[] = await pushSkills(
              api,
              { orgId, baseUrl },
              explicit ? paths : resolveTargets([]),
              {
                force: Boolean(options.force),
                dryRun: Boolean(options.dryRun),
                collection: options.collection,
                skipEmpty: !explicit,
              }
            );
            reportPush(results);
            if (results.some(result => result.action === 'conflict' || result.action === 'error')) {
              process.exitCode = 1;
            }
          } catch (error) {
            outputError(error);
            process.exitCode = 1;
          }
        }
      )
  );

  cmd.addCommand(
    new Command('ls')
      .description('List the skills you can read')
      .option('-q, --query <text>', 'Only skills whose name or description contains the text')
      .option('-c, --collection <name>', 'Only the skills in this collection')
      .option('--collections', 'List the collections instead of the skills')
      .option('--org <id>', 'Organization from the config file, instead of the default')
      .action(async (options: { query?: string; collection?: string; collections?: boolean; org?: string }) => {
        try {
          const { api } = resolveSkillsContext(gatana, options.org);
          if (options.collections) {
            await getSkillCollectionResource(api);
            return;
          }
          await getSkillResource(api, undefined, options.query, options.collection);
        } catch (error) {
          outputError(error);
          process.exitCode = 1;
        }
      })
  );

  cmd.addCommand(
    new Command('hook')
      .description('Show the hook configuration snippet')
      .argument('<agent>', `One of: ${HOOK_AGENTS.join(', ')}`, (value: string) => {
        if (!HOOK_AGENTS.includes(value as HookAgent)) {
          throw new InvalidArgumentError(`One of: ${HOOK_AGENTS.join(', ')}`);
        }
        return value as HookAgent;
      })
      .option('--install', "Write the hook into the agent's configuration instead of printing it")
      .action(async (agent: HookAgent, options: { install?: boolean }) => {
        if (options.install) {
          const result = await installHook(agent);
          if (result.status === 'skipped') {
            console.error(`${agent} is not installed on this machine: ${result.file} does not exist`);
            process.exitCode = 1;
            return;
          }
          reportHooks([result]);
          if (result.status === 'manual') {
            process.exitCode = 1;
          }
          return;
        }
        const { snippet, note } = renderHookSnippet(agent);
        console.log(snippet);
        console.error(`\n${note}`);
      })
  );

  return cmd;
}
