//! What a sync does, decided from the remote list, the manifest and what is on disk. Pure, so the
//! cases are testable without a filesystem.

use super::api::{ServerSkill, Skill};
use super::frontmatter::is_valid_skill_name;
use super::manifest::{ManifestEntry, server_skill_key};
use super::paths::SKILL_FILE;
use crate::util::iso_millis;
use indexmap::IndexMap;
use serde::Serialize;
use std::collections::{HashMap, HashSet};

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum OpKind {
    Write,
    Remove,
    Skip,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum Reason {
    New,
    Changed,
    Renamed,
    MissingLocally,
    Pruned,
    Unchanged,
    ForeignFolder,
    LocalEdits,
    Kept,
    /// A server skill keeps the folder in this run.
    FolderTaken,
}

impl Reason {
    pub fn as_str(self) -> &'static str {
        match self {
            Reason::New => "new",
            Reason::Changed => "changed",
            Reason::Renamed => "renamed",
            Reason::MissingLocally => "missing-locally",
            Reason::Pruned => "pruned",
            Reason::Unchanged => "unchanged",
            Reason::ForeignFolder => "foreign-folder",
            Reason::LocalEdits => "local-edits",
            Reason::Kept => "kept",
            Reason::FolderTaken => "folder-taken",
        }
    }
}

#[derive(Clone, Debug, PartialEq, Serialize)]
pub struct SyncOp {
    pub kind: OpKind,
    pub id: String,
    pub name: String,
    pub reason: Reason,
}

impl SyncOp {
    fn new(kind: OpKind, id: &str, name: &str, reason: Reason) -> Self {
        Self { kind, id: id.to_string(), name: name.to_string(), reason }
    }
}

#[derive(Default)]
pub struct LocalState {
    /// Names of the folders in the directory, symlinks included.
    pub dirs: HashSet<String>,
    /// Per folder of the manifest: sha256 of each file that the manifest lists and the folder has,
    /// by its path.
    pub hashes: HashMap<String, HashMap<String, String>>,
}

pub struct PlanInput<'a> {
    pub remote: &'a [Skill],
    pub manifest: &'a IndexMap<String, ManifestEntry>,
    pub local: &'a LocalState,
    pub prune: bool,
    pub force: bool,
    /// The folders of the server skills that this run does not plan again: every one without a
    /// listing, and with prune off the ones that the listing no longer has. No other skill takes
    /// such a folder, also with force.
    pub reserved: &'a HashSet<&'a str>,
}

/// Removals must run before writes: a renamed skill frees its old folder and may take a name
/// another entry just freed.
pub fn compute_sync_plan(input: PlanInput) -> Vec<SyncOp> {
    let PlanInput { remote, manifest, local, prune, force, reserved } = input;
    let mut ops = Vec::new();
    let owned: HashSet<&str> = manifest.values().map(|entry| entry.name.as_str()).collect();
    // A folder we did not create, and no manifest entry is about to free it.
    let is_foreign = |name: &str| local.dirs.contains(name) && !owned.contains(name);
    let is_taken =
        |id: &str, name: &str| reserved.contains(name) && manifest.get(id).is_none_or(|entry| entry.name != name);
    // Where a new or renamed skill goes.
    let target = |id: &str, name: &str, reason: Reason| {
        if is_taken(id, name) {
            SyncOp::new(OpKind::Skip, id, name, Reason::FolderTaken)
        } else if is_foreign(name) && !force {
            SyncOp::new(OpKind::Skip, id, name, Reason::ForeignFolder)
        } else {
            SyncOp::new(OpKind::Write, id, name, reason)
        }
    };

    let mut remote_ids = HashSet::new();
    for skill in remote {
        remote_ids.insert(skill.id.as_str());
        let updated_at = iso_millis(&skill.updated_at).unwrap_or_else(|| skill.updated_at.clone());
        let Some(entry) = manifest.get(&skill.id) else {
            ops.push(target(&skill.id, &skill.name, Reason::New));
            continue;
        };

        if entry.name != skill.name {
            ops.push(SyncOp::new(OpKind::Remove, &skill.id, &entry.name, Reason::Renamed));
            ops.push(target(&skill.id, &skill.name, Reason::Renamed));
            continue;
        }

        let files = local.hashes.get(&skill.name).filter(|_| local.dirs.contains(&skill.name));
        let Some(files) = files.filter(|files| files.contains_key(SKILL_FILE)) else {
            ops.push(SyncOp::new(OpKind::Write, &skill.id, &skill.name, Reason::MissingLocally));
            continue;
        };
        // A local edit: a file of the manifest that changed or is gone. A file that the manifest
        // does not list is not the sync's file and does not count.
        if entry.files.iter().any(|(path, file)| files.get(path) != Some(&file.hash)) {
            let (kind, reason) =
                if force { (OpKind::Write, Reason::Changed) } else { (OpKind::Skip, Reason::LocalEdits) };
            ops.push(SyncOp::new(kind, &skill.id, &skill.name, reason));
            continue;
        }
        if entry.updated_at != updated_at {
            ops.push(SyncOp::new(OpKind::Write, &skill.id, &skill.name, Reason::Changed));
        } else {
            ops.push(SyncOp::new(OpKind::Skip, &skill.id, &skill.name, Reason::Unchanged));
        }
    }

    // Deleted, unshared, made private, or filtered out: no longer listed.
    for (id, entry) in manifest {
        if !remote_ids.contains(id.as_str()) {
            ops.push(if prune {
                SyncOp::new(OpKind::Remove, id, &entry.name, Reason::Pruned)
            } else {
                SyncOp::new(OpKind::Skip, id, &entry.name, Reason::Kept)
            });
        }
    }
    ops
}

/// The longest skill name that the backend and the agentskills.io specification accept.
const MAX_NAME_LENGTH: usize = 64;

/// The folder of each server skill, by its key in the manifest. A skill keeps its name. When a
/// folder in `taken` or a server with a lower slug has that folder, the skill gets
/// `<slug>-<name>`, and the second value says who has the plain name. Every machine then gets the
/// same folders. A skill with no free folder is left out and reported. `taken` holds the folders
/// of the organization skills and of the server skills that the run does not plan again, each with
/// who has it, for messages.
pub fn assign_server_folders(
    skills: &[ServerSkill],
    taken: HashMap<String, String>,
    warnings: &mut Vec<String>,
) -> HashMap<String, (String, Option<String>)> {
    let mut sorted: Vec<&ServerSkill> = skills.iter().collect();
    sorted.sort_by_key(|skill| (skill.server_slug.as_str(), skill.uri.as_str()));
    let mut owners = taken;
    let mut folders = HashMap::new();
    // Every plain name is given out before the first name with a prefix, so that a prefix never
    // takes the name of another skill.
    let mut losers = Vec::new();
    for skill in sorted {
        // The name comes from a server and becomes a folder name.
        if !is_valid_skill_name(&skill.name) || skill.name.len() > MAX_NAME_LENGTH {
            warnings.push(format!(
                "skill {:?} of server \"{}\" skipped: the name cannot be a folder name",
                skill.name, skill.server_slug
            ));
        } else if owners.contains_key(&skill.name) {
            losers.push(skill);
        } else {
            owners.insert(skill.name.clone(), format!("server \"{}\"", skill.server_slug));
            folders.insert(server_skill_key(&skill.server_id, &skill.uri), (skill.name.clone(), None));
        }
    }
    for skill in losers {
        let (name, slug) = (&skill.name, &skill.server_slug);
        let prefixed = format!("{slug}-{name}");
        let owner = owners[name].clone();
        if !is_valid_skill_name(&prefixed) || prefixed.len() > MAX_NAME_LENGTH {
            warnings.push(format!(
                "skill \"{name}\" of server \"{slug}\" skipped: {owner} has the folder {name}, and \"{prefixed}\" cannot be a skill name"
            ));
        } else if let Some(other) = owners.get(&prefixed) {
            warnings.push(format!(
                "skill \"{name}\" of server \"{slug}\" skipped: {owner} has the folder {name}, and {other} has the folder {prefixed}"
            ));
        } else {
            owners.insert(prefixed.clone(), format!("server \"{slug}\""));
            folders.insert(server_skill_key(&skill.server_id, &skill.uri), (prefixed, Some(owner)));
        }
    }
    folders
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::skills::manifest::FileEntry;
    use serde_json::Value;

    const T1: &str = "2026-09-10T08:00:00.000Z";
    const T2: &str = "2026-09-10T09:00:00.000Z";

    fn remote(id: &str, name: &str, updated_at: &str) -> Skill {
        Skill {
            id: id.into(),
            name: name.into(),
            description: String::new(),
            updated_at: updated_at.into(),
            collection_id: None,
            collection_name: None,
            raw: Value::Null,
        }
    }

    /// Folders with the hash of their SKILL.md, or None for a folder without one.
    fn local(entries: &[(&str, Option<&str>)]) -> LocalState {
        LocalState {
            dirs: entries.iter().map(|(name, _)| name.to_string()).collect(),
            hashes: entries
                .iter()
                .filter_map(|(name, hash)| {
                    hash.map(|hash| (name.to_string(), HashMap::from([(SKILL_FILE.to_string(), hash.to_string())])))
                })
                .collect(),
        }
    }

    fn entry(name: &str) -> ManifestEntry {
        let file = FileEntry { hash: "h".into(), digest: None };
        ManifestEntry { name: name.into(), updated_at: T1.into(), files: [(SKILL_FILE.to_string(), file)].into() }
    }

    fn manifest(entries: &[(&str, &str)]) -> IndexMap<String, ManifestEntry> {
        entries.iter().map(|(id, name)| (id.to_string(), entry(name))).collect()
    }

    fn brief(
        remote: &[Skill],
        manifest: &IndexMap<String, ManifestEntry>,
        local: &LocalState,
        prune: bool,
        force: bool,
    ) -> Vec<String> {
        compute_sync_plan(PlanInput { remote, manifest, local, prune, force, reserved: &HashSet::new() })
            .iter()
            .map(|op| {
                format!(
                    "{}:{}:{}",
                    serde_json::to_value(op.kind).unwrap().as_str().unwrap(),
                    op.name,
                    op.reason.as_str()
                )
            })
            .collect()
    }

    #[test]
    fn new_skill_is_written_a_foreign_folder_of_the_same_name_is_skipped_unless_forced() {
        let empty = IndexMap::new();
        assert_eq!(brief(&[remote("1", "a", T1)], &empty, &local(&[]), true, false), ["write:a:new"]);
        let occupied = local(&[("a", Some("x"))]);
        assert_eq!(brief(&[remote("1", "a", T1)], &empty, &occupied, true, false), ["skip:a:foreign-folder"]);
        assert_eq!(brief(&[remote("1", "a", T1)], &empty, &occupied, true, true), ["write:a:new"]);
    }

    #[test]
    fn unchanged_changed_and_missing_locally() {
        let manifest = manifest(&[("1", "a")]);
        let present = local(&[("a", Some("h"))]);
        assert_eq!(brief(&[remote("1", "a", T1)], &manifest, &present, true, false), ["skip:a:unchanged"]);
        assert_eq!(brief(&[remote("1", "a", T2)], &manifest, &present, true, false), ["write:a:changed"]);
        assert_eq!(brief(&[remote("1", "a", T1)], &manifest, &local(&[]), true, false), ["write:a:missing-locally"]);
        // Folder present but SKILL.md gone counts as missing.
        assert_eq!(
            brief(&[remote("1", "a", T1)], &manifest, &local(&[("a", None)]), true, false),
            ["write:a:missing-locally"]
        );
    }

    #[test]
    fn local_edits_are_never_overwritten_without_force() {
        let manifest = manifest(&[("1", "a")]);
        let edited = local(&[("a", Some("different"))]);
        assert_eq!(brief(&[remote("1", "a", T2)], &manifest, &edited, true, false), ["skip:a:local-edits"]);
        assert_eq!(brief(&[remote("1", "a", T1)], &manifest, &edited, true, true), ["write:a:changed"]);
    }

    #[test]
    fn a_changed_or_missing_supporting_file_is_a_local_edit_and_an_extra_file_is_not() {
        let mut manifest = manifest(&[("1", "a")]);
        manifest["1"].files.insert("docs/guide.md".into(), FileEntry { hash: "g".into(), digest: None });
        let with = |files: &[(&str, &str)]| LocalState {
            dirs: ["a".to_string()].into(),
            hashes: [(
                "a".to_string(),
                files.iter().map(|(path, hash)| (path.to_string(), hash.to_string())).collect(),
            )]
            .into(),
        };
        let plan = |local: &LocalState| brief(&[remote("1", "a", T2)], &manifest, local, true, false);
        assert_eq!(plan(&with(&[(SKILL_FILE, "h"), ("docs/guide.md", "g")])), ["write:a:changed"]);
        assert_eq!(plan(&with(&[(SKILL_FILE, "h"), ("docs/guide.md", "edited")])), ["skip:a:local-edits"]);
        assert_eq!(plan(&with(&[(SKILL_FILE, "h")])), ["skip:a:local-edits"]);
        // The local state holds only the files of the manifest, so an extra file never reaches the plan.
        assert_eq!(plan(&with(&[("docs/guide.md", "g")])), ["write:a:missing-locally"]);
    }

    #[test]
    fn rename_removes_the_old_folder_then_writes_the_new_one_and_swapped_names_work() {
        let single = manifest(&[("1", "a")]);
        assert_eq!(
            brief(&[remote("1", "b", T2)], &single, &local(&[("a", Some("h"))]), true, false),
            ["remove:a:renamed", "write:b:renamed"]
        );
        let swap = manifest(&[("1", "a"), ("2", "b")]);
        assert_eq!(
            brief(
                &[remote("1", "b", T2), remote("2", "a", T2)],
                &swap,
                &local(&[("a", Some("h")), ("b", Some("h"))]),
                true,
                false
            ),
            ["remove:a:renamed", "write:b:renamed", "remove:b:renamed", "write:a:renamed"]
        );
    }

    #[test]
    fn rename_onto_a_foreign_folder_is_skipped() {
        assert_eq!(
            brief(
                &[remote("1", "b", T1)],
                &manifest(&[("1", "a")]),
                &local(&[("a", Some("h")), ("b", Some("x"))]),
                true,
                false
            ),
            ["remove:a:renamed", "skip:b:foreign-folder"]
        );
    }

    #[test]
    fn a_folder_that_a_server_skill_keeps_is_taken_by_no_new_or_renamed_skill_also_with_force() {
        let reserved = HashSet::from(["deploy"]);
        let manifest = manifest(&[("srvr_a skill://deploy/SKILL.md", "deploy"), ("1", "old")]);
        let local = local(&[("deploy", Some("h")), ("old", Some("h"))]);
        for force in [false, true] {
            let ops = compute_sync_plan(PlanInput {
                remote: &[remote("2", "deploy", T1), remote("1", "deploy", T2)],
                manifest: &manifest,
                local: &local,
                prune: false,
                force,
                reserved: &reserved,
            });
            let ops: Vec<(OpKind, &str, Reason)> =
                ops.iter().map(|op| (op.kind, op.name.as_str(), op.reason)).collect();
            assert_eq!(
                ops,
                [
                    (OpKind::Skip, "deploy", Reason::FolderTaken),
                    (OpKind::Remove, "old", Reason::Renamed),
                    (OpKind::Skip, "deploy", Reason::FolderTaken),
                    (OpKind::Skip, "deploy", Reason::Kept),
                ]
            );
        }
    }

    #[test]
    fn an_organization_skill_then_the_lower_slug_gets_the_folder_and_the_others_get_the_prefix() {
        let skill = |slug: &str, path: &str, name: &str| ServerSkill {
            server_id: format!("id-{slug}"),
            server_slug: slug.into(),
            uri: format!("skill://{path}/SKILL.md"),
            name: name.into(),
            files: Vec::new(),
        };
        let folder = |folders: &HashMap<String, (String, Option<String>)>, slug: &str, path: &str| {
            folders.get(&format!("id-{slug} skill://{path}/SKILL.md")).map(|(folder, _)| folder.clone())
        };
        // The order of the listing does not count.
        let skills = [
            skill("zeta", "deploy", "deploy"),
            skill("alpha", "deploy", "deploy"),
            skill("alpha", "team/deploy", "deploy"),
            skill("alpha", "review", "review"),
            skill("alpha", "Bad Name", "Bad Name"),
            // The plain name of this skill is the name with a prefix of another one.
            skill("beta", "zeta-deploy", "zeta-deploy"),
            skill("beta", "lint", "lint"),
        ];
        let mut warnings = Vec::new();
        let taken = HashMap::from([
            ("review".to_string(), "an organization skill".to_string()),
            ("lint".to_string(), "server \"old\"".to_string()),
        ]);
        let folders = assign_server_folders(&skills, taken, &mut warnings);
        assert_eq!(folder(&folders, "alpha", "deploy").as_deref(), Some("deploy"));
        assert_eq!(folder(&folders, "alpha", "review").as_deref(), Some("alpha-review"));
        assert_eq!(folders["id-alpha skill://review/SKILL.md"].1.as_deref(), Some("an organization skill"));
        // A folder that a server skill keeps in this run counts as taken.
        assert_eq!(folder(&folders, "beta", "lint").as_deref(), Some("beta-lint"));
        assert_eq!(folders["id-beta skill://lint/SKILL.md"].1.as_deref(), Some("server \"old\""));
        assert_eq!(folder(&folders, "alpha", "team/deploy").as_deref(), Some("alpha-deploy"));
        assert_eq!(folder(&folders, "beta", "zeta-deploy").as_deref(), Some("zeta-deploy"));
        // Both folders are taken: the skill and the two owners are named.
        assert_eq!(folder(&folders, "zeta", "deploy"), None);
        assert_eq!(folder(&folders, "alpha", "Bad Name"), None);
        assert_eq!(warnings.len(), 2);
        assert!(warnings[0].contains("\"Bad Name\" of server \"alpha\""));
        assert!(warnings[1].contains(
            "skill \"deploy\" of server \"zeta\" skipped: server \"alpha\" has the folder deploy, and server \"beta\" has the folder zeta-deploy"
        ));
    }

    #[test]
    fn a_skill_no_longer_listed_is_pruned_or_kept_with_prune_off() {
        let manifest = manifest(&[("1", "a")]);
        let present = local(&[("a", Some("h"))]);
        assert_eq!(brief(&[], &manifest, &present, true, false), ["remove:a:pruned"]);
        assert_eq!(brief(&[], &manifest, &present, false, false), ["skip:a:kept"]);
    }
}
