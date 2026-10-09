//! `gatana install`: the Gatana gateway as an MCP server in the configuration of each agent. The
//! entries hold the URL only. Every agent signs in by itself, in the browser, the first time it
//! connects; the connection then shows under Clients & API Keys in the dashboard, and the files
//! here hold no secret.

use crate::skills::hooks::{HookAgent, HookResult, HookStatus, JsonFile, agent_home, read_json_object, write_json};
use anyhow::Result;
use serde_json::{Map, Value, json};
use std::path::{Path, PathBuf};

/// The name of the server in every agent's configuration.
pub const SERVER_NAME: &str = "gatana";

/// The MCP endpoint of an organization: its base URL plus `/mcp`.
pub fn mcp_url(base_url: &str) -> String {
    format!("{}/mcp", base_url.trim_end_matches('/'))
}

/// The file that holds the MCP servers of an agent. Claude Code keeps its user-level servers in
/// `~/.claude.json`, next to its home directory, not inside it.
pub fn config_file(agent: HookAgent, home: &Path) -> PathBuf {
    match agent {
        HookAgent::Claude => home.join(".claude.json"),
        HookAgent::Codex => agent_home(agent, home).join("config.toml"),
        HookAgent::Hermes => agent_home(agent, home).join("config.yaml"),
        HookAgent::Openclaw => agent_home(agent, home).join("openclaw.json"),
    }
}

/// The skills presets (targets.rs) an agent reads. OpenClaw reads the default folders, as its
/// session-start hook assumes.
pub fn skill_targets(agent: HookAgent) -> &'static [&'static str] {
    match agent {
        HookAgent::Claude => &["claude"],
        HookAgent::Codex => &["agents"],
        HookAgent::Hermes => &["hermes"],
        HookAgent::Openclaw => &["claude", "agents"],
    }
}

/// What the person does in the agent after the install: the sign-in belongs to them.
pub fn next_step(agent: HookAgent) -> &'static str {
    match agent {
        HookAgent::Claude => "run /mcp in Claude Code, select gatana, then Authenticate and sign in",
        HookAgent::Codex => "run \"codex mcp login gatana\" and sign in",
        HookAgent::Hermes => "run /reload-mcp in Hermes and sign in when it asks",
        HookAgent::Openclaw => "restart the OpenClaw gateway so it loads the server and the hook",
    }
}

fn claude_entry(url: &str) -> Value {
    json!({ "type": "http", "url": url })
}

fn codex_block(url: &str) -> String {
    format!("[mcp_servers.{SERVER_NAME}]\nurl = \"{url}\"")
}

fn hermes_block(url: &str) -> String {
    [
        "mcp_servers:".to_string(),
        format!("  {SERVER_NAME}:"),
        format!("    url: '{url}'"),
        "    auth: oauth".to_string(),
        "    enabled: true".to_string(),
    ]
    .join("\n")
}

fn openclaw_entry(url: &str) -> Value {
    json!({ "url": url, "transport": "streamable-http" })
}

fn pretty(value: &Value) -> String {
    serde_json::to_string_pretty(value).unwrap_or_default()
}

/// The entry of one agent and where it goes, for merging by hand when the file cannot be edited.
pub fn render_snippet(agent: HookAgent, url: &str) -> (String, String) {
    match agent {
        HookAgent::Claude => (
            pretty(&json!({ "mcpServers": { SERVER_NAME: claude_entry(url) } })),
            format!(
                "Merge into ~/.claude.json, or run: claude mcp add --transport http --scope user {SERVER_NAME} {url}"
            ),
        ),
        HookAgent::Codex => {
            (codex_block(url), format!("Add to ~/.codex/config.toml, or run: codex mcp add {SERVER_NAME} --url {url}"))
        }
        HookAgent::Hermes => (
            hermes_block(url),
            format!("Merge into ~/.hermes/config.yaml, or run: hermes mcp add {SERVER_NAME} --url {url} --auth oauth"),
        ),
        HookAgent::Openclaw => (
            pretty(&json!({ "mcp": { "servers": { SERVER_NAME: openclaw_entry(url) } } })),
            "Merge into ~/.openclaw/openclaw.json, then restart the gateway.".to_string(),
        ),
    }
}

/// Claude Code and OpenClaw keep their servers in a JSON object at a path: `mcpServers` and
/// `mcp.servers`. An entry named gatana that is already there is kept as it is, whatever its URL:
/// the agent is connected, and a new URL would make it sign in again.
fn install_json_entry(agent: HookAgent, file: PathBuf, path: &[&str], entry: Value) -> Result<HookResult> {
    let root = match read_json_object(&file)? {
        JsonFile::Unparseable => {
            return Ok(
                HookResult::new(agent, file, HookStatus::Manual).with_note("not plain JSON; add the server by hand")
            );
        }
        JsonFile::Missing => Map::new(),
        JsonFile::Object(map) => map,
    };
    let mut root = Value::Object(root);
    let mut node = &mut root;
    for key in path {
        let map = node.as_object_mut().expect("the path leads through objects only");
        let child = map.entry(*key).or_insert_with(|| Value::Object(Map::new()));
        if !child.is_object() {
            return Ok(HookResult::new(agent, file, HookStatus::Manual)
                .with_note(format!("\"{}\" is not an object; add the server by hand", path.join("."))));
        }
        node = child;
    }
    let servers = node.as_object_mut().expect("checked above");
    if servers.contains_key(SERVER_NAME) {
        return Ok(HookResult::new(agent, file, HookStatus::Present));
    }
    servers.insert(SERVER_NAME.into(), entry);
    write_json(&file, &root)?;
    Ok(HookResult::new(agent, file, HookStatus::Installed))
}

fn read_text(file: &Path) -> Result<String> {
    match std::fs::read_to_string(file) {
        Ok(text) => Ok(text),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(String::new()),
        Err(error) => Err(error.into()),
    }
}

/// Appends a block to a file people edit by hand, after a blank line.
fn append_block(file: &Path, text: &str, block: &str) -> Result<()> {
    let separator = if text.is_empty() || text.ends_with('\n') { "" } else { "\n" };
    let gap = if text.is_empty() { "" } else { "\n" };
    if let Some(parent) = file.parent() {
        std::fs::create_dir_all(parent)?;
    }
    std::fs::write(file, format!("{text}{separator}{gap}{block}\n"))?;
    Ok(())
}

/// A table header for the server, with or without quotes or a sub-table, or an inline entry under
/// `[mcp_servers]`.
fn has_codex_entry(text: &str) -> bool {
    regex_lite::Regex::new(r#"(?m)^[ \t]*(\[mcp_servers\."?gatana"?[\].]|gatana[ \t]*=)"#)
        .expect("valid regex")
        .is_match(text)
}

/// Codex keeps TOML, which the CLI does not parse. A table header appended at the end is valid
/// wherever the file ends, so the entry is added as text; an entry that is there in any spelling
/// is left alone.
fn install_codex(file: PathBuf, url: &str) -> Result<HookResult> {
    let agent = HookAgent::Codex;
    let text = read_text(&file)?;
    if has_codex_entry(&text) {
        return Ok(HookResult::new(agent, file, HookStatus::Present));
    }
    append_block(&file, &text, &codex_block(url))?;
    Ok(HookResult::new(agent, file, HookStatus::Installed))
}

/// Hermes keeps YAML that people edit by hand, and a parse-and-dump would drop their comments. So:
/// no `mcp_servers` key yet, append ours as text; the key with our server in it, done; the key with
/// other servers only, leave the file alone and ask for a manual merge.
fn install_hermes(file: PathBuf, url: &str) -> Result<HookResult> {
    let agent = HookAgent::Hermes;
    let text = read_text(&file)?;
    let config = match crate::yaml::load(&text) {
        Ok(config) => config,
        Err(_) => {
            return Ok(
                HookResult::new(agent, file, HookStatus::Manual).with_note("not valid YAML; add the server by hand")
            );
        }
    };
    match config.get("mcp_servers") {
        Some(servers) if servers.get(SERVER_NAME).is_some() => Ok(HookResult::new(agent, file, HookStatus::Present)),
        Some(_) => Ok(HookResult::new(agent, file, HookStatus::Manual)
            .with_note("already has an mcp_servers section; add the server by hand")),
        None => {
            append_block(&file, &text, &hermes_block(url))?;
            Ok(HookResult::new(agent, file, HookStatus::Installed))
        }
    }
}

/// Adds the gateway to one agent's configuration. The file is created when it is missing, so an
/// agent that is not on the machine yet finds the server when it is installed.
pub fn install(agent: HookAgent, home: &Path, url: &str) -> Result<HookResult> {
    let file = config_file(agent, home);
    match agent {
        HookAgent::Claude => install_json_entry(agent, file, &["mcpServers"], claude_entry(url)),
        HookAgent::Codex => install_codex(file, url),
        HookAgent::Hermes => install_hermes(file, url),
        HookAgent::Openclaw => {
            install_json_entry(agent, file, &["mcp", "servers"], openclaw_entry(url)).map(|result| {
                match result.status {
                    HookStatus::Installed => result.with_note("restart the gateway to load it"),
                    _ => result,
                }
            })
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_endpoint_is_mcp_under_the_organization() {
        assert_eq!(mcp_url("https://acme.gatana.ai"), "https://acme.gatana.ai/mcp");
        assert_eq!(mcp_url("https://acme.gatana.ai/"), "https://acme.gatana.ai/mcp");
    }

    #[test]
    fn codex_entries_are_found_in_every_spelling() {
        assert!(has_codex_entry("[mcp_servers.gatana]\nurl = \"x\"\n"));
        assert!(has_codex_entry("[mcp_servers.\"gatana\"]\nurl = \"x\"\n"));
        assert!(has_codex_entry("[mcp_servers.gatana.env]\nA = \"1\"\n"));
        assert!(has_codex_entry("[mcp_servers]\ngatana = { url = \"x\" }\n"));
        assert!(!has_codex_entry("[mcp_servers.gatana-dev]\nurl = \"x\"\n"));
        assert!(!has_codex_entry("# gatana = nothing\nmodel = \"o3\"\n"));
    }
}
