//! Session-start hooks that keep the installed skills current: each agent runs
//! `gatana skills sync --quiet` when a session starts.

use anyhow::Result;
use serde::Serialize;
use serde_json::{Map, Value, json};
use std::path::{Path, PathBuf};

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, clap::ValueEnum)]
#[serde(rename_all = "lowercase")]
pub enum HookAgent {
    Claude,
    Codex,
    Hermes,
    Openclaw,
}

pub const HOOK_AGENTS: [HookAgent; 4] = [HookAgent::Claude, HookAgent::Codex, HookAgent::Hermes, HookAgent::Openclaw];

impl HookAgent {
    pub fn as_str(self) -> &'static str {
        match self {
            HookAgent::Claude => "claude",
            HookAgent::Codex => "codex",
            HookAgent::Hermes => "hermes",
            HookAgent::Openclaw => "openclaw",
        }
    }

    /// The product name, for menus and messages.
    pub fn label(self) -> &'static str {
        match self {
            HookAgent::Claude => "Claude Code",
            HookAgent::Codex => "Codex",
            HookAgent::Hermes => "Hermes",
            HookAgent::Openclaw => "OpenClaw",
        }
    }
}

/// What every hook runs. Claude Code, Codex and OpenClaw read the default targets (~/.claude/skills
/// and ~/.agents/skills), so their hooks sync those; Hermes reads its own folder. Claude Code and
/// Codex add the stdout of a SessionStart hook to the model's context, hence --quiet everywhere.
const SYNC_DEFAULT: &str = "gatana skills sync --quiet";
const SYNC_HERMES: &str = "gatana skills sync hermes --quiet";
const SYNC_MARKER: &str = "gatana skills sync";
const OPENCLAW_HOOK: &str = "gatana-skills";

/// The agent's home directory; its presence is how we tell the agent is installed on this machine.
pub fn agent_home(agent: HookAgent, home: &Path) -> PathBuf {
    home.join(format!(".{}", agent.as_str()))
}

fn claude_entry() -> Value {
    json!({ "matcher": "startup|resume", "hooks": [{ "type": "command", "command": SYNC_DEFAULT }] })
}

fn codex_entry() -> Value {
    json!({
        "matcher": "startup|resume",
        "hooks": [{ "type": "command", "command": SYNC_DEFAULT, "statusMessage": "Syncing Gatana skills", "timeout": 60 }],
    })
}

fn hermes_block() -> String {
    [
        "hooks:".to_string(),
        "  on_session_start:".to_string(),
        format!("    - command: \"{SYNC_HERMES}\""),
        "      timeout: 60".to_string(),
        "  on_session_reset:".to_string(),
        format!("    - command: \"{SYNC_HERMES}\""),
        "      timeout: 60".to_string(),
    ]
    .join("\n")
}

fn openclaw_config() -> Value {
    json!({ "hooks": { "internal": { "enabled": true, "entries": { OPENCLAW_HOOK: { "enabled": true } } } } })
}

fn openclaw_hook_md() -> String {
    format!(
        r#"---
name: {OPENCLAW_HOOK}
description: "Sync the skills of your Gatana organization when the gateway starts and on /new and /reset"
metadata:
  {{ "openclaw": {{ "events": ["gateway:startup", "command:new", "command:reset"] }} }}
---

# Gatana skills

Runs `{SYNC_DEFAULT}` so the skills folders OpenClaw reads follow the organization.
Installed by `gatana skills install`; run `gatana skills remove-hooks openclaw` to stop.
"#
    )
}

const OPENCLAW_HANDLER: &str = r#"import { execFile } from 'node:child_process';

// Written by "gatana skills install". Syncs the Gatana skills folders; failures are logged, never thrown,
// so a missing CLI or a network problem cannot break the gateway.
export default async function handler() {
  await new Promise(resolve => {
    execFile('gatana', ['skills', 'sync', '--quiet'], { timeout: 60_000 }, error => {
      if (error) {
        console.error(`gatana skills sync failed: ${error.message}`);
      }
      resolve(undefined);
    });
  });
}
"#;

fn pretty(value: &Value) -> String {
    serde_json::to_string_pretty(value).unwrap_or_default()
}

/// Configuration that runs a quiet sync when an agent session starts, for pasting by hand.
pub fn render_hook_snippet(agent: HookAgent) -> (String, &'static str) {
    match agent {
        HookAgent::Claude => (
            pretty(&json!({ "hooks": { "SessionStart": [claude_entry()] } })),
            "Merge into ~/.claude/settings.json (every project) or .claude/settings.json (one project).",
        ),
        HookAgent::Codex => (
            pretty(&json!({ "hooks": { "SessionStart": [codex_entry()] } })),
            "Merge into ~/.codex/hooks.json (every project) or .codex/hooks.json (one project).",
        ),
        HookAgent::Hermes => (hermes_block(), "Merge into ~/.hermes/config.yaml."),
        HookAgent::Openclaw => (
            [
                format!("# ~/.openclaw/hooks/{OPENCLAW_HOOK}/HOOK.md"),
                openclaw_hook_md(),
                format!("# ~/.openclaw/hooks/{OPENCLAW_HOOK}/handler.ts"),
                OPENCLAW_HANDLER.to_string(),
                "# merge into ~/.openclaw/openclaw.json".to_string(),
                pretty(&openclaw_config()),
            ]
            .join("\n"),
            "Write the two files, merge the config, then restart the gateway.",
        ),
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum HookStatus {
    /// Written now.
    Installed,
    /// Was already there.
    Present,
    /// Removed now.
    Removed,
    /// There was no hook of ours to remove.
    Absent,
    /// The agent is not on this machine: its home directory does not exist.
    Skipped,
    /// The config file could not be edited safely; the hook must be added or removed by hand.
    Manual,
}

#[derive(Clone, Debug, Serialize)]
pub struct HookResult {
    pub agent: HookAgent,
    pub file: PathBuf,
    pub status: HookStatus,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub note: Option<String>,
}

impl HookResult {
    pub(crate) fn new(agent: HookAgent, file: PathBuf, status: HookStatus) -> Self {
        Self { agent, file, status, note: None }
    }

    pub(crate) fn with_note(mut self, note: impl Into<String>) -> Self {
        self.note = Some(note.into());
        self
    }
}

pub(crate) enum JsonFile {
    Missing,
    Unparseable,
    Object(Map<String, Value>),
}

/// Strict JSON only. A file with comments or trailing commas is not rewritten: a round trip would
/// drop them.
pub(crate) fn read_json_object(path: &Path) -> Result<JsonFile> {
    let text = match std::fs::read_to_string(path) {
        Ok(text) => text,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(JsonFile::Missing),
        Err(error) => return Err(error.into()),
    };
    if text.trim().is_empty() {
        return Ok(JsonFile::Missing);
    }
    Ok(match serde_json::from_str::<Value>(&text) {
        Ok(Value::Object(map)) => JsonFile::Object(map),
        _ => JsonFile::Unparseable,
    })
}

pub(crate) fn write_json(path: &Path, value: &Value) -> Result<()> {
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    std::fs::write(path, format!("{}\n", pretty(value)))?;
    Ok(())
}

fn is_sync_command(hook: &Value) -> bool {
    hook.get("command").and_then(Value::as_str).is_some_and(|command| command.contains(SYNC_MARKER))
}

/// True when any command hook under SessionStart already runs a gatana sync.
fn has_sync_hook(session_start: Option<&Value>) -> bool {
    session_start.and_then(Value::as_array).is_some_and(|entries| {
        entries.iter().any(|entry| {
            entry.get("hooks").and_then(Value::as_array).is_some_and(|hooks| hooks.iter().any(is_sync_command))
        })
    })
}

fn object_at(map: &Map<String, Value>, key: &str) -> Map<String, Value> {
    map.get(key).and_then(Value::as_object).cloned().unwrap_or_default()
}

/// Claude Code and Codex share one shape: {hooks: {SessionStart: [entry]}} in a JSON file.
fn install_json_hook(agent: HookAgent, file: PathBuf, entry: Value) -> Result<HookResult> {
    let mut settings = match read_json_object(&file)? {
        JsonFile::Unparseable => {
            return Ok(HookResult::new(agent, file, HookStatus::Manual).with_note(format!(
                "not plain JSON; merge the output of \"gatana skills hook {}\" by hand",
                agent.as_str()
            )));
        }
        JsonFile::Missing => Map::new(),
        JsonFile::Object(map) => map,
    };
    let mut hooks = object_at(&settings, "hooks");
    if has_sync_hook(hooks.get("SessionStart")) {
        return Ok(HookResult::new(agent, file, HookStatus::Present));
    }
    let mut session_start = hooks.get("SessionStart").and_then(Value::as_array).cloned().unwrap_or_default();
    session_start.push(entry);
    hooks.insert("SessionStart".into(), Value::Array(session_start));
    settings.insert("hooks".into(), Value::Object(hooks));
    write_json(&file, &Value::Object(settings))?;
    Ok(HookResult::new(agent, file, HookStatus::Installed))
}

/// Hermes keeps its configuration in YAML that people edit by hand, and a parse-and-dump would
/// drop their comments. So: no hooks key yet, append ours as text; hooks present and ours among
/// them, done; hooks present without ours, leave the file alone and ask for a manual merge.
fn install_hermes_hook(file: PathBuf) -> Result<HookResult> {
    let agent = HookAgent::Hermes;
    let text = match std::fs::read_to_string(&file) {
        Ok(text) => text,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => String::new(),
        Err(error) => return Err(error.into()),
    };
    if text.contains(SYNC_MARKER) {
        return Ok(HookResult::new(agent, file, HookStatus::Present));
    }
    let config = match crate::yaml::load(&text) {
        Ok(config) => config,
        Err(_) => {
            return Ok(HookResult::new(agent, file, HookStatus::Manual)
                .with_note("not valid YAML; merge the output of \"gatana skills hook hermes\" by hand"));
        }
    };
    if config.get("hooks").is_some() {
        return Ok(HookResult::new(agent, file, HookStatus::Manual)
            .with_note("already has a hooks section; merge the output of \"gatana skills hook hermes\" by hand"));
    }
    let separator = if text.is_empty() || text.ends_with('\n') { "" } else { "\n" };
    let gap = if text.is_empty() { "" } else { "\n" };
    if let Some(parent) = file.parent() {
        std::fs::create_dir_all(parent)?;
    }
    std::fs::write(&file, format!("{text}{separator}{gap}{}\n", hermes_block()))?;
    Ok(HookResult::new(agent, file, HookStatus::Installed))
}

/// OpenClaw hooks are code, not commands: a folder with a HOOK.md and a handler, enabled per name
/// in openclaw.json. The files are always written (they are ours); the config is edited only when
/// it is plain JSON. The gateway loads hooks at start, so a restart is part of the note either way.
fn install_openclaw_hook(home: &Path) -> Result<HookResult> {
    let agent = HookAgent::Openclaw;
    let dir = home.join("hooks").join(OPENCLAW_HOOK);
    let config_file = home.join("openclaw.json");
    let files_were_there = dir.join("HOOK.md").exists();
    std::fs::create_dir_all(&dir)?;
    std::fs::write(dir.join("HOOK.md"), openclaw_hook_md())?;
    std::fs::write(dir.join("handler.ts"), OPENCLAW_HANDLER)?;

    let mut config = match read_json_object(&config_file)? {
        JsonFile::Unparseable => {
            return Ok(HookResult::new(agent, config_file, HookStatus::Manual).with_note(format!(
                "hook written to {}; the config is not plain JSON, enable it by hand and restart the gateway",
                dir.display()
            )));
        }
        JsonFile::Missing => Map::new(),
        JsonFile::Object(map) => map,
    };
    let mut hooks = object_at(&config, "hooks");
    let mut internal = object_at(&hooks, "internal");
    let mut entries = object_at(&internal, "entries");
    let enabled = internal.get("enabled") == Some(&Value::Bool(true))
        && entries.get(OPENCLAW_HOOK).and_then(|entry| entry.get("enabled")) == Some(&Value::Bool(true));
    if enabled && files_were_there {
        return Ok(HookResult::new(agent, config_file, HookStatus::Present));
    }
    entries.insert(OPENCLAW_HOOK.into(), json!({ "enabled": true }));
    internal.insert("enabled".into(), Value::Bool(true));
    internal.insert("entries".into(), Value::Object(entries));
    hooks.insert("internal".into(), Value::Object(internal));
    config.insert("hooks".into(), Value::Object(hooks));
    write_json(&config_file, &Value::Object(config))?;
    Ok(HookResult::new(agent, config_file, HookStatus::Installed).with_note("restart the gateway to load it"))
}

/// Installs the hook of one agent; skipped when the agent is not on this machine.
pub fn install_hook(agent: HookAgent, home: &Path) -> Result<HookResult> {
    let base = agent_home(agent, home);
    if !base.exists() {
        return Ok(HookResult::new(agent, base, HookStatus::Skipped));
    }
    match agent {
        HookAgent::Claude => install_json_hook(agent, base.join("settings.json"), claude_entry()),
        HookAgent::Codex => install_json_hook(agent, base.join("hooks.json"), codex_entry()),
        HookAgent::Hermes => install_hermes_hook(base.join("config.yaml")),
        HookAgent::Openclaw => install_openclaw_hook(&base),
    }
}

/// Every agent found on this machine gets its hook.
pub fn install_hooks(home: &Path) -> Result<Vec<HookResult>> {
    HOOK_AGENTS.iter().map(|agent| install_hook(*agent, home)).collect()
}

/// The agents on this machine, by the presence of their home directory.
pub fn find_hook_agents(home: &Path) -> Vec<HookAgent> {
    HOOK_AGENTS.into_iter().filter(|agent| agent_home(*agent, home).exists()).collect()
}

/// Removes our commands from the SessionStart entries; entries and keys that empty out disappear
/// with them.
fn remove_json_hook(agent: HookAgent, file: PathBuf) -> Result<HookResult> {
    let mut json = match read_json_object(&file)? {
        JsonFile::Missing => return Ok(HookResult::new(agent, file, HookStatus::Absent)),
        JsonFile::Unparseable => {
            return Ok(HookResult::new(agent, file, HookStatus::Manual)
                .with_note(format!("not plain JSON; remove the \"{SYNC_MARKER}\" hook by hand")));
        }
        JsonFile::Object(map) => map,
    };
    let mut hooks = object_at(&json, "hooks");
    if !has_sync_hook(hooks.get("SessionStart")) {
        return Ok(HookResult::new(agent, file, HookStatus::Absent));
    }
    let entries = hooks.get("SessionStart").and_then(Value::as_array).cloned().unwrap_or_default();
    let kept: Vec<Value> = entries
        .into_iter()
        .filter_map(|mut entry| {
            let Some(commands) = entry.get("hooks").and_then(Value::as_array) else {
                return Some(entry);
            };
            let remaining: Vec<Value> = commands.iter().filter(|hook| !is_sync_command(hook)).cloned().collect();
            if remaining.len() == commands.len() {
                return Some(entry);
            }
            if remaining.is_empty() {
                return None;
            }
            entry["hooks"] = Value::Array(remaining);
            Some(entry)
        })
        .collect();
    if kept.is_empty() {
        hooks.shift_remove("SessionStart");
    } else {
        hooks.insert("SessionStart".into(), Value::Array(kept));
    }
    if hooks.is_empty() {
        json.shift_remove("hooks");
    } else {
        json.insert("hooks".into(), Value::Object(hooks));
    }
    write_json(&file, &Value::Object(json))?;
    Ok(HookResult::new(agent, file, HookStatus::Removed))
}

/// Only the exact block the installer appended is removed; a hand-edited hooks section stays,
/// because cutting lines out of someone's YAML risks breaking what they wrote around it.
fn remove_hermes_hook(file: PathBuf) -> Result<HookResult> {
    let agent = HookAgent::Hermes;
    let text = match std::fs::read_to_string(&file) {
        Ok(text) => text,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
            return Ok(HookResult::new(agent, file, HookStatus::Absent));
        }
        Err(error) => return Err(error.into()),
    };
    if !text.contains(SYNC_MARKER) {
        return Ok(HookResult::new(agent, file, HookStatus::Absent));
    }
    let block = hermes_block();
    let Some(index) = text.find(&block) else {
        return Ok(HookResult::new(agent, file, HookStatus::Manual)
            .with_note(format!("the hooks were edited; remove the \"{SYNC_MARKER}\" lines by hand")));
    };
    let joined = format!("{}{}", &text[..index], &text[index + block.len()..]);
    let collapsed = regex_lite::Regex::new(r"\n{3,}").expect("valid regex").replace_all(&joined, "\n\n").into_owned();
    let mut next =
        if collapsed.ends_with('\n') { format!("{}\n", collapsed.trim_end_matches('\n')) } else { collapsed };
    if next.trim().is_empty() {
        next = String::new();
    }
    std::fs::write(&file, next)?;
    Ok(HookResult::new(agent, file, HookStatus::Removed))
}

/// The hook folder is ours and is deleted outright; the config entry goes when the file is plain
/// JSON.
fn remove_openclaw_hook(home: &Path) -> Result<HookResult> {
    let agent = HookAgent::Openclaw;
    let dir = home.join("hooks").join(OPENCLAW_HOOK);
    let config_file = home.join("openclaw.json");
    let had_files = dir.exists();
    if had_files {
        std::fs::remove_dir_all(&dir)?;
    }
    let mut config = match read_json_object(&config_file)? {
        JsonFile::Unparseable => {
            return Ok(HookResult::new(agent, config_file, HookStatus::Manual).with_note(format!(
                "hook folder {} removed; the config is not plain JSON, remove the \"{OPENCLAW_HOOK}\" entry by hand and restart the gateway",
                dir.display()
            )));
        }
        JsonFile::Missing => Map::new(),
        JsonFile::Object(map) => map,
    };
    let mut hooks = object_at(&config, "hooks");
    let mut internal = object_at(&hooks, "internal");
    let mut entries = object_at(&internal, "entries");
    if !entries.contains_key(OPENCLAW_HOOK) {
        let status = if had_files { HookStatus::Removed } else { HookStatus::Absent };
        return Ok(HookResult::new(agent, config_file, status));
    }
    entries.shift_remove(OPENCLAW_HOOK);
    internal.insert("entries".into(), Value::Object(entries));
    hooks.insert("internal".into(), Value::Object(internal));
    config.insert("hooks".into(), Value::Object(hooks));
    write_json(&config_file, &Value::Object(config))?;
    Ok(HookResult::new(agent, config_file, HookStatus::Removed).with_note("restart the gateway to drop it"))
}

/// Removes the hook of one agent; skipped when the agent is not on this machine.
pub fn remove_hook(agent: HookAgent, home: &Path) -> Result<HookResult> {
    let base = agent_home(agent, home);
    if !base.exists() {
        return Ok(HookResult::new(agent, base, HookStatus::Skipped));
    }
    match agent {
        HookAgent::Claude => remove_json_hook(agent, base.join("settings.json")),
        HookAgent::Codex => remove_json_hook(agent, base.join("hooks.json")),
        HookAgent::Hermes => remove_hermes_hook(base.join("config.yaml")),
        HookAgent::Openclaw => remove_openclaw_hook(&base),
    }
}

/// Removes the hook from every agent found on this machine.
pub fn remove_hooks(home: &Path) -> Result<Vec<HookResult>> {
    HOOK_AGENTS.iter().map(|agent| remove_hook(*agent, home)).collect()
}
