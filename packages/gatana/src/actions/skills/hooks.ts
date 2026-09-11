export type HookAgent = 'claude' | 'hermes';

export const HOOK_AGENTS: HookAgent[] = ['claude', 'hermes'];

/**
 * Configuration that runs a quiet sync when an agent session starts. Claude Code adds the stdout
 * of a SessionStart hook to the model's context, hence --quiet. Hermes runs on_session_start for
 * new sessions only; on_session_reset covers /new.
 */
export function renderHookSnippet(agent: HookAgent): { snippet: string; note: string } {
  switch (agent) {
    case 'claude':
      return {
        snippet: JSON.stringify(
          {
            hooks: {
              SessionStart: [
                {
                  matcher: 'startup|resume',
                  hooks: [{ type: 'command', command: 'gatana skills sync claude --quiet' }],
                },
              ],
            },
          },
          null,
          2
        ),
        note: 'Merge into ~/.claude/settings.json (every project) or .claude/settings.json (one project).',
      };
    case 'hermes':
      return {
        snippet: [
          'hooks:',
          '  on_session_start:',
          '    - command: "gatana skills sync hermes --quiet"',
          '      timeout: 60',
          '  on_session_reset:',
          '    - command: "gatana skills sync hermes --quiet"',
          '      timeout: 60',
        ].join('\n'),
        note: 'Merge into ~/.hermes/config.yaml.',
      };
  }
}
