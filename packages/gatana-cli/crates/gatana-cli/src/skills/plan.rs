//! What a sync does, decided from the remote list, the manifest and what is on disk. Pure, so the
//! cases are testable without a filesystem.

use super::api::Skill;
use super::manifest::ManifestEntry;
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
    /// sha256 of `<folder>/SKILL.md` for the folders that have one.
    pub hashes: HashMap<String, String>,
}

pub struct PlanInput<'a> {
    pub remote: &'a [Skill],
    pub manifest: &'a IndexMap<String, ManifestEntry>,
    pub local: &'a LocalState,
    pub prune: bool,
    pub force: bool,
}

/// Removals must run before writes: a renamed skill frees its old folder and may take a name
/// another entry just freed.
pub fn compute_sync_plan(input: PlanInput) -> Vec<SyncOp> {
    let PlanInput { remote, manifest, local, prune, force } = input;
    let mut ops = Vec::new();
    let owned: HashSet<&str> = manifest.values().map(|entry| entry.name.as_str()).collect();
    // A folder we did not create, and no manifest entry is about to free it.
    let is_foreign = |name: &str| local.dirs.contains(name) && !owned.contains(name);

    let mut remote_ids = HashSet::new();
    for skill in remote {
        remote_ids.insert(skill.id.as_str());
        let updated_at = iso_millis(&skill.updated_at).unwrap_or_else(|| skill.updated_at.clone());
        let Some(entry) = manifest.get(&skill.id) else {
            if is_foreign(&skill.name) && !force {
                ops.push(SyncOp::new(OpKind::Skip, &skill.id, &skill.name, Reason::ForeignFolder));
            } else {
                ops.push(SyncOp::new(OpKind::Write, &skill.id, &skill.name, Reason::New));
            }
            continue;
        };

        if entry.name != skill.name {
            ops.push(SyncOp::new(OpKind::Remove, &skill.id, &entry.name, Reason::Renamed));
            if is_foreign(&skill.name) && !force {
                ops.push(SyncOp::new(OpKind::Skip, &skill.id, &skill.name, Reason::ForeignFolder));
            } else {
                ops.push(SyncOp::new(OpKind::Write, &skill.id, &skill.name, Reason::Renamed));
            }
            continue;
        }

        let Some(local_hash) = local.hashes.get(&skill.name).filter(|_| local.dirs.contains(&skill.name)) else {
            ops.push(SyncOp::new(OpKind::Write, &skill.id, &skill.name, Reason::MissingLocally));
            continue;
        };
        if *local_hash != entry.hash {
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

#[cfg(test)]
mod tests {
    use super::*;
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

    fn local(entries: &[(&str, Option<&str>)]) -> LocalState {
        LocalState {
            dirs: entries.iter().map(|(name, _)| name.to_string()).collect(),
            hashes: entries
                .iter()
                .filter_map(|(name, hash)| hash.map(|hash| (name.to_string(), hash.to_string())))
                .collect(),
        }
    }

    fn entry(name: &str) -> ManifestEntry {
        ManifestEntry { name: name.into(), updated_at: T1.into(), hash: "h".into() }
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
        compute_sync_plan(PlanInput { remote, manifest, local, prune, force })
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
    fn a_skill_no_longer_listed_is_pruned_or_kept_with_prune_off() {
        let manifest = manifest(&[("1", "a")]);
        let present = local(&[("a", Some("h"))]);
        assert_eq!(brief(&[], &manifest, &present, true, false), ["remove:a:pruned"]);
        assert_eq!(brief(&[], &manifest, &present, false, false), ["skip:a:kept"]);
    }
}
