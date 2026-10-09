//! `gatana install`: sign in when needed, choose the agents on this machine, and give each one the
//! gateway as an MCP server, the skills of the organization, and the session-start hook that keeps
//! the skills current.

use super::{config, skills};
use crate::cli::InstallAgentsArgs;
use crate::connect;
use crate::context::Context;
use crate::output;
use crate::skills::hooks::{self, HOOK_AGENTS, HookAgent, HookResult, HookStatus, agent_home};
use crate::skills::sync::{SyncOptions, sync_targets};
use crate::skills::targets::{home, prepare_targets, resolve_targets};
use crate::util::get_path;
use anyhow::{Result, bail};
use serde_json::Value;
use std::io::IsTerminal;

pub async fn run(context: Context, args: InstallAgentsArgs) -> Result<()> {
    let InstallAgentsArgs { agents, no_browser } = args;
    let context = signed_in(context, !no_browser).await?;
    let agents = choose_agents(agents)?;
    let home = home();
    let url = connect::mcp_url(&context.config()?.base_url);

    // The gateway first: it creates the agent's folder when the agent is not on the machine yet,
    // so the skills and the hook below find a place too.
    output::println(&format!("\n{} {url}", output::bold("Gateway:")));
    for agent in &agents {
        report_connection(&connect::install(*agent, &home, &url)?, &url);
    }

    output::println(&format!("\n{}", output::bold("Skills:")));
    let (api, identity) = skills::connect(&context, None).await?;
    let mut targets: Vec<String> = Vec::new();
    for name in agents.iter().flat_map(|agent| connect::skill_targets(*agent)) {
        if !targets.iter().any(|known| known == name) {
            targets.push(name.to_string());
        }
    }
    let dirs = prepare_targets(&resolve_targets(&targets, &home))?;
    let options = SyncOptions { prune: true, ..SyncOptions::default() };
    let summaries = sync_targets(&api, &identity, &dirs, &options).await?;
    skills::report_summaries(&summaries, false, false);

    output::println(&format!("\n{}", output::bold("Hooks:")));
    let results = agents.iter().map(|agent| hooks::install_hook(*agent, &home)).collect::<Result<Vec<HookResult>>>()?;
    skills::report_hooks(&results);

    output::println(&format!("\n{}", output::bold("Next, sign in from each agent:")));
    for agent in &agents {
        output::println(&format!("  {}: {}", output::bold(agent.label()), connect::next_step(*agent)));
    }
    Ok(())
}

/// Who the credentials belong to, or None when there are none or they do not work.
async fn whoami(context: &Context) -> Option<String> {
    let me = context.api().await.ok()?.v1().get_auth_me().value().await.ok()?;
    let text = |path: &str| get_path(&me, path).and_then(Value::as_str).unwrap_or_default().to_string();
    Some(format!("{} at {}", text("user.email"), text("tenant.id")))
}

/// The context with working credentials: the one given, or a new one after a browser sign-in.
async fn signed_in(context: Context, browser: bool) -> Result<Context> {
    if let Some(who) = whoami(&context).await {
        output::println(&format!("Signed in as {}.", output::bold(&who)));
        return Ok(context);
    }
    output::println(&output::bold("Sign in to Gatana first."));
    config::apex_login(&context, None, browser).await?;
    // The old context cached the failure; a new one reads the config file again.
    let context = Context::new()?;
    match whoami(&context).await {
        Some(who) => {
            output::println(&format!("Signed in as {}.", output::bold(&who)));
            Ok(context)
        }
        None => {
            bail!("The sign-in did not give working credentials. Run \"gatana config current\" to see what is used.")
        }
    }
}

/// The agents named on the command line, or chosen in a menu where the agents found on this
/// machine are checked already.
fn choose_agents(given: Vec<HookAgent>) -> Result<Vec<HookAgent>> {
    if !given.is_empty() {
        let mut agents: Vec<HookAgent> = Vec::new();
        for agent in given {
            if !agents.contains(&agent) {
                agents.push(agent);
            }
        }
        return Ok(agents);
    }
    if !std::io::stdin().is_terminal() {
        bail!("Name the agents to connect, for example: gatana install claude codex");
    }
    let home = home();
    let found: Vec<bool> = HOOK_AGENTS.iter().map(|agent| agent_home(*agent, &home).exists()).collect();
    let labels: Vec<String> = HOOK_AGENTS
        .iter()
        .zip(&found)
        .map(|(agent, found)| if *found { agent.label().to_string() } else { format!("{} (not found)", agent.label()) })
        .collect();
    let picked = dialoguer::MultiSelect::new()
        .with_prompt("Where to install? Space selects, Enter confirms")
        .items(&labels)
        .defaults(&found)
        .interact()?;
    if picked.is_empty() {
        bail!("Nothing selected.");
    }
    Ok(picked.into_iter().map(|index| HOOK_AGENTS[index]).collect())
}

fn report_connection(result: &HookResult, url: &str) {
    let (agent, file) = (result.agent.as_str(), output::tilde(&result.file));
    let note = result.note.as_ref().map(|note| format!(" ({note})")).unwrap_or_default();
    match result.status {
        HookStatus::Installed => {
            output::println(&format!("gateway {} for {agent}: {file}{note}", output::green("added")))
        }
        HookStatus::Present => {
            output::println(&output::dim(&format!("gateway already configured for {agent}: {file}")))
        }
        HookStatus::Manual => {
            output::eprintln(&format!("{} gateway not added for {agent}: {file}{note}", output::yellow("warning:")));
            let (snippet, how) = connect::render_snippet(result.agent, url);
            output::eprintln(&snippet);
            output::eprintln(&format!("{how}\n"));
        }
        HookStatus::Removed | HookStatus::Absent | HookStatus::Skipped => {}
    }
}
