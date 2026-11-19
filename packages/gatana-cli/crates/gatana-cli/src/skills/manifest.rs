//! `.gatana-skills.json` sits in every synced directory and records which skill folders the sync
//! owns, and which collections, skills and servers the directory follows. Everything not in it is somebody
//! else's and is never touched. One directory serves one organization.

use super::paths::SKILL_FILE;
use indexmap::IndexMap;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;

pub const MANIFEST_FILE: &str = ".gatana-skills.json";

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct FileEntry {
    /// sha256 of the file as written, to notice local edits before overwriting them.
    pub hash: String,
    /// The digest in the file list of the server that the file was last compared with, to fetch only
    /// what changed. None for a file that CLI 5.2 or older wrote, or that came from a server without
    /// file routes: such a file is current while `updatedAt` of the skill is.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub digest: Option<String>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct ManifestEntry {
    /// The folder of the skill.
    pub name: String,
    #[serde(rename = "updatedAt")]
    pub updated_at: String,
    /// Every file the sync wrote into the folder, by its path with `/`, `SKILL.md` included.
    pub files: BTreeMap<String, FileEntry>,
}

/// A skill of a connected MCP server. Its key in the manifest is the server ID, a space and the URI
/// of its SKILL.md as the server publishes it: the name is not an identity, because two servers
/// can publish one name.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct ServerSkillEntry {
    #[serde(rename = "serverId")]
    pub server_id: String,
    /// The slug as last seen, for messages.
    #[serde(rename = "serverSlug")]
    pub server_slug: String,
    pub uri: String,
    /// The folder of the skill: its name, or `<slug>-<name>` when another skill has that folder.
    pub name: String,
    /// As for an organization skill. `digest` is the digest in the listing of the server. `hash`
    /// differs from it for a SKILL.md whose name the sync rewrote.
    pub files: BTreeMap<String, FileEntry>,
}

pub fn server_skill_key(server_id: &str, uri: &str) -> String {
    format!("{server_id} {uri}")
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize, Default)]
#[serde(rename_all = "lowercase")]
pub enum SubscriptionKind {
    /// Manifests written before skills could be followed carry no kind: they followed collections.
    #[default]
    Collection,
    Skill,
    /// Every skill of one connected MCP server. The id is the server ID and the name is the slug.
    Server,
}

impl SubscriptionKind {
    pub fn as_str(self) -> &'static str {
        match self {
            SubscriptionKind::Collection => "collection",
            SubscriptionKind::Skill => "skill",
            SubscriptionKind::Server => "server",
        }
    }
}

/// A collection, a single skill or a server the directory follows. The id is what is followed; the
/// name is what was last seen, for messages.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Subscription {
    #[serde(default)]
    pub kind: SubscriptionKind,
    pub id: String,
    pub name: String,
}

/// Version 3. `subscriptions` null means the directory takes every skill the user can read; a
/// list, even an empty one, means only the skills of those collections and servers and the skills
/// themselves.
/// The distinction matters when the list is empty: the directory must not flip to everything on
/// its own.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct SkillsManifest {
    pub version: u8,
    #[serde(rename = "orgId")]
    pub org_id: String,
    #[serde(rename = "baseUrl")]
    pub base_url: String,
    #[serde(rename = "syncedAt")]
    pub synced_at: String,
    pub skills: IndexMap<String, ManifestEntry>,
    /// The skills of connected servers, by `server_skill_key`. Not in the file when empty, so a
    /// directory without server skills has the file that a CLI without them wrote.
    #[serde(default, rename = "serverSkills", skip_serializing_if = "IndexMap::is_empty")]
    pub server_skills: IndexMap<String, ServerSkillEntry>,
    pub subscriptions: Option<Vec<Subscription>>,
    /// The skills whose file list a sync has not checked since a version 1 or 2 file, which CLI 5.2
    /// or older wrote. Those versions synced only the SKILL.md. A skill leaves the set when a sync
    /// or a push has brought its folder in line with the file list. A skill that has local edits, or
    /// whose check failed, stays for the next sync. Not in the file when empty.
    #[serde(default, rename = "filesUnchecked", skip_serializing_if = "BTreeSet::is_empty")]
    pub files_unchecked: BTreeSet<String>,
}

/// Versions 1 and 2: one hash per skill, of its SKILL.md. Version 1 has no subscriptions.
#[derive(Deserialize)]
struct OldManifest {
    #[serde(rename = "orgId")]
    org_id: String,
    #[serde(rename = "baseUrl")]
    base_url: String,
    #[serde(rename = "syncedAt")]
    synced_at: String,
    skills: IndexMap<String, OldEntry>,
    subscriptions: Option<Vec<Subscription>>,
}

#[derive(Deserialize)]
struct OldEntry {
    name: String,
    #[serde(rename = "updatedAt")]
    updated_at: String,
    hash: String,
}

#[derive(Debug, thiserror::Error)]
#[error("{0}")]
pub struct ManifestError(pub String);

pub fn empty_manifest(org_id: &str, base_url: &str) -> SkillsManifest {
    SkillsManifest {
        version: 3,
        org_id: org_id.to_string(),
        base_url: base_url.to_string(),
        synced_at: "1970-01-01T00:00:00.000Z".to_string(),
        skills: IndexMap::new(),
        server_skills: IndexMap::new(),
        subscriptions: None,
        files_unchecked: BTreeSet::new(),
    }
}

/// Missing file: None. A version 1 or 2 file reads as version 3: its one hash per skill is the hash
/// of the SKILL.md, and version 1 has no subscriptions. Unreadable
/// content: an error, on purpose. Treating a broken manifest as empty would make every owned folder
/// foreign, or with --force deletable.
pub fn read_manifest(dir: &Path) -> anyhow::Result<Option<SkillsManifest>> {
    let path = dir.join(MANIFEST_FILE);
    let text = match std::fs::read_to_string(&path) {
        Ok(text) => text,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(None),
        Err(error) => return Err(anyhow::Error::new(error).context(format!("reading {}", path.display()))),
    };
    let shape_error = || {
        ManifestError(format!(
            "{} has an invalid format or unsupported version. Fix or delete it, then sync again",
            path.display()
        ))
    };
    let value: Value = serde_json::from_str(&text).map_err(|_| {
        ManifestError(format!("{} is not valid JSON. Fix or delete it, then sync again", path.display()))
    })?;
    match value.get("version").and_then(Value::as_u64) {
        Some(3) => serde_json::from_value(value).map(Some).map_err(|_| shape_error().into()),
        Some(version @ (1 | 2)) => {
            let old: OldManifest = serde_json::from_value(value).map_err(|_| shape_error())?;
            let skills: IndexMap<String, ManifestEntry> = old
                .skills
                .into_iter()
                .map(|(id, entry)| {
                    let file = FileEntry { hash: entry.hash, digest: None };
                    let files = BTreeMap::from([(SKILL_FILE.to_string(), file)]);
                    (id, ManifestEntry { name: entry.name, updated_at: entry.updated_at, files })
                })
                .collect();
            Ok(Some(SkillsManifest {
                version: 3,
                org_id: old.org_id,
                base_url: old.base_url,
                synced_at: old.synced_at,
                files_unchecked: skills.keys().cloned().collect(),
                skills,
                server_skills: IndexMap::new(),
                subscriptions: old.subscriptions.filter(|_| version == 2),
            }))
        }
        _ => Err(shape_error().into()),
    }
}

pub fn write_manifest(dir: &Path, manifest: &SkillsManifest) -> anyhow::Result<()> {
    std::fs::create_dir_all(dir)?;
    let text = format!("{}\n", serde_json::to_string_pretty(manifest)?);
    write_atomic(&dir.join(MANIFEST_FILE), text.as_bytes())
}

/// Writes next to the target and renames over it, so a reader never sees half a file.
pub fn write_atomic(path: &Path, content: &[u8]) -> anyhow::Result<()> {
    let mut tmp = path.as_os_str().to_owned();
    tmp.push(format!(".{}.tmp", std::process::id()));
    std::fs::write(&tmp, content)?;
    std::fs::rename(&tmp, path)?;
    Ok(())
}

pub fn sha256(content: &[u8]) -> String {
    let digest = Sha256::digest(content);
    digest.iter().map(|byte| format!("{byte:02x}")).collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn missing_reads_as_none_written_reads_back_and_no_temp_file_remains() {
        let dir = tempfile::tempdir().unwrap();
        assert!(read_manifest(dir.path()).unwrap().is_none());
        let mut manifest = empty_manifest("acme", "https://acme.example");
        let files = BTreeMap::from([
            ("SKILL.md".to_string(), FileEntry { hash: "y".into(), digest: Some("sha256:y".into()) }),
            ("docs/a.md".to_string(), FileEntry { hash: "z".into(), digest: None }),
        ]);
        manifest.skills.insert("s1".into(), ManifestEntry { name: "a".into(), updated_at: "x".into(), files });
        write_manifest(dir.path(), &manifest).unwrap();
        assert_eq!(read_manifest(dir.path()).unwrap(), Some(manifest));
        let names: Vec<_> = std::fs::read_dir(dir.path()).unwrap().map(|entry| entry.unwrap().file_name()).collect();
        assert_eq!(names, vec![MANIFEST_FILE]);
    }

    #[test]
    fn corrupt_or_misshapen_manifests_are_errors_not_empty_manifests() {
        let dir = tempfile::tempdir().unwrap();
        std::fs::write(dir.path().join(MANIFEST_FILE), "{not json").unwrap();
        assert!(read_manifest(dir.path()).unwrap_err().downcast_ref::<ManifestError>().is_some());
        for text in [r#"{"version":2,"skills":{}}"#, r#"{"version":3,"skills":{}}"#, r#"{"version":4}"#] {
            std::fs::write(dir.path().join(MANIFEST_FILE), text).unwrap();
            assert!(read_manifest(dir.path()).unwrap_err().downcast_ref::<ManifestError>().is_some());
        }
    }

    #[test]
    fn version_1_and_2_manifests_read_as_version_3_with_the_one_hash_as_the_hash_of_the_skill_md() {
        let dir = tempfile::tempdir().unwrap();
        std::fs::write(
            dir.path().join(MANIFEST_FILE),
            r#"{"version":1,"orgId":"acme","baseUrl":"https://acme.example","syncedAt":"x","skills":{}}"#,
        )
        .unwrap();
        let manifest = read_manifest(dir.path()).unwrap().unwrap();
        assert_eq!(manifest.version, 3);
        assert_eq!(manifest.subscriptions, None);
        assert!(manifest.files_unchecked.is_empty());

        std::fs::write(
            dir.path().join(MANIFEST_FILE),
            r#"{"version":2,"orgId":"acme","baseUrl":"https://acme.example","syncedAt":"x","skills":{"s1":{"name":"a","updatedAt":"t","hash":"h"}},"subscriptions":[]}"#,
        )
        .unwrap();
        let manifest = read_manifest(dir.path()).unwrap().unwrap();
        assert_eq!(manifest.version, 3);
        assert_eq!(manifest.subscriptions, Some(Vec::new()));
        assert_eq!(manifest.files_unchecked, BTreeSet::from(["s1".to_string()]));
        let text = serde_json::to_string(&manifest).unwrap();
        assert!(text.contains(r#""filesUnchecked":["s1"]"#));
        assert_eq!(serde_json::from_str::<SkillsManifest>(&text).unwrap(), manifest);
        let files = BTreeMap::from([("SKILL.md".to_string(), FileEntry { hash: "h".into(), digest: None })]);
        assert_eq!(manifest.skills["s1"], ManifestEntry { name: "a".into(), updated_at: "t".into(), files });
    }

    #[test]
    fn a_server_skill_and_a_followed_server_are_additions_to_version_3() {
        let dir = tempfile::tempdir().unwrap();
        // The file of a CLI without server skills reads as before.
        std::fs::write(
            dir.path().join(MANIFEST_FILE),
            r#"{"version":3,"orgId":"acme","baseUrl":"https://acme.example","syncedAt":"x","skills":{},"subscriptions":null}"#,
        )
        .unwrap();
        let mut manifest = read_manifest(dir.path()).unwrap().unwrap();
        assert!(manifest.server_skills.is_empty());
        // And without server skills the file has no new field.
        assert!(!serde_json::to_string(&manifest).unwrap().contains("serverSkills"));

        let files = BTreeMap::from([(
            "SKILL.md".to_string(),
            FileEntry { hash: "written".into(), digest: Some("sha256:listed".into()) },
        )]);
        let entry = ServerSkillEntry {
            server_id: "srvr_1".into(),
            server_slug: "github".into(),
            uri: "skill://git-workflow/SKILL.md".into(),
            name: "github-git-workflow".into(),
            files,
        };
        manifest.server_skills.insert(server_skill_key(&entry.server_id, &entry.uri), entry);
        manifest.subscriptions =
            Some(vec![Subscription { kind: SubscriptionKind::Server, id: "srvr_1".into(), name: "github".into() }]);
        assert_eq!(
            serde_json::to_string(&manifest).unwrap(),
            r#"{"version":3,"orgId":"acme","baseUrl":"https://acme.example","syncedAt":"x","skills":{},"serverSkills":{"srvr_1 skill://git-workflow/SKILL.md":{"serverId":"srvr_1","serverSlug":"github","uri":"skill://git-workflow/SKILL.md","name":"github-git-workflow","files":{"SKILL.md":{"hash":"written","digest":"sha256:listed"}}}},"subscriptions":[{"kind":"server","id":"srvr_1","name":"github"}]}"#
        );
        write_manifest(dir.path(), &manifest).unwrap();
        assert_eq!(read_manifest(dir.path()).unwrap(), Some(manifest));
    }

    #[test]
    fn the_file_layout_is_stable() {
        let mut manifest = empty_manifest("acme", "https://acme.example");
        manifest.subscriptions =
            Some(vec![Subscription { kind: SubscriptionKind::Skill, id: "s".into(), name: "n".into() }]);
        let files = BTreeMap::from([
            ("SKILL.md".to_string(), FileEntry { hash: "h1".into(), digest: Some("sha256:h1".into()) }),
            ("old.md".to_string(), FileEntry { hash: "h2".into(), digest: None }),
        ]);
        manifest.skills.insert("s1".into(), ManifestEntry { name: "a".into(), updated_at: "t".into(), files });
        let text = serde_json::to_string(&manifest).unwrap();
        assert_eq!(
            text,
            r#"{"version":3,"orgId":"acme","baseUrl":"https://acme.example","syncedAt":"1970-01-01T00:00:00.000Z","skills":{"s1":{"name":"a","updatedAt":"t","files":{"SKILL.md":{"hash":"h1","digest":"sha256:h1"},"old.md":{"hash":"h2"}}}},"subscriptions":[{"kind":"skill","id":"s","name":"n"}]}"#
        );
    }
}
