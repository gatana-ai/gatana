use gatana_cli::connect::{config_file, install, render_snippet, skill_targets};
use gatana_cli::skills::hooks::{HookAgent, HookResult};
use serde_json::{Value, json};
use std::path::Path;

const URL: &str = "https://acme.gatana.ai/mcp";

fn status(result: &HookResult) -> String {
    serde_json::to_value(result.status).unwrap().as_str().unwrap().to_string()
}

fn read_json(path: &Path) -> Value {
    serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap()
}

#[test]
fn claude_code_gets_the_server_in_its_user_file_once_and_keeps_the_rest() {
    let home = tempfile::tempdir().unwrap();
    let file = home.path().join(".claude.json");
    assert_eq!(config_file(HookAgent::Claude, home.path()), file);
    std::fs::write(&file, json!({ "numStartups": 3, "mcpServers": { "other": { "type": "stdio" } } }).to_string())
        .unwrap();

    let first = install(HookAgent::Claude, home.path(), URL).unwrap();
    assert_eq!(status(&first), "installed");
    let settings = read_json(&file);
    assert_eq!(settings["numStartups"], 3);
    assert_eq!(settings["mcpServers"]["other"]["type"], "stdio");
    assert_eq!(settings["mcpServers"]["gatana"], json!({ "type": "http", "url": URL }));

    // A second run, even with another URL, leaves the connected entry alone.
    let second = install(HookAgent::Claude, home.path(), "https://gatana.ai/mcp").unwrap();
    assert_eq!(status(&second), "present");
    assert_eq!(read_json(&file)["mcpServers"]["gatana"]["url"], URL);
}

#[test]
fn a_missing_file_is_created_and_a_file_that_is_not_plain_json_is_left_alone() {
    let home = tempfile::tempdir().unwrap();
    let result = install(HookAgent::Openclaw, home.path(), URL).unwrap();
    assert_eq!(status(&result), "installed");
    assert!(result.note.as_deref().unwrap().contains("restart"));
    let config = read_json(&home.path().join(".openclaw/openclaw.json"));
    assert_eq!(config["mcp"]["servers"]["gatana"], json!({ "url": URL, "transport": "streamable-http" }));

    let file = home.path().join(".claude.json");
    let text = "{\n  // comment\n  \"a\": 1\n}\n";
    std::fs::write(&file, text).unwrap();
    let result = install(HookAgent::Claude, home.path(), URL).unwrap();
    assert_eq!(status(&result), "manual");
    assert_eq!(std::fs::read_to_string(&file).unwrap(), text);
}

#[test]
fn codex_gets_a_table_appended_after_the_existing_text_and_only_once() {
    let home = tempfile::tempdir().unwrap();
    let file = home.path().join(".codex/config.toml");
    std::fs::create_dir_all(home.path().join(".codex")).unwrap();
    std::fs::write(&file, "model = \"o3\"\n\n[mcp_servers.other]\nurl = \"https://example.com\"").unwrap();

    assert_eq!(status(&install(HookAgent::Codex, home.path(), URL).unwrap()), "installed");
    let text = std::fs::read_to_string(&file).unwrap();
    assert_eq!(
        text,
        "model = \"o3\"\n\n[mcp_servers.other]\nurl = \"https://example.com\"\n\n[mcp_servers.gatana]\nurl = \"https://acme.gatana.ai/mcp\"\n"
    );
    assert_eq!(status(&install(HookAgent::Codex, home.path(), URL).unwrap()), "present");
    assert_eq!(std::fs::read_to_string(&file).unwrap(), text);

    // An inline entry under [mcp_servers] counts as present too.
    std::fs::write(&file, "[mcp_servers]\ngatana = { url = \"x\" }\n").unwrap();
    assert_eq!(status(&install(HookAgent::Codex, home.path(), URL).unwrap()), "present");
}

#[test]
fn hermes_gets_the_block_with_comments_intact_and_a_config_with_servers_is_not_rewritten() {
    let home = tempfile::tempdir().unwrap();
    let file = home.path().join(".hermes/config.yaml");
    std::fs::create_dir_all(home.path().join(".hermes")).unwrap();
    std::fs::write(&file, "# my hermes config\nmodel: gpt\n").unwrap();

    assert_eq!(status(&install(HookAgent::Hermes, home.path(), URL).unwrap()), "installed");
    let text = std::fs::read_to_string(&file).unwrap();
    assert!(text.starts_with("# my hermes config\nmodel: gpt\n\nmcp_servers:\n  gatana:\n"));
    assert!(text.contains("    url: 'https://acme.gatana.ai/mcp'\n    auth: oauth\n    enabled: true\n"));
    assert_eq!(status(&install(HookAgent::Hermes, home.path(), URL).unwrap()), "present");

    std::fs::write(&file, "mcp_servers:\n  other:\n    url: https://example.com\n").unwrap();
    let result = install(HookAgent::Hermes, home.path(), URL).unwrap();
    assert_eq!(status(&result), "manual");
    assert_eq!(std::fs::read_to_string(&file).unwrap(), "mcp_servers:\n  other:\n    url: https://example.com\n");
}

#[test]
fn snippets_carry_the_url_and_each_agent_has_skill_folders() {
    for agent in [HookAgent::Claude, HookAgent::Codex, HookAgent::Hermes, HookAgent::Openclaw] {
        let (snippet, how) = render_snippet(agent, URL);
        assert!(snippet.contains(URL), "{agent:?}");
        assert!(!how.is_empty());
        assert!(!skill_targets(agent).is_empty());
    }
}
