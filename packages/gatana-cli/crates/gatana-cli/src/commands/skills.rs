//! `gatana skills ...`

use super::Silent;
use crate::cli::{InstallArgs, SkillsCommand, SyncArgs};
use crate::config::{default_organization, tenant_from_url};
use crate::context::Context;
use crate::output::{self, Column, Options};
use crate::skills::api::HttpSkillsApi;
use crate::skills::hooks::{self, HookAgent, HookResult, HookStatus};
use crate::skills::manifest::SubscriptionKind;
use crate::skills::plan::{OpKind, Reason};
use crate::skills::push::{PushAction, PushOptions, PushResult, push_skills};
use crate::skills::subscriptions::{describe_subscription, resolve_subscription};
use crate::skills::sync::{SkillsIdentity, SyncOptions, SyncSummary, sync_targets};
use crate::skills::targets::{home, prepare_targets, preset, resolve_targets};
use anyhow::{Result, anyhow, bail};
use serde_json::{Value, json};

pub async fn run(context: &Context, command: SkillsCommand) -> Result<()> {
    match command {
        SkillsCommand::Install(args) => install(context, args).await,
        SkillsCommand::Sync(args) => sync(context, args).await,
        SkillsCommand::RemoveHooks { agent } => remove_hooks(agent),
        SkillsCommand::Push { paths, collection, force, dry_run, org } => {
            let org_context = org_context(org.as_deref())?;
            let context = org_context.as_ref().unwrap_or(context);
            let (api, identity) = connect(context, org.as_deref()).await?;
            // Typed paths must hold a skill; the default agent folders may not exist yet.
            let explicit = !paths.is_empty();
            let paths = if explicit { paths } else { resolve_targets(&[], &home()) };
            let options = PushOptions { force, dry_run, collection, skip_empty: !explicit };
            let results = push_skills(&api, &identity, &paths, &options).await?;
            report_push(&results);
            if results.iter().any(|result| matches!(result.action, PushAction::Conflict | PushAction::Error)) {
                return Err(Silent.into());
            }
            Ok(())
        }
        SkillsCommand::Ls { query, collection, collections, org } => {
            let org_context = org_context(org.as_deref())?;
            let context = org_context.as_ref().unwrap_or(context);
            let (api, _) = connect(context, org.as_deref()).await?;
            if collections {
                crate::skills::show_collections(&api).await
            } else {
                crate::skills::show_skills(&api, None, query.as_deref(), collection.as_deref()).await
            }
        }
        SkillsCommand::Hook { agent, install } => {
            if install {
                let result = hooks::install_hook(agent, &home())?;
                return finish_hook_command(agent, result, report_hooks);
            }
            let (snippet, note) = hooks::render_hook_snippet(agent);
            output::println(&snippet);
            output::eprintln(&format!("\n{note}"));
            Ok(())
        }
    }
}

/// `--org` picks an organization from the config file instead of the resolved configuration.
fn org_context(org: Option<&str>) -> Result<Option<Context>> {
    org.map(Context::for_org).transpose()
}

/// The skills API and the organization the files are stamped with. The organization id is
/// recorded in every manifest and SKILL.md, so it must be known even when only a base URL is: the
/// first host label is the tenant.
async fn connect<'a>(context: &'a Context, org: Option<&str>) -> Result<(HttpSkillsApi<'a>, SkillsIdentity)> {
    let config = context.config().map_err(|error| match org {
        Some(org) => anyhow!("Organization {org} is not configured. Run \"gatana config login {org}\" first"),
        None => error,
    })?;
    let api = context.api().await?;
    let env = |name: &str| std::env::var(name).ok().filter(|value| !value.is_empty());
    let org_id = org
        .map(str::to_string)
        .or_else(|| env("GATANA_ORG_ID"))
        .or_else(|| if env("GATANA_API_KEY").is_some() { None } else { default_organization() })
        .unwrap_or_else(|| tenant_from_url(&config.base_url));
    let identity = SkillsIdentity { org_id, base_url: config.base_url.clone() };
    Ok((HttpSkillsApi::new(api, &config.base_url), identity))
}

/// The first install argument may be a name or the first target. Presets and anything path-like
/// keep their old meaning, so "install hermes" still targets ~/.hermes/skills and "./release" is
/// always a directory; skill and collection names cannot contain a slash.
fn is_target_word(word: &str) -> bool {
    preset(word).is_some()
        || word.contains('/')
        || word.starts_with('.')
        || word.starts_with('~')
        || std::path::Path::new(word).is_absolute()
}

async fn install(context: &Context, args: InstallArgs) -> Result<()> {
    let InstallArgs { mut name, mut targets, dry_run, no_prune, force, reset, collection, skill, no_hooks, quiet, org } =
        args;
    let named = collection || skill;
    if let Some(word) = name.clone().filter(|word| !named && is_target_word(word)) {
        targets.insert(0, word);
        name = None;
    }
    if named && name.is_none() {
        bail!("--collection and --skill need a name");
    }
    if name.is_some() && reset {
        bail!("--reset and a name exclude each other");
    }
    let org_context = org_context(org.as_deref())?;
    let context = org_context.as_ref().unwrap_or(context);
    let (api, identity) = connect(context, org.as_deref()).await?;
    let kind = if collection {
        Some(SubscriptionKind::Collection)
    } else if skill {
        Some(SubscriptionKind::Skill)
    } else {
        None
    };
    let subscribe = match &name {
        Some(name) => Some(resolve_subscription(&api, name, kind).await?),
        None => None,
    };
    let dirs = prepare_targets(&resolve_targets(&targets, &home()))?;
    let options = SyncOptions { dry_run, prune: !no_prune, force, subscribe, reset };
    let summaries = sync_targets(&api, &identity, &dirs, &options).await?;
    report_summaries(&summaries, dry_run, quiet);
    // --no-hooks is the only thing that keeps the hooks away. A quiet install reports only what
    // needs a hand.
    if !dry_run && !no_hooks {
        let results = hooks::install_hooks(&home())?;
        let shown: Vec<HookResult> =
            results.into_iter().filter(|result| !quiet || result.status == HookStatus::Manual).collect();
        report_hooks(&shown);
    }
    Ok(())
}

async fn sync(context: &Context, args: SyncArgs) -> Result<()> {
    let SyncArgs { targets, dry_run, no_prune, force, quiet, org } = args;
    let org_context = org_context(org.as_deref())?;
    let context = org_context.as_ref().unwrap_or(context);
    let (api, identity) = connect(context, org.as_deref()).await?;
    let dirs = prepare_targets(&resolve_targets(&targets, &home()))?;
    let options = SyncOptions { dry_run, prune: !no_prune, force, ..SyncOptions::default() };
    let summaries = sync_targets(&api, &identity, &dirs, &options).await?;
    report_summaries(&summaries, dry_run, quiet);
    Ok(())
}

const OP_COLUMNS: [Column; 3] =
    [Column::path("Action", "kind"), Column::path("Skill", "name"), Column::path("Reason", "reason")];

const PUSH_COLUMNS: [Column; 3] = [
    Column::path("Skill", "name"),
    Column::path("Action", "action"),
    Column::computed("Detail", |row| {
        row.get("detail").filter(|detail| !detail.is_null()).cloned().unwrap_or(json!(""))
    }),
];

fn describe_subscriptions(summary: &SyncSummary) -> String {
    match &summary.subscriptions {
        None => String::new(),
        Some(list) if list.is_empty() => " (no subscriptions: nothing is installed here until you install a collection or skill by name, or run \"gatana skills install --reset\")".to_string(),
        Some(list) => format!(" (following: {})", list.iter().map(describe_subscription).collect::<Vec<_>>().join(", ")),
    }
}

fn report_summaries(summaries: &[SyncSummary], dry_run: bool, quiet: bool) {
    for warning in summaries.iter().flat_map(|summary| &summary.warnings) {
        output::eprintln(&format!("warning: {warning}"));
    }
    if quiet {
        return;
    }
    if output::machine_readable() {
        let shown: Vec<SyncSummary> = summaries
            .iter()
            .map(|summary| SyncSummary { ops: if dry_run { summary.ops.clone() } else { None }, ..summary.clone() })
            .collect();
        output::print(&serde_json::to_value(shown).unwrap_or_default());
        return;
    }
    for summary in summaries {
        let dir = summary.dir.display();
        if dry_run {
            let changes: Vec<Value> = summary
                .ops()
                .iter()
                .filter(|op| op.kind != OpKind::Skip || op.reason != Reason::Unchanged)
                .map(|op| serde_json::to_value(op).unwrap_or_default())
                .collect();
            let verdict = if changes.is_empty() { "nothing to do" } else { "would apply" };
            output::println(&format!("{dir}: {verdict}{}", describe_subscriptions(summary)));
            if !changes.is_empty() {
                output::output(&Value::Array(changes), Options::columns(&OP_COLUMNS));
            }
            continue;
        }
        output::println(&format!(
            "{dir}: {} written, {} removed, {} skipped, {} skills{}",
            summary.written,
            summary.removed,
            summary.skipped,
            summary.total,
            describe_subscriptions(summary)
        ));
    }
}

/// Unchanged skills are counted, not listed: a push of a whole agent folder is mostly skills
/// nobody touched, and the rows that matter are the updates and the conflicts. Machine-readable
/// formats still carry every result.
fn report_push(results: &[PushResult]) {
    if output::machine_readable() {
        output::print(&serde_json::to_value(results).unwrap_or_default());
        return;
    }
    let shown: Vec<Value> = results
        .iter()
        .filter(|result| result.action != PushAction::Unchanged)
        .map(|result| serde_json::to_value(result).unwrap_or_default())
        .collect();
    if !shown.is_empty() {
        output::output(&Value::Array(shown), Options::columns(&PUSH_COLUMNS));
    }
    let count = |action: PushAction| results.iter().filter(|result| result.action == action).count();
    output::println(&format!(
        "{} created, {} updated, {} conflicts, {} errors, {} unchanged",
        count(PushAction::Created),
        count(PushAction::Updated),
        count(PushAction::Conflict),
        count(PushAction::Error),
        count(PushAction::Unchanged)
    ));
}

fn note(result: &HookResult) -> String {
    result.note.as_ref().map(|note| format!(" ({note})")).unwrap_or_default()
}

/// One line per agent found on the machine; agents that are not installed are not mentioned.
fn report_hooks(results: &[HookResult]) {
    for result in results {
        let (agent, file) = (result.agent.as_str(), result.file.display());
        match result.status {
            HookStatus::Installed => output::println(&format!("hook installed for {agent}: {file}{}", note(result))),
            HookStatus::Present => output::println(&format!("hook already installed for {agent}: {file}")),
            HookStatus::Manual => output::eprintln(
                format!(
                    "warning: hook for {agent} not installed: {file} {}",
                    result.note.as_deref().unwrap_or_default()
                )
                .trim_end(),
            ),
            _ => {}
        }
    }
}

fn report_hook_removals(results: &[HookResult]) {
    for result in results {
        let (agent, file) = (result.agent.as_str(), result.file.display());
        match result.status {
            HookStatus::Removed => output::println(&format!("hook removed for {agent}: {file}{}", note(result))),
            HookStatus::Absent => output::println(&format!("no hook installed for {agent}: {file}")),
            HookStatus::Manual => output::eprintln(
                format!("warning: hook for {agent} not removed: {file} {}", result.note.as_deref().unwrap_or_default())
                    .trim_end(),
            ),
            _ => {}
        }
    }
}

fn finish_hook_command(agent: HookAgent, result: HookResult, report: fn(&[HookResult])) -> Result<()> {
    if result.status == HookStatus::Skipped {
        output::eprintln(&format!(
            "{} is not installed on this machine: {} does not exist",
            agent.as_str(),
            result.file.display()
        ));
        return Err(Silent.into());
    }
    let manual = result.status == HookStatus::Manual;
    report(&[result]);
    if manual { Err(Silent.into()) } else { Ok(()) }
}

fn remove_hooks(agent: Option<HookAgent>) -> Result<()> {
    if let Some(agent) = agent {
        let result = hooks::remove_hook(agent, &home())?;
        return finish_hook_command(agent, result, report_hook_removals);
    }
    let results = hooks::remove_hooks(&home())?;
    report_hook_removals(&results);
    if results.iter().any(|result| result.status == HookStatus::Manual) {
        return Err(Silent.into());
    }
    Ok(())
}
