use gatana_cli::skills::hooks::{
    HookAgent, HookResult, find_hook_agents, install_hook, install_hooks, remove_hook, remove_hooks,
};
use serde_json::{Value, json};
use std::path::Path;

fn statuses(results: &[HookResult]) -> Vec<String> {
    results
        .iter()
        .map(|result| {
            format!("{}:{}", result.agent.as_str(), serde_json::to_value(result.status).unwrap().as_str().unwrap())
        })
        .collect()
}

fn status(result: HookResult) -> String {
    serde_json::to_value(result.status).unwrap().as_str().unwrap().to_string()
}

fn read_json(path: &Path) -> Value {
    serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap()
}

#[test]
fn agents_that_are_not_on_the_machine_are_skipped_and_the_ones_that_are_get_a_hook_once() {
    let home = tempfile::tempdir().unwrap();
    std::fs::create_dir(home.path().join(".claude")).unwrap();
    std::fs::create_dir(home.path().join(".codex")).unwrap();

    let first = install_hooks(home.path()).unwrap();
    assert_eq!(statuses(&first), ["claude:installed", "codex:installed", "hermes:skipped", "openclaw:skipped"]);
    let claude = read_json(&home.path().join(".claude/settings.json"));
    assert_eq!(claude["hooks"]["SessionStart"][0]["hooks"][0]["command"], "gatana skills sync --quiet");
    let codex = read_json(&home.path().join(".codex/hooks.json"));
    assert_eq!(codex["hooks"]["SessionStart"][0]["hooks"][0]["command"], "gatana skills sync --quiet");
    assert_eq!(codex["hooks"]["SessionStart"][0]["hooks"][0]["timeout"], 60);

    let second = install_hooks(home.path()).unwrap();
    assert_eq!(statuses(&second), ["claude:present", "codex:present", "hermes:skipped", "openclaw:skipped"]);
}

#[test]
fn existing_claude_settings_and_other_session_start_hooks_are_kept_in_their_order() {
    let home = tempfile::tempdir().unwrap();
    std::fs::create_dir(home.path().join(".claude")).unwrap();
    let file = home.path().join(".claude/settings.json");
    std::fs::write(
        &file,
        json!({ "model": "opus", "hooks": { "SessionStart": [{ "hooks": [{ "type": "command", "command": "echo hi" }] }], "Stop": [] } })
            .to_string(),
    )
    .unwrap();
    assert_eq!(status(install_hook(HookAgent::Claude, home.path()).unwrap()), "installed");
    let settings = read_json(&file);
    assert_eq!(settings["model"], "opus");
    assert_eq!(settings["hooks"]["Stop"], json!([]));
    assert_eq!(settings["hooks"]["SessionStart"].as_array().unwrap().len(), 2);
    assert_eq!(settings["hooks"]["SessionStart"][0]["hooks"][0]["command"], "echo hi");
    // The user's keys keep their place in the file.
    let keys: Vec<&String> = settings.as_object().unwrap().keys().collect();
    assert_eq!(keys, ["model", "hooks"]);
}

#[test]
fn a_settings_file_that_is_not_plain_json_is_left_alone_and_reported() {
    let home = tempfile::tempdir().unwrap();
    std::fs::create_dir(home.path().join(".claude")).unwrap();
    let file = home.path().join(".claude/settings.json");
    let text = "{\n  // my comment\n  \"model\": \"opus\"\n}\n";
    std::fs::write(&file, text).unwrap();
    assert_eq!(status(install_hook(HookAgent::Claude, home.path()).unwrap()), "manual");
    assert_eq!(std::fs::read_to_string(&file).unwrap(), text);
}

#[test]
fn hermes_gets_the_block_appended_with_comments_intact_and_a_config_with_hooks_is_not_rewritten() {
    let home = tempfile::tempdir().unwrap();
    std::fs::create_dir(home.path().join(".hermes")).unwrap();
    let file = home.path().join(".hermes/config.yaml");
    std::fs::write(&file, "# my hermes config\nmodel: gpt\n").unwrap();
    assert_eq!(status(install_hook(HookAgent::Hermes, home.path()).unwrap()), "installed");
    let text = std::fs::read_to_string(&file).unwrap();
    assert!(text.starts_with("# my hermes config\nmodel: gpt\n"));
    let config = gatana_cli::yaml::load(&text).unwrap();
    assert_eq!(config["model"], "gpt");
    assert_eq!(config["hooks"]["on_session_start"][0]["command"], "gatana skills sync hermes --quiet");
    assert_eq!(status(install_hook(HookAgent::Hermes, home.path()).unwrap()), "present");

    let hand_written = "hooks:\n  on_session_start:\n    - command: \"echo hi\"\n";
    std::fs::write(&file, hand_written).unwrap();
    assert_eq!(status(install_hook(HookAgent::Hermes, home.path()).unwrap()), "manual");
    assert_eq!(std::fs::read_to_string(&file).unwrap(), hand_written);
}

#[test]
fn openclaw_gets_the_hook_folder_and_an_enabled_entry_and_other_config_is_kept() {
    let home = tempfile::tempdir().unwrap();
    std::fs::create_dir(home.path().join(".openclaw")).unwrap();
    std::fs::write(
        home.path().join(".openclaw/openclaw.json"),
        json!({ "agents": { "list": [] }, "hooks": { "internal": { "entries": { "other": { "enabled": true } } } } })
            .to_string(),
    )
    .unwrap();
    assert_eq!(status(install_hook(HookAgent::Openclaw, home.path()).unwrap()), "installed");
    let hook_md = std::fs::read_to_string(home.path().join(".openclaw/hooks/gatana-skills/HOOK.md")).unwrap();
    assert!(hook_md.contains(r#""events": ["gateway:startup", "command:new", "command:reset"]"#));
    let handler = std::fs::read_to_string(home.path().join(".openclaw/hooks/gatana-skills/handler.ts")).unwrap();
    assert!(handler.contains("execFile('gatana', ['skills', 'sync', '--quiet']"));
    let config = read_json(&home.path().join(".openclaw/openclaw.json"));
    assert_eq!(config["agents"], json!({ "list": [] }));
    assert_eq!(config["hooks"]["internal"]["enabled"], true);
    assert_eq!(
        config["hooks"]["internal"]["entries"],
        json!({ "other": { "enabled": true }, "gatana-skills": { "enabled": true } })
    );
    assert_eq!(status(install_hook(HookAgent::Openclaw, home.path()).unwrap()), "present");
}

#[test]
fn remove_hooks_takes_our_hook_out_of_every_agent_and_keeps_the_rest() {
    let home = tempfile::tempdir().unwrap();
    std::fs::create_dir(home.path().join(".claude")).unwrap();
    std::fs::create_dir(home.path().join(".codex")).unwrap();
    let claude_file = home.path().join(".claude/settings.json");
    std::fs::write(
        &claude_file,
        json!({ "model": "opus", "hooks": { "SessionStart": [{ "hooks": [{ "type": "command", "command": "echo hi" }] }], "Stop": [] } })
            .to_string(),
    )
    .unwrap();
    install_hooks(home.path()).unwrap();

    let results = remove_hooks(home.path()).unwrap();
    assert_eq!(statuses(&results), ["claude:removed", "codex:removed", "hermes:skipped", "openclaw:skipped"]);
    let claude = read_json(&claude_file);
    assert_eq!(claude["model"], "opus");
    assert_eq!(claude["hooks"]["Stop"], json!([]));
    assert_eq!(claude["hooks"]["SessionStart"].as_array().unwrap().len(), 1);
    assert_eq!(claude["hooks"]["SessionStart"][0]["hooks"][0]["command"], "echo hi");
    // Codex had only our hook: the emptied keys disappear with it.
    let codex = read_json(&home.path().join(".codex/hooks.json"));
    assert!(codex.get("hooks").is_none());

    // A second removal finds nothing, and the hooks can come back.
    assert_eq!(status(remove_hook(HookAgent::Claude, home.path()).unwrap()), "absent");
    assert_eq!(status(install_hook(HookAgent::Claude, home.path()).unwrap()), "installed");
}

#[test]
fn remove_hooks_cuts_only_the_exact_hermes_block_and_leaves_edited_hooks_for_the_hand() {
    let home = tempfile::tempdir().unwrap();
    std::fs::create_dir(home.path().join(".hermes")).unwrap();
    let file = home.path().join(".hermes/config.yaml");
    std::fs::write(&file, "# my hermes config\nmodel: gpt\n").unwrap();
    install_hook(HookAgent::Hermes, home.path()).unwrap();

    assert_eq!(status(remove_hook(HookAgent::Hermes, home.path()).unwrap()), "removed");
    assert_eq!(std::fs::read_to_string(&file).unwrap(), "# my hermes config\nmodel: gpt\n");
    assert_eq!(status(remove_hook(HookAgent::Hermes, home.path()).unwrap()), "absent");

    std::fs::write(&file, "hooks:\n  on_session_start:\n    - command: \"gatana skills sync hermes --quiet\"\n")
        .unwrap();
    assert_eq!(status(remove_hook(HookAgent::Hermes, home.path()).unwrap()), "manual");
    assert!(std::fs::read_to_string(&file).unwrap().contains("gatana skills sync hermes"));
}

#[test]
fn remove_hooks_deletes_the_openclaw_folder_and_entry_and_keeps_other_entries() {
    let home = tempfile::tempdir().unwrap();
    std::fs::create_dir(home.path().join(".openclaw")).unwrap();
    std::fs::write(
        home.path().join(".openclaw/openclaw.json"),
        json!({ "hooks": { "internal": { "entries": { "other": { "enabled": true } } } } }).to_string(),
    )
    .unwrap();
    install_hook(HookAgent::Openclaw, home.path()).unwrap();

    assert_eq!(status(remove_hook(HookAgent::Openclaw, home.path()).unwrap()), "removed");
    assert_eq!(find_hook_agents(home.path()), vec![HookAgent::Openclaw]);
    assert!(!home.path().join(".openclaw/hooks/gatana-skills/HOOK.md").exists());
    let config = read_json(&home.path().join(".openclaw/openclaw.json"));
    assert_eq!(config["hooks"]["internal"]["entries"], json!({ "other": { "enabled": true } }));
    assert_eq!(status(remove_hook(HookAgent::Openclaw, home.path()).unwrap()), "absent");
}

#[test]
fn the_agents_on_the_machine_are_found_by_their_home_folders() {
    let home = tempfile::tempdir().unwrap();
    assert!(find_hook_agents(home.path()).is_empty());
    std::fs::create_dir(home.path().join(".codex")).unwrap();
    std::fs::create_dir(home.path().join(".openclaw")).unwrap();
    assert_eq!(find_hook_agents(home.path()), vec![HookAgent::Codex, HookAgent::Openclaw]);
}
