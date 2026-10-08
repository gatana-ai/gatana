//! Installs the skills of an organization into a directory, and keeps them current.

use super::api::{Skill, SkillsApi, is_not_found};
use super::frontmatter::{Revision, frontmatter_for, render_skill_md};
use super::manifest::{
    ManifestEntry, SkillsManifest, Subscription, SubscriptionKind, empty_manifest, read_manifest, sha256, write_atomic,
    write_manifest,
};
use super::plan::{LocalState, OpKind, PlanInput, Reason, SyncOp, compute_sync_plan};
use crate::util::{iso_millis, now_iso};
use anyhow::{Result, bail};
use futures_util::{StreamExt, stream};
use serde::Serialize;
use serde_json::Map;
use std::collections::{HashMap, HashSet};
use std::path::{Path, PathBuf};

const SKILL_FILE: &str = "SKILL.md";
const FETCH_CONCURRENCY: usize = 4;

/// The manifest entry of a skill written to disk; None when it disappeared since the listing.
type Written = Result<Option<(String, ManifestEntry)>>;

/// The organization the files are stamped with.
#[derive(Clone, Debug)]
pub struct SkillsIdentity {
    pub org_id: String,
    pub base_url: String,
}

#[derive(Clone, Debug, Default)]
pub struct SyncOptions {
    pub dry_run: bool,
    pub prune: bool,
    pub force: bool,
    /// Add this collection or skill to what the directory follows before syncing.
    pub subscribe: Option<Subscription>,
    /// Forget what the directory follows first: it takes every readable skill again.
    pub reset: bool,
}

#[derive(Clone, Debug, Serialize)]
pub struct SyncSummary {
    pub dir: PathBuf,
    pub written: usize,
    pub removed: usize,
    pub skipped: usize,
    /// Skills the manifest owns after the run.
    pub total: usize,
    /// What the directory follows, or null when it takes every readable skill.
    pub subscriptions: Option<Vec<Subscription>>,
    pub warnings: Vec<String>,
    /// Shown for dry runs only.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ops: Option<Vec<SyncOp>>,
}

impl SyncSummary {
    pub fn ops(&self) -> &[SyncOp] {
        self.ops.as_deref().unwrap_or_default()
    }
}

/// What the directory should hold. Without subscriptions: every skill the user can read. With
/// them: the skills of the followed collections and the followed skills themselves, matched by id
/// in the one list the server gives, so a rename on the server is followed and reported rather
/// than breaking the sync. A collection or skill that is gone, or no longer shared with the user,
/// contributes nothing and is reported; its entry stays so the user sees it in the next message
/// and can reset it with --reset.
async fn list_remote(
    api: &impl SkillsApi,
    dir: &Path,
    manifest: &SkillsManifest,
    warnings: &mut Vec<String>,
) -> Result<(Vec<Skill>, Option<Vec<Subscription>>)> {
    let all = api.list(None, None).await?;
    let Some(followed) = &manifest.subscriptions else {
        return Ok((all, None));
    };
    let collections: HashMap<String, String> =
        api.list_collections().await?.into_iter().map(|collection| (collection.id, collection.name)).collect();
    let skills: HashMap<&str, &str> = all.iter().map(|skill| (skill.id.as_str(), skill.name.as_str())).collect();
    let mut subscriptions = Vec::new();
    let mut wanted_collections = HashSet::new();
    let mut wanted_skills = HashSet::new();
    for subscription in followed {
        let current_name = match subscription.kind {
            SubscriptionKind::Skill => skills.get(subscription.id.as_str()).map(|name| name.to_string()),
            SubscriptionKind::Collection => collections.get(&subscription.id).cloned(),
        };
        let kind = subscription.kind.as_str();
        let Some(current_name) = current_name else {
            let what = if subscription.kind == SubscriptionKind::Skill { "it is" } else { "its skills are" };
            warnings.push(format!(
                "{}: {kind} \"{}\" is gone or no longer shared with you; {what} removed. Run \"gatana skills install --reset\" to reset what the directory follows",
                dir.display(),
                subscription.name
            ));
            subscriptions.push(subscription.clone());
            continue;
        };
        if current_name != subscription.name {
            warnings.push(format!(
                "{}: {kind} \"{}\" is now named \"{current_name}\"",
                dir.display(),
                subscription.name
            ));
        }
        subscriptions.push(Subscription { kind: subscription.kind, id: subscription.id.clone(), name: current_name });
        match subscription.kind {
            SubscriptionKind::Skill => wanted_skills.insert(subscription.id.clone()),
            SubscriptionKind::Collection => wanted_collections.insert(subscription.id.clone()),
        };
    }
    let remote = all
        .into_iter()
        .filter(|skill| {
            wanted_skills.contains(&skill.id)
                || skill.collection_id.as_ref().is_some_and(|collection| wanted_collections.contains(collection))
        })
        .collect();
    Ok((remote, Some(subscriptions)))
}

fn read_local_state(dir: &Path) -> Result<LocalState> {
    let mut state = LocalState::default();
    for entry in std::fs::read_dir(dir)? {
        let entry = entry?;
        let file_type = entry.file_type()?;
        if !file_type.is_dir() && !file_type.is_symlink() {
            continue;
        }
        let name = entry.file_name().to_string_lossy().into_owned();
        // A folder without a SKILL.md, or one we may not read: known as a folder, unknown as a skill.
        if let Ok(text) = std::fs::read_to_string(dir.join(&name).join(SKILL_FILE)) {
            state.hashes.insert(name.clone(), sha256(&text));
        }
        state.dirs.insert(name);
    }
    Ok(state)
}

/// Removes the SKILL.md and the folder when nothing else is in it. Never follows a symlink.
fn remove_skill_folder(dir: &Path, name: &str, warnings: &mut Vec<String>) -> Result<()> {
    let folder = dir.join(name);
    let Ok(metadata) = std::fs::symlink_metadata(&folder) else {
        return Ok(());
    };
    if metadata.file_type().is_symlink() {
        warnings.push(format!("{} is a symlink; left in place", folder.display()));
        return Ok(());
    }
    match std::fs::remove_file(folder.join(SKILL_FILE)) {
        Ok(()) => {}
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {}
        Err(error) => return Err(error.into()),
    }
    if std::fs::remove_dir(&folder).is_err() {
        warnings.push(format!("{} kept: it holds files the sync did not write", folder.display()));
    }
    Ok(())
}

pub async fn sync_directory(
    api: &impl SkillsApi,
    identity: &SkillsIdentity,
    dir: &Path,
    options: &SyncOptions,
) -> Result<SyncSummary> {
    std::fs::create_dir_all(dir)?;
    let mut warnings = Vec::new();

    let mut manifest = read_manifest(dir)?.unwrap_or_else(|| empty_manifest(&identity.org_id, &identity.base_url));
    if manifest.org_id != identity.org_id || manifest.base_url != identity.base_url {
        if !options.force {
            bail!(
                "{} is synced from {} ({}). Pass --force to switch it to {} ({}); the old folders stay and become foreign",
                dir.display(),
                manifest.org_id,
                manifest.base_url,
                identity.org_id,
                identity.base_url
            );
        }
        warnings.push(format!(
            "{}: switched from {} to {}; the earlier folders are no longer owned",
            dir.display(),
            manifest.org_id,
            identity.org_id
        ));
        manifest = empty_manifest(&identity.org_id, &identity.base_url);
    }

    // Subscription changes ride on the sync so a dry run previews them without writing anything:
    // the changed list only reaches the manifest through the write at the end.
    if options.reset {
        manifest.subscriptions = None;
    }
    if let Some(subscribe) = &options.subscribe {
        let current = manifest.subscriptions.get_or_insert_with(Vec::new);
        if !current.iter().any(|subscription| subscription.id == subscribe.id) {
            current.push(subscribe.clone());
        }
    }

    let (remote, subscriptions) = list_remote(api, dir, &manifest, &mut warnings).await?;
    let local = read_local_state(dir)?;
    let ops = compute_sync_plan(PlanInput {
        remote: &remote,
        manifest: &manifest.skills,
        local: &local,
        prune: options.prune,
        force: options.force,
    });

    for op in &ops {
        match (op.kind, op.reason) {
            (OpKind::Skip, Reason::ForeignFolder) => warnings.push(format!(
                "{} exists but was not created by this sync; skipped (use --force to take it over)",
                dir.join(&op.name).display()
            )),
            (OpKind::Skip, Reason::LocalEdits) => warnings.push(format!(
                "{} was edited locally; skipped (push it, or use --force to overwrite)",
                dir.join(&op.name).join(SKILL_FILE).display()
            )),
            _ => {}
        }
    }

    let count = |kind: OpKind| ops.iter().filter(|op| op.kind == kind).count();
    let summary = |total: usize, warnings: Vec<String>, ops: Vec<SyncOp>| SyncSummary {
        dir: dir.to_path_buf(),
        written: count(OpKind::Write),
        removed: count(OpKind::Remove),
        skipped: count(OpKind::Skip),
        total,
        subscriptions: subscriptions.clone(),
        warnings,
        ops: Some(ops),
    };

    if options.dry_run {
        return Ok(summary(manifest.skills.len(), warnings, ops.clone()));
    }

    for op in ops.iter().filter(|op| op.kind == OpKind::Remove) {
        remove_skill_folder(dir, &op.name, &mut warnings)?;
    }

    let mut next = SkillsManifest {
        synced_at: now_iso(),
        skills: Default::default(),
        subscriptions: subscriptions.clone(),
        ..manifest.clone()
    };
    for op in ops.iter().filter(|op| op.kind == OpKind::Skip && op.reason != Reason::ForeignFolder) {
        if let Some(entry) = manifest.skills.get(&op.id) {
            next.skills.insert(op.id.clone(), entry.clone());
        }
    }

    let writes: Vec<&SyncOp> = ops.iter().filter(|op| op.kind == OpKind::Write).collect();
    let results: Vec<(usize, Written)> = stream::iter(writes.iter().enumerate())
        .map(|(index, op)| async move { (index, write_skill(api, identity, dir, op).await) })
        .buffer_unordered(FETCH_CONCURRENCY)
        .collect()
        .await;
    let mut results = results;
    results.sort_by_key(|(index, _)| *index);
    for ((_, result), op) in results.into_iter().zip(&writes) {
        match result? {
            Some((id, entry)) => {
                next.skills.insert(id, entry);
            }
            None => {
                warnings.push(format!("{} disappeared between listing and reading; skipped", op.name));
                if let Some(entry) = manifest.skills.get(&op.id) {
                    next.skills.insert(op.id.clone(), entry.clone());
                }
            }
        }
    }

    write_manifest(dir, &next)?;
    Ok(summary(next.skills.len(), warnings, ops.clone()))
}

/// Fetches one skill and writes its folder. None when it disappeared since the listing.
async fn write_skill(api: &impl SkillsApi, identity: &SkillsIdentity, dir: &Path, op: &SyncOp) -> Written {
    let skill = match api.get(&op.id).await {
        Ok(skill) => skill,
        Err(error) if is_not_found(&error) => return Ok(None),
        Err(error) => return Err(error),
    };
    let text = render_skill_md(
        &frontmatter_for(Revision::from(&skill.skill), &identity.org_id, Map::new(), &Map::new()),
        &skill.content,
    );
    let folder = dir.join(&skill.skill.name);
    std::fs::create_dir_all(&folder)?;
    write_atomic(&folder.join(SKILL_FILE), &text)?;
    let updated_at = iso_millis(&skill.skill.updated_at).unwrap_or_else(|| skill.skill.updated_at.clone());
    Ok(Some((
        skill.skill.id.clone(),
        ManifestEntry { name: skill.skill.name.clone(), updated_at, hash: sha256(&text) },
    )))
}

/// What "gatana skills install" and the session-start hooks both run. A folder without a manifest
/// was never installed into and takes every skill the user can read: that is what the empty
/// manifest says, so a hook alone sets up a new machine, and the first prompt of the first session
/// already has the skills. What a folder follows is only ever narrowed by an install with a name.
pub async fn sync_targets(
    api: &impl SkillsApi,
    identity: &SkillsIdentity,
    dirs: &[PathBuf],
    options: &SyncOptions,
) -> Result<Vec<SyncSummary>> {
    let mut summaries = Vec::new();
    for dir in dirs {
        summaries.push(sync_directory(api, identity, dir, options).await?);
    }
    Ok(summaries)
}
