// Runs a hosted server's index.js for `gatana hosted verify` and `gatana hosted run`. The gatana
// binary writes this file to a temporary folder and starts it with the local `node`.
//
//   node runner.mjs verify <sourceDir> <resultFile>
//   node runner.mjs run <sourceDir> <resultFile> <toolName> <inputFile>
//
// The result goes to <resultFile> as JSON, so whatever the tool prints reaches the terminal
// untouched: { ok: true, result } or { ok: false, stage, error, issues?, expected? }.
import { createRequire } from 'node:module';
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

const [mode, sourceDir, resultFile, toolName, inputFile] = process.argv.slice(2);
const entrypoint = join(sourceDir, 'index.js');

function finish(result) {
  writeFileSync(resultFile, JSON.stringify(result, (_key, value) => (value === undefined ? null : value)));
  // A tool may leave timers or sockets open; the run is over either way.
  process.exit(0);
}

function messageOf(error) {
  if (typeof error === 'string') return error;
  if (error && typeof error === 'object' && typeof error.message === 'string') return error.message;
  try {
    return JSON.stringify(error);
  } catch {
    return String(error);
  }
}

/** The zod the source code itself resolves, so its schemas convert with the same instance. */
async function loadZod() {
  try {
    const require = createRequire(entrypoint);
    const zod = await import(pathToFileURL(require.resolve('zod')).href);
    return zod.z ?? zod.default ?? zod;
  } catch {
    return undefined;
  }
}

/** A Zod schema as plain JSON: its JSON Schema, or failing that the type of each field. */
function describeInput(z, input) {
  if (input == null) return null;
  try {
    if (typeof z?.toJSONSchema === 'function') return z.toJSONSchema(input);
  } catch {
    // Not a schema this zod can convert.
  }
  if (typeof input === 'object' && input.shape && typeof input.shape === 'object') {
    const shape = {};
    for (const [key, value] of Object.entries(input.shape)) {
      shape[key] = value?._zpiType || value?._def?.typeName || typeof value;
    }
    return shape;
  }
  return String(input);
}

let impl;
try {
  impl = await import(pathToFileURL(entrypoint).href);
} catch (error) {
  finish({ ok: false, stage: 'import', error: messageOf(error) });
}
if (!impl.schema || typeof impl.schema !== 'object') {
  finish({ ok: false, stage: 'import', error: 'Module does not export a valid "schema" object.' });
}
const z = await loadZod();

if (mode === 'verify') {
  const entries = Object.entries(impl.schema);
  const exported = Object.keys(impl).filter(key => typeof impl[key] === 'function' && key !== 'default');
  const names = new Set(entries.map(([name]) => name));
  const tools = [];
  for (const [name, descriptor] of entries) {
    const issues = [];
    if (!descriptor?.description) issues.push('missing description');
    const hasExport = typeof impl[name] === 'function';
    if (!hasExport) issues.push(`no exported function "${name}" found`);
    tools.push({
      name,
      valid: issues.length === 0,
      hasExport,
      schema: { description: descriptor?.description || null, input: describeInput(z, descriptor?.input) },
      issues,
    });
  }
  for (const name of exported.filter(name => !names.has(name))) {
    tools.push({
      name,
      valid: false,
      hasExport: true,
      schema: null,
      issues: [`exported function "${name}" has no matching schema entry`],
    });
  }
  finish({
    ok: true,
    result: {
      toolCount: entries.length,
      exportedFunctions: exported.length,
      tools,
      valid: tools.every(tool => tool.valid),
    },
  });
}

if (mode === 'run') {
  if (!impl.schema[toolName]) {
    finish({
      ok: false,
      stage: 'lookup',
      error: `Tool "${toolName}" not found in schema. Available tools: ${Object.keys(impl.schema).join(', ')}`,
    });
  }
  if (typeof impl[toolName] !== 'function') {
    finish({ ok: false, stage: 'lookup', error: `Tool "${toolName}" is defined in schema but has no exported function.` });
  }
  let input = JSON.parse(readFileSync(inputFile, 'utf8'));
  const schema = impl.schema[toolName].input;
  if (schema && typeof schema.safeParse === 'function') {
    const parsed = schema.safeParse(input);
    if (!parsed.success) {
      const issues = (parsed.error?.issues ?? parsed.error?.errors ?? []).map(issue => ({
        path: issue.path?.join('.') || '(root)',
        message: issue.message,
      }));
      finish({ ok: false, stage: 'validation', error: `Input validation failed for tool "${toolName}":`, issues, expected: describeInput(z, schema) });
    }
    // The parsed value: coerced and defaulted.
    input = parsed.data;
  }
  try {
    // A local run has no Gatana session, so no auth headers.
    finish({ ok: true, result: await impl[toolName](input, { headers: {} }) });
  } catch (error) {
    finish({ ok: false, stage: 'execution', error: `Tool execution failed: ${messageOf(error)}` });
  }
}

finish({ ok: false, stage: 'usage', error: `unknown mode ${mode}` });
