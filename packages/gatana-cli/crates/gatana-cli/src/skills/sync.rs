//! Installs the skills of an organization into a directory, and keeps them current.

use super::api::{ServerSkill, Skill, SkillsApi, SkillsError, is_not_found};
use super::frontmatter::is_valid_skill_name;
use super::manifest::{
    FileEntry, ManifestEntry, ServerSkillEntry, SkillsManifest, Subscription, SubscriptionKind, empty_manifest,
    read_manifest, server_skill_key, sha256, write_atomic, write_manifest,
};
use super::paths::{SKILL_FILE, check_paths};
use super::plan::{LocalState, OpKind, PlanInput, Reason, SyncOp, assign_server_folders, compute_sync_plan};
use crate::util::{iso_millis, now_iso};
use anyhow::{Result, bail};
use futures_util::{StreamExt, stream};
use indexmap::IndexMap;
use serde::Serialize;
use serde_json::Value;
use std::cell::RefCell;
use std::collections::{BTreeMap, HashMap, HashSet};
use std::path::{Path, PathBuf};

const FETCH_CONCURRENCY: usize = 4;

/// The manifest entry of a skill whose folder is current, and what to tell the user. Without an
/// entry, nothing was written and the reason is in the warnings.
type Written = Result<(Option<ManifestEntry>, Vec<String>)>;

/// Where the files of a skill come from.
enum Source<'a> {
    Registry {
        id: &'a str,
    },
    /// A connected server. `uris` holds the URI of each path. `rename` is the name of the skill and
    /// the name that the written SKILL.md gets, when the folder has the server slug in front.
    Server {
        slug: &'a str,
        uris: &'a HashMap<&'a str, &'a str>,
        rename: Option<(&'a str, &'a str)>,
        /// The servers that asked for credentials in this run.
        blocked: &'a RefCell<HashSet<String>>,
    },
}

/// What the run did for one planned skill. With no entry, the folder is as it was.
struct Done {
    /// The place of the skill in the plan.
    index: usize,
    skill: Option<ManifestEntry>,
    server_skill: Option<ServerSkillEntry>,
    warnings: Vec<String>,
    error: Option<String>,
}

/// A listed server skill that has a folder: what the sync needs to write it.
struct ServerPlan<'a> {
    skill: &'a ServerSkill,
    folder: String,
    /// Who has the folder of the plain name, when this skill has the prefix.
    name_owner: Option<String>,
    /// The files that a skill folder gets on every machine, by their path on disk.
    files: Vec<(String, &'a str, &'a str)>,
    /// The files that were left out, each with the reason.
    notes: Vec<String>,
}

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
    /// Skills that failed. The other skills of the run are written and recorded.
    pub errors: Vec<String>,
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
/// them: the skills of the followed collections and servers and the followed skills themselves,
/// matched by id in the lists the server gives, so a rename on the server is followed and reported
/// rather than breaking the sync. A collection, skill or server that is gone, or no longer shared
/// with the user, contributes nothing and is reported; its entry stays so the user sees it in the
/// next message and can reset it with --reset.
///
/// The server skills are None when their listing is not known: the backend has no such route, or
/// the request failed. A listing that is not known is not an empty listing, so the folders of
/// server skills then stay as they are.
async fn list_remote(
    api: &impl SkillsApi,
    dir: &Path,
    manifest: &SkillsManifest,
    warnings: &mut Vec<String>,
    errors: &mut Vec<String>,
) -> Result<(Vec<Skill>, Option<Vec<ServerSkill>>, Option<Vec<Subscription>>)> {
    let all = api.list(None, None).await?;
    let server_skills = match api.list_server_skills().await {
        Ok(listing) => listing,
        Err(error) => {
            errors.push(format!("{}: the skills of connected servers were not updated: {error:#}", dir.display()));
            None
        }
    };
    let Some(followed) = &manifest.subscriptions else {
        return Ok((all, server_skills, None));
    };
    let collections: HashMap<String, String> =
        api.list_collections().await?.into_iter().map(|collection| (collection.id, collection.name)).collect();
    let skills: HashMap<&str, &str> = all.iter().map(|skill| (skill.id.as_str(), skill.name.as_str())).collect();
    let mut subscriptions = Vec::new();
    let mut wanted_collections = HashSet::new();
    let mut wanted_skills = HashSet::new();
    let mut wanted_servers = HashSet::new();
    for subscription in followed {
        let current_name = match (subscription.kind, &server_skills) {
            (SubscriptionKind::Skill, _) => skills.get(subscription.id.as_str()).map(|name| name.to_string()),
            (SubscriptionKind::Collection, _) => collections.get(&subscription.id).cloned(),
            (SubscriptionKind::Server, Some(listing)) => {
                listing.iter().find(|skill| skill.server_id == subscription.id).map(|skill| skill.server_slug.clone())
            }
            (SubscriptionKind::Server, None) => {
                subscriptions.push(subscription.clone());
                continue;
            }
        };
        let kind = subscription.kind.as_str();
        let Some(current_name) = current_name else {
            let what = if subscription.kind == SubscriptionKind::Skill { "it is" } else { "its skills are" };
            let gone = if subscription.kind == SubscriptionKind::Server {
                "publishes no skills for you any more"
            } else {
                "is gone or no longer shared with you"
            };
            warnings.push(format!(
                "{}: {kind} \"{}\" {gone}; {what} removed. Run \"gatana skills install --reset\" to reset what the directory follows",
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
            SubscriptionKind::Server => wanted_servers.insert(subscription.id.clone()),
        };
    }
    let remote = all
        .into_iter()
        .filter(|skill| {
            wanted_skills.contains(&skill.id)
                || skill.collection_id.as_ref().is_some_and(|collection| wanted_collections.contains(collection))
        })
        .collect();
    let server_skills = server_skills
        .map(|listing| listing.into_iter().filter(|skill| wanted_servers.contains(&skill.server_id)).collect());
    Ok((remote, server_skills, Some(subscriptions)))
}

/// The path of a server file on disk. The listing gives it as the URI writes it, with percent
/// escapes. None for an escape that is not valid, that hides a `/`, or that gives bytes that are
/// not UTF-8.
fn decode_path(path: &str) -> Option<String> {
    let mut bytes = Vec::with_capacity(path.len());
    let mut rest = path;
    while let Some(index) = rest.find('%') {
        bytes.extend_from_slice(&rest.as_bytes()[..index]);
        let byte = u8::from_str_radix(rest.get(index + 1..index + 3)?, 16).ok()?;
        if byte == b'/' {
            return None;
        }
        bytes.push(byte);
        rest = &rest[index + 3..];
    }
    bytes.extend_from_slice(rest.as_bytes());
    String::from_utf8(bytes).ok()
}

/// A SKILL.md with another `name` in its frontmatter and every other byte as it was. None when
/// the frontmatter has no `name` line with the old name, or when the new text does not parse to
/// the new name.
fn rename_skill_md(content: &[u8], from: &str, to: &str) -> Option<Vec<u8>> {
    let text = std::str::from_utf8(content).ok()?;
    let mut offset = 0;
    let mut end_of_frontmatter = None;
    let mut name_at = None;
    for (index, line) in text.split_inclusive('\n').enumerate() {
        let bare = line.trim_end_matches(['\r', '\n']);
        if index == 0 {
            if bare != "---" {
                return None;
            }
        } else if bare == "---" {
            end_of_frontmatter = Some(offset);
            break;
        } else if name_at.is_none()
            && let Some(value) = bare.strip_prefix("name:")
        {
            name_at = Some(offset + "name:".len() + value.find(from)?);
        }
        offset += line.len();
    }
    let (end, at) = (end_of_frontmatter?, name_at?);
    let renamed = format!("{}{to}{}", &text[..at], &text[at + from.len()..]);
    let frontmatter = crate::yaml::load(&renamed[..end + to.len() - from.len()]).ok()?;
    (frontmatter.get("name").and_then(Value::as_str) == Some(to)).then(|| renamed.into_bytes())
}

fn read_local_state(dir: &Path, entries: &IndexMap<String, ManifestEntry>) -> Result<LocalState> {
    let mut state = LocalState::default();
    for entry in std::fs::read_dir(dir)? {
        let entry = entry?;
        let file_type = entry.file_type()?;
        if file_type.is_dir() || file_type.is_symlink() {
            state.dirs.insert(entry.file_name().to_string_lossy().into_owned());
        }
    }
    for entry in entries.values() {
        let folder = dir.join(&entry.name);
        // A file that is gone, or one we may not read, has no hash.
        let hashes = entry
            .files
            .keys()
            .filter_map(|path| Some((path.clone(), sha256(&std::fs::read(folder.join(path)).ok()?))))
            .collect();
        state.hashes.insert(entry.name.clone(), hashes);
    }
    Ok(state)
}

/// The first part of `<dir>/<name>/<path>` below `dir` that exists and is a symlink. A write or a
/// removal through it would land outside the skill folder.
fn symlink_on_the_way(dir: &Path, name: &str, path: &str) -> Option<PathBuf> {
    let mut current = dir.to_path_buf();
    for part in std::iter::once(name).chain(path.split('/')) {
        current.push(part);
        if std::fs::symlink_metadata(&current).is_ok_and(|metadata| metadata.file_type().is_symlink()) {
            return Some(current);
        }
    }
    None
}

/// Removes files of a skill folder, then each of their folders that is empty now. The skill folder
/// itself stays. Never follows a symlink.
fn remove_files<'a>(dir: &Path, name: &str, paths: impl Iterator<Item = &'a String>, warnings: &mut Vec<String>) {
    let folder = dir.join(name);
    let mut parents = HashSet::new();
    for path in paths {
        if let Some(link) = symlink_on_the_way(dir, name, path) {
            warnings.push(format!("{} is a symlink; {} left in place", link.display(), folder.join(path).display()));
            continue;
        }
        if let Err(error) = std::fs::remove_file(folder.join(path))
            && error.kind() != std::io::ErrorKind::NotFound
        {
            warnings.push(format!("{} not removed: {error}", folder.join(path).display()));
        }
        parents.extend(Path::new(path).ancestors().skip(1).filter(|parent| !parent.as_os_str().is_empty()));
    }
    // Deepest first. A folder with other content refuses and stays.
    let mut parents: Vec<&Path> = parents.into_iter().collect();
    parents.sort_by_key(|parent| std::cmp::Reverse(parent.components().count()));
    for parent in parents {
        let _ = std::fs::remove_dir(folder.join(parent));
    }
}

/// Removes the files that the sync wrote, and the folder when nothing else is in it.
fn remove_skill_folder(dir: &Path, entry: &ManifestEntry, warnings: &mut Vec<String>) {
    let folder = dir.join(&entry.name);
    let Ok(metadata) = std::fs::symlink_metadata(&folder) else {
        return;
    };
    if metadata.file_type().is_symlink() {
        warnings.push(format!("{} is a symlink; left in place", folder.display()));
        return;
    }
    remove_files(dir, &entry.name, entry.files.keys(), warnings);
    if std::fs::remove_dir(&folder).is_err() {
        warnings.push(format!("{} kept: it contains files that Gatana did not create", folder.display()));
    }
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
                "{} syncs skills from {} ({}).\nUse --force to switch to {} ({}).\nExisting skill folders will stay, but Gatana will stop tracking them. Skills with the same name in the new organization will overwrite the local SKILL.md files.",
                dir.display(),
                manifest.org_id,
                manifest.base_url,
                identity.org_id,
                identity.base_url
            );
        }
        warnings.push(format!(
            "{}: switched from {} to {}. Existing skill folders are no longer tracked unless the new organization has a skill with the same name",
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

    let mut errors = Vec::new();
    let (mut remote, server_skills, subscriptions) =
        list_remote(api, dir, &manifest, &mut warnings, &mut errors).await?;
    // The name becomes a folder name, so the rule of the backend is checked again here.
    remote.retain(|skill| {
        let valid = is_valid_skill_name(&skill.name);
        if !valid {
            warnings.push(format!("skill {:?} skipped: the name cannot be a folder name", skill.name));
        }
        valid
    });

    // The folders of the server skills that this run does not plan again stay where they are, by
    // folder with the server slug: every one without a listing, and with --no-prune the ones that
    // the listing no longer has.
    let listed: Option<HashSet<String>> = server_skills
        .as_ref()
        .map(|listing| listing.iter().map(|skill| server_skill_key(&skill.server_id, &skill.uri)).collect());
    let kept_server_folders: HashMap<&str, &str> = manifest
        .server_skills
        .iter()
        .filter(|(key, _)| listed.as_ref().is_none_or(|listed| !options.prune && !listed.contains(*key)))
        .map(|(_, entry)| (entry.name.as_str(), entry.server_slug.as_str()))
        .collect();
    // An organization skill has its folder before a server skill, also one that stays with
    // --no-prune. A kept server skill folder is taken for both.
    let organization = || "an organization skill".to_string();
    let mut taken: HashMap<String, String> = remote.iter().map(|skill| (skill.name.clone(), organization())).collect();
    if !options.prune {
        taken.extend(manifest.skills.values().map(|entry| (entry.name.clone(), organization())));
    }
    taken.extend(kept_server_folders.iter().map(|(folder, slug)| (folder.to_string(), format!("server \"{slug}\""))));
    let listing = server_skills.as_deref().unwrap_or_default();
    let mut folders = assign_server_folders(listing, taken, &mut warnings);
    let mut server_plans: HashMap<String, ServerPlan> = HashMap::new();
    for skill in listing {
        let key = server_skill_key(&skill.server_id, &skill.uri);
        let Some((folder, name_owner)) = folders.remove(&key) else {
            continue;
        };
        // A server is trusted less than the registry: every path goes through the path rules.
        let mut notes = Vec::new();
        let mut decoded = HashMap::new();
        for file in &skill.files {
            let unique = decode_path(&file.path).map(|path| decoded.insert(path, file));
            if !matches!(unique, Some(None)) {
                notes.push(format!(
                    "{}: file {:?} skipped: the path has an escape that cannot be a file name, or it is listed twice",
                    dir.join(&folder).display(),
                    file.path
                ));
            }
        }
        let (kept, skipped) = check_paths(decoded.keys().map(String::as_str));
        notes.extend(skipped.iter().map(|(path, reason)| {
            format!("{}: file {:?} skipped: {reason}", dir.join(&folder).display(), decoded[*path].path)
        }));
        let files =
            kept.iter().map(|path| (path.to_string(), decoded[*path].digest.as_str(), decoded[*path].uri.as_str()));
        let files = files.collect();
        server_plans.insert(key, ServerPlan { skill, folder, name_owner, files, notes });
    }

    // One plan for both kinds of skill, so that a folder can pass from one to the other in one run.
    // A server skill has no `updatedAt`: it changed when its listing is not what the manifest holds.
    let as_listed = |id: &str, name: &str, changed: bool| Skill {
        id: id.to_string(),
        name: name.to_string(),
        description: String::new(),
        updated_at: if changed { "changed".to_string() } else { String::new() },
        collection_id: None,
        collection_name: None,
        raw: Value::Null,
    };
    let mut entries = manifest.skills.clone();
    for (key, entry) in &manifest.server_skills {
        let files = entry.files.clone();
        entries.insert(key.clone(), ManifestEntry { name: entry.name.clone(), updated_at: String::new(), files });
        // Without a listing, the folder stays as it is.
        if server_skills.is_none() {
            remote.push(as_listed(key, &entry.name, false));
        }
    }
    for (key, plan) in &server_plans {
        let changed = manifest.server_skills.get(key).is_none_or(|entry| {
            entry.files.len() != plan.files.len()
                || plan.files.iter().any(|(path, digest, _)| {
                    entry.files.get(path).and_then(|file| file.digest.as_deref()) != Some(*digest)
                })
        });
        remote.push(as_listed(key, &plan.folder, changed));
    }
    // The order of a map changes from run to run.
    remote.sort_by(|a, b| a.name.cmp(&b.name));

    let local = read_local_state(dir, &entries)?;
    let reserved: HashSet<&str> = kept_server_folders.keys().copied().collect();
    let ops = compute_sync_plan(PlanInput {
        remote: &remote,
        manifest: &entries,
        local: &local,
        prune: options.prune,
        force: options.force,
        reserved: &reserved,
    });

    for op in &ops {
        match (op.kind, op.reason) {
            (OpKind::Skip, Reason::ForeignFolder) => warnings.push(format!(
                "{} is not tracked by Gatana. Skipped. Use --force to overwrite the files of the skill in it",
                dir.join(&op.name).display()
            )),
            (OpKind::Skip, Reason::FolderTaken) => warnings.push(format!(
                "skill \"{}\" skipped: server \"{}\" keeps the folder {} in this run, because {}",
                op.name,
                kept_server_folders.get(op.name.as_str()).copied().unwrap_or_default(),
                dir.join(&op.name).display(),
                if server_skills.is_none() {
                    "the skills of connected servers were not listed"
                } else {
                    "--no-prune keeps it"
                }
            )),
            (OpKind::Skip, Reason::LocalEdits) if manifest.server_skills.contains_key(&op.id) => warnings.push(format!(
                "{} has local edits. Skipped. Use --force to overwrite them",
                dir.join(&op.name).display()
            )),
            (OpKind::Skip, Reason::LocalEdits) => warnings.push(format!(
                "{} has local edits. Skipped. Push the changes with gatana skills push, or use --force to overwrite them",
                dir.join(&op.name).display()
            )),
            _ => {}
        }
    }

    let count = |kind: OpKind| ops.iter().filter(|op| op.kind == kind).count();
    // `refused` is the number of planned writes that wrote nothing.
    let summary =
        |total: usize, refused: usize, warnings: Vec<String>, errors: Vec<String>, ops: Vec<SyncOp>| SyncSummary {
            dir: dir.to_path_buf(),
            written: count(OpKind::Write) - refused,
            removed: count(OpKind::Remove),
            skipped: count(OpKind::Skip) + refused,
            total,
            subscriptions: subscriptions.clone(),
            warnings,
            errors,
            ops: Some(ops),
        };

    if options.dry_run {
        return Ok(summary(entries.len(), 0, warnings, errors, ops.clone()));
    }

    // The manifest on disk follows the run: it is written again after each folder that the run
    // removed or brought up to date. A run that is stopped in the middle, as a session-start hook
    // does after its time limit, then keeps the record of what it finished. Without it, the next
    // run would find folders that it does not own.
    let mut next = SkillsManifest { synced_at: now_iso(), subscriptions: subscriptions.clone(), ..manifest.clone() };
    for op in ops.iter().filter(|op| op.kind == OpKind::Remove) {
        if let Some(entry) = entries.get(&op.id) {
            remove_skill_folder(dir, entry, &mut warnings);
            next.skills.shift_remove(&op.id);
            next.server_skills.shift_remove(&op.id);
            write_manifest(dir, &next)?;
        }
    }

    // A manifest of CLI 5.2 or older knows only the SKILL.md of each skill. A sync after the upgrade
    // therefore also checks the file list of a skill that did not change, until a check succeeds.
    // A skill with local edits gets the check in a sync after the edits are gone.
    let is_checked = |op: &&SyncOp| {
        op.kind == OpKind::Write || (op.reason == Reason::Unchanged && manifest.files_unchecked.contains(&op.id))
    };
    let listed: HashMap<&str, &Skill> = remote.iter().map(|skill| (skill.id.as_str(), skill)).collect();
    let writes: Vec<&SyncOp> = ops.iter().filter(is_checked).collect();
    // The servers that asked for credentials in this run. No new read starts for them.
    let without_credentials: RefCell<HashSet<String>> = RefCell::new(HashSet::new());
    let (manifest_ref, listed_ref, plans_ref, blocked) = (&manifest, &listed, &server_plans, &without_credentials);
    // Organization skills and server skills, a few at a time. Each file of a server skill is one
    // connection from Gatana to the server.
    let mut results = stream::iter(writes.iter().enumerate())
        .map(|(index, op)| async move {
            let mut done = Done { index, skill: None, server_skill: None, warnings: Vec::new(), error: None };
            if let Some(skill) = listed_ref.get(op.id.as_str()).filter(|_| !plans_ref.contains_key(&op.id))
                && !manifest_ref.server_skills.contains_key(&op.id)
            {
                // The entry describes the folder only while the folder has the name of the skill.
                let known = manifest_ref.skills.get(&op.id).filter(|entry| entry.name == op.name);
                match write_skill(api, dir, skill, known, options.force).await {
                    Ok((entry, notes)) => (done.skill, done.warnings) = (entry, notes),
                    Err(error) => done.error = Some(format!("{}: {error:#}", dir.join(&op.name).display())),
                }
                return done;
            }
            // No plan: the listing is not known, so the folder stays as it is.
            let Some(plan) = plans_ref.get(&op.id) else {
                return done;
            };
            let (skill, slug) = (plan.skill, plan.skill.server_slug.as_str());
            let known = manifest_ref.server_skills.get(&op.id).filter(|entry| entry.name == plan.folder);
            let uris: HashMap<&str, &str> = plan.files.iter().map(|(path, _, uri)| (path.as_str(), *uri)).collect();
            let listing: Vec<(&str, &str)> =
                plan.files.iter().map(|(path, digest, _)| (path.as_str(), *digest)).collect();
            let rename = (plan.folder != skill.name).then_some((skill.name.as_str(), plan.folder.as_str()));
            let source = Source::Server { slug, uris: &uris, rename, blocked };
            let known_files = known.map(|entry| &entry.files);
            let files = match write_folder(api, dir, &plan.folder, &source, &listing, known_files, options.force).await
            {
                Ok((files, notes)) => {
                    done.warnings = notes;
                    files
                }
                Err(error) => {
                    match error.downcast_ref::<SkillsError>() {
                        // Once per server: its other skills would get the same answer.
                        Some(SkillsError::NeedsCredentials { message, authorize_url }) => {
                            if blocked.borrow_mut().insert(slug.to_string()) {
                                let link = authorize_url.as_deref().filter(|url| !message.contains(*url));
                                done.warnings.push(format!(
                                    "{message}{} The skills of server \"{slug}\" were skipped",
                                    link.map(|url| format!(" Authorize at {url} .")).unwrap_or_default()
                                ));
                            }
                        }
                        // Gatana could not read or verify the file. The server is at fault, not the sync.
                        Some(SkillsError::Api { status: 400, message }) => done
                            .warnings
                            .push(format!("skill \"{}\" of server \"{slug}\" skipped: {message}", skill.name)),
                        _ => done.error = Some(format!("{}: {error:#}", dir.join(&plan.folder).display())),
                    }
                    None
                }
            };
            let Some(files) = files else {
                return done;
            };
            done.warnings.extend(plan.notes.iter().cloned());
            if let Some(owner) = plan.name_owner.as_ref().filter(|_| known.is_none()) {
                done.warnings.push(format!(
                    "skill \"{}\" of server \"{slug}\" is in the folder {}: {owner} has the folder {}",
                    skill.name, plan.folder, skill.name
                ));
            }
            done.server_skill = Some(ServerSkillEntry {
                server_id: skill.server_id.clone(),
                server_slug: skill.server_slug.clone(),
                uri: skill.uri.clone(),
                name: plan.folder.clone(),
                files,
            });
            done
        })
        .buffer_unordered(FETCH_CONCURRENCY);

    let mut refused = 0;
    let mut reports = Vec::new();
    while let Some(done) = results.next().await {
        let op = writes[done.index];
        // A skill that failed, or that the run did not write, keeps the entry that it had.
        if done.skill.is_none() && done.server_skill.is_none() {
            refused += usize::from(op.kind == OpKind::Write);
        }
        // The folder is now in line with the file list of the skill.
        let checked = done.skill.is_some() && next.files_unchecked.remove(&op.id);
        let changed = checked
            || done.skill.as_ref().is_some_and(|entry| next.skills.get(&op.id) != Some(entry))
            || done.server_skill.as_ref().is_some_and(|entry| next.server_skills.get(&op.id) != Some(entry));
        if let Some(entry) = done.skill {
            next.skills.insert(op.id.clone(), entry);
        }
        if let Some(entry) = done.server_skill {
            next.server_skills.insert(op.id.clone(), entry);
        }
        if changed {
            write_manifest(dir, &next)?;
        }
        reports.push((done.index, done.warnings, done.error));
    }
    drop(results);
    // The skills finish in any order. The messages keep the order of the plan.
    reports.sort_by_key(|(index, _, _)| *index);
    for (_, notes, error) in reports {
        warnings.extend(notes);
        errors.extend(error);
    }

    next.files_unchecked.retain(|id| next.skills.contains_key(id));
    write_manifest(dir, &next)?;
    Ok(summary(next.skills.len() + next.server_skills.len(), refused, warnings, errors, ops.clone()))
}

/// Brings the folder of one organization skill in line with the server.
/// `known` is the manifest entry of the folder, if the sync owns it under this name.
async fn write_skill(
    api: &impl SkillsApi,
    dir: &Path,
    skill: &Skill,
    known: Option<&ManifestEntry>,
    force: bool,
) -> Written {
    let folder = dir.join(&skill.name);
    let updated_at = iso_millis(&skill.updated_at).unwrap_or_else(|| skill.updated_at.clone());
    let refused = |warning: String| Ok((None, vec![warning]));
    let gone = || refused(format!("{} disappeared between listing and reading; skipped", skill.name));

    let listing = match api.list_files(&skill.id).await {
        Ok(listing) => listing,
        Err(error) if is_not_found(&error) => return gone(),
        Err(error) => return Err(error),
    };
    let Some(listing) = listing else {
        // A server without file routes: the skill is its SKILL.md, as the server renders it.
        let hash = std::fs::read(folder.join(SKILL_FILE)).ok().map(|content| sha256(&content));
        let unchanged = known.filter(|entry| entry.updated_at == updated_at).and_then(|entry| {
            let file = entry.files.get(SKILL_FILE)?;
            (hash.as_ref() == Some(&file.hash)).then(|| entry.clone())
        });
        if unchanged.is_some() {
            return Ok((unchanged, Vec::new()));
        }
        if let Some(link) = symlink_on_the_way(dir, &skill.name, SKILL_FILE) {
            return refused(format!("{} is a symlink; {} skipped", link.display(), folder.display()));
        }
        let text = match api.get(&skill.id).await {
            Ok(skill) => skill.markdown,
            Err(error) if is_not_found(&error) => return gone(),
            Err(error) => return Err(error),
        };
        std::fs::create_dir_all(&folder)?;
        write_atomic(&folder.join(SKILL_FILE), text.as_bytes())?;
        let file = FileEntry { hash: sha256(text.as_bytes()), digest: None };
        let files = BTreeMap::from([(SKILL_FILE.to_string(), file)]);
        return Ok((Some(ManifestEntry { name: skill.name.clone(), updated_at, files }), Vec::new()));
    };

    let listing: Vec<(&str, &str)> = listing.iter().map(|file| (file.path.as_str(), file.digest.as_str())).collect();
    // A file without a digest is as new as the skill was when CLI 5.2 or older wrote it.
    let known_files = known.map(|entry| {
        let mut files = entry.files.clone();
        if entry.updated_at == updated_at {
            for (path, digest) in &listing {
                if let Some(file) = files.get_mut(*path).filter(|file| file.digest.is_none()) {
                    file.digest = Some(digest.to_string());
                }
            }
        }
        files
    });
    let source = Source::Registry { id: &skill.id };
    let (files, warnings) = write_folder(api, dir, &skill.name, &source, &listing, known_files.as_ref(), force).await?;
    Ok((files.map(|files| ManifestEntry { name: skill.name.clone(), updated_at, files }), warnings))
}

/// Brings one skill folder in line with a file listing: fetches the files whose digest is not the
/// one of the manifest, writes them, and removes the files that the listing no longer has.
/// `listing` holds each path with its digest. `known` holds the files of the manifest entry of the
/// folder. Answers the files of the folder as it is now. Without them, nothing was written and the
/// reason is in the warnings.
async fn write_folder(
    api: &impl SkillsApi,
    dir: &Path,
    name: &str,
    source: &Source<'_>,
    listing: &[(&str, &str)],
    known: Option<&BTreeMap<String, FileEntry>>,
    force: bool,
) -> Result<(Option<BTreeMap<String, FileEntry>>, Vec<String>)> {
    let folder = dir.join(name);
    let refused = |warning: String| Ok((None, vec![warning]));
    let gone = || refused(format!("{name} disappeared between listing and reading; skipped"));
    let hash_of = |path: &str| std::fs::read(folder.join(path)).ok().map(|content| sha256(&content));

    let digests: HashMap<&str, &str> = listing.iter().copied().collect();
    let (paths, skipped) = check_paths(digests.keys().copied());
    let mut warnings: Vec<String> =
        skipped.iter().map(|(path, reason)| format!("{}: file {path:?} skipped: {reason}", folder.display())).collect();
    if !paths.contains(&SKILL_FILE) {
        return refused(format!("{} skipped: the server lists no SKILL.md for it", folder.display()));
    }

    // Decide per file before anything changes on disk, so that a refusal leaves the folder whole.
    let mut files = BTreeMap::new();
    let mut fetch = Vec::new();
    // Files of the manifest that differ on disk, which the write replaces or removes. Without
    // --force, only a folder whose SKILL.md is gone gets here with such a file.
    let mut replaced = Vec::new();
    let skill_md_missing = hash_of(SKILL_FILE).is_none();
    for path in &paths {
        let digest = digests[path];
        if let Some(link) = symlink_on_the_way(dir, name, path) {
            return refused(format!("{} is a symlink; {} skipped", link.display(), folder.display()));
        }
        let local = hash_of(path);
        let known_file = known.and_then(|files| files.get(*path));
        if let (Some(file), Some(local)) = (known_file, &local)
            && *local != file.hash
        {
            replaced.push(path.to_string());
        }
        let current = match (known_file, &local) {
            (Some(file), Some(local)) => *local == file.hash && file.digest.as_deref() == Some(digest),
            // A file that the sync did not write. It stays when it is the file of the server.
            (None, Some(local)) if format!("sha256:{local}") != digest && !force => {
                return refused(format!(
                    "{} exists and Gatana did not write it. Skipped {}. {}use --force to overwrite the file",
                    folder.join(path).display(),
                    folder.display(),
                    match source {
                        Source::Registry { .. } => "Push the folder with gatana skills push, or ",
                        Source::Server { .. } => "Move the file, or ",
                    }
                ));
            }
            (None, Some(local)) => format!("sha256:{local}") == digest,
            (_, None) => false,
        };
        match local.filter(|_| current) {
            Some(hash) => {
                files.insert(path.to_string(), FileEntry { hash, digest: Some(digest.to_string()) });
            }
            None => fetch.push(*path),
        }
    }

    // Fetch everything before the first write: a failed request then leaves the folder as the
    // manifest describes it.
    let mut fetched = Vec::new();
    for path in fetch {
        let content = match source {
            Source::Registry { id } => match api.get_file(id, path).await {
                Ok(content) => content,
                Err(error) if is_not_found(&error) => return gone(),
                Err(error) => return Err(error),
            },
            Source::Server { slug, uris, blocked, .. } => {
                // Another skill of the server got the credentials prompt. The message is there.
                if blocked.borrow().contains(*slug) {
                    return Ok((None, warnings));
                }
                api.get_server_skill_file(slug, uris[path]).await?
            }
        };
        if format!("sha256:{}", sha256(&content)) != digests[path] {
            return refused(format!("{name} changed on the server during the sync; skipped"));
        }
        // The folder of a server skill can have the server slug in front. A host reads the folder
        // name as the name of the skill, so the SKILL.md gets that name.
        let content = match source {
            Source::Server { rename: Some((from, to)), .. } if path == SKILL_FILE => {
                match rename_skill_md(&content, from, to) {
                    Some(renamed) => renamed,
                    None => {
                        return refused(format!(
                            "{} skipped: the name in its SKILL.md cannot be changed to {to}",
                            folder.display()
                        ));
                    }
                }
            }
            _ => content,
        };
        files.insert(path.to_string(), FileEntry { hash: sha256(&content), digest: Some(digests[path].to_string()) });
        fetched.push((path, content));
    }

    if let Some(known) = known {
        let gone: Vec<&String> = known.keys().filter(|path| !files.contains_key(*path)).collect();
        let edited =
            gone.iter().filter(|path| hash_of(path.as_str()).is_some_and(|hash| hash != known[path.as_str()].hash));
        replaced.extend(edited.map(|path| path.to_string()));
        remove_files(dir, name, gone.into_iter(), &mut warnings);
    }
    for (path, content) in fetched {
        let target = folder.join(path);
        if let Some(link) = symlink_on_the_way(dir, name, path) {
            bail!("{} became a symlink during the sync; {} not written", link.display(), target.display());
        }
        if let Some(parent) = target.parent() {
            std::fs::create_dir_all(parent)?;
        }
        write_atomic(&target, &content)?;
    }
    // A replaced local edit is reported, so that a lost change can be traced to this run.
    if !force && !replaced.is_empty() {
        let cause =
            if skill_md_missing { ". The folder had no SKILL.md, so the sync wrote the skill again" } else { "" };
        warnings.push(format!(
            "{}: the sync replaced the local edits in {}{cause}",
            folder.display(),
            replaced.join(", ")
        ));
    }
    Ok((Some(files), warnings))
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
