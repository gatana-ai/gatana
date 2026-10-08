//! `.gatana-skills.json` sits in every synced directory and records which skill folders the sync
//! owns, and which collections and skills the directory follows. Everything not in it is somebody
//! else's and is never touched. One directory serves one organization.

use indexmap::IndexMap;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::path::Path;

pub const MANIFEST_FILE: &str = ".gatana-skills.json";

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct ManifestEntry {
    pub name: String,
    #[serde(rename = "updatedAt")]
    pub updated_at: String,
    /// sha256 of the SKILL.md as written, to notice local edits before overwriting them.
    pub hash: String,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize, Default)]
#[serde(rename_all = "lowercase")]
pub enum SubscriptionKind {
    /// Manifests written before skills could be followed carry no kind: they followed collections.
    #[default]
    Collection,
    Skill,
}

impl SubscriptionKind {
    pub fn as_str(self) -> &'static str {
        match self {
            SubscriptionKind::Collection => "collection",
            SubscriptionKind::Skill => "skill",
        }
    }
}

/// A collection or a single skill the directory follows. The id is what is followed; the name is
/// what was last seen, for messages.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Subscription {
    #[serde(default)]
    pub kind: SubscriptionKind,
    pub id: String,
    pub name: String,
}

/// Version 2. `subscriptions` null means the directory takes every skill the user can read; a
/// list, even an empty one, means only the skills of those collections and the skills themselves.
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
    pub subscriptions: Option<Vec<Subscription>>,
}

#[derive(Deserialize)]
struct ManifestV1 {
    #[serde(rename = "orgId")]
    org_id: String,
    #[serde(rename = "baseUrl")]
    base_url: String,
    #[serde(rename = "syncedAt")]
    synced_at: String,
    skills: IndexMap<String, ManifestEntry>,
}

#[derive(Debug, thiserror::Error)]
#[error("{0}")]
pub struct ManifestError(pub String);

pub fn empty_manifest(org_id: &str, base_url: &str) -> SkillsManifest {
    SkillsManifest {
        version: 2,
        org_id: org_id.to_string(),
        base_url: base_url.to_string(),
        synced_at: "1970-01-01T00:00:00.000Z".to_string(),
        skills: IndexMap::new(),
        subscriptions: None,
    }
}

/// Missing file: None. A version 1 file reads as version 2 without subscriptions. Unreadable
/// content: an error, on purpose. Treating a broken manifest as empty would make every owned folder
/// foreign, or with --force deletable.
pub fn read_manifest(dir: &Path) -> anyhow::Result<Option<SkillsManifest>> {
    let path = dir.join(MANIFEST_FILE);
    let text = match std::fs::read_to_string(&path) {
        Ok(text) => text,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(None),
        Err(error) => return Err(anyhow::Error::new(error).context(format!("reading {}", path.display()))),
    };
    let shape_error =
        || ManifestError(format!("{} has an unexpected shape. Fix or delete it, then sync again", path.display()));
    let value: Value = serde_json::from_str(&text).map_err(|_| {
        ManifestError(format!("{} is not valid JSON. Fix or delete it, then sync again", path.display()))
    })?;
    match value.get("version").and_then(Value::as_u64) {
        Some(2) => serde_json::from_value(value).map(Some).map_err(|_| shape_error().into()),
        Some(1) => {
            let v1: ManifestV1 = serde_json::from_value(value).map_err(|_| shape_error())?;
            Ok(Some(SkillsManifest {
                version: 2,
                org_id: v1.org_id,
                base_url: v1.base_url,
                synced_at: v1.synced_at,
                skills: v1.skills,
                subscriptions: None,
            }))
        }
        _ => Err(shape_error().into()),
    }
}

pub fn write_manifest(dir: &Path, manifest: &SkillsManifest) -> anyhow::Result<()> {
    std::fs::create_dir_all(dir)?;
    let text = format!("{}\n", serde_json::to_string_pretty(manifest)?);
    write_atomic(&dir.join(MANIFEST_FILE), &text)
}

/// Writes next to the target and renames over it, so a reader never sees half a file.
pub fn write_atomic(path: &Path, text: &str) -> anyhow::Result<()> {
    let mut tmp = path.as_os_str().to_owned();
    tmp.push(format!(".{}.tmp", std::process::id()));
    std::fs::write(&tmp, text)?;
    std::fs::rename(&tmp, path)?;
    Ok(())
}

pub fn sha256(text: &str) -> String {
    let digest = Sha256::digest(text.as_bytes());
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
        manifest
            .skills
            .insert("s1".into(), ManifestEntry { name: "a".into(), updated_at: "x".into(), hash: "y".into() });
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
        std::fs::write(dir.path().join(MANIFEST_FILE), r#"{"version":2,"skills":{}}"#).unwrap();
        assert!(read_manifest(dir.path()).unwrap_err().downcast_ref::<ManifestError>().is_some());
    }

    #[test]
    fn a_version_1_manifest_reads_as_version_2_without_subscriptions() {
        let dir = tempfile::tempdir().unwrap();
        std::fs::write(
            dir.path().join(MANIFEST_FILE),
            r#"{"version":1,"orgId":"acme","baseUrl":"https://acme.example","syncedAt":"x","skills":{}}"#,
        )
        .unwrap();
        let manifest = read_manifest(dir.path()).unwrap().unwrap();
        assert_eq!(manifest.version, 2);
        assert_eq!(manifest.subscriptions, None);
    }

    #[test]
    fn the_file_layout_matches_the_typescript_cli() {
        let mut manifest = empty_manifest("acme", "https://acme.example");
        manifest.subscriptions =
            Some(vec![Subscription { kind: SubscriptionKind::Skill, id: "s".into(), name: "n".into() }]);
        let text = serde_json::to_string_pretty(&manifest).unwrap();
        assert_eq!(
            text,
            "{\n  \"version\": 2,\n  \"orgId\": \"acme\",\n  \"baseUrl\": \"https://acme.example\",\n  \"syncedAt\": \
             \"1970-01-01T00:00:00.000Z\",\n  \"skills\": {},\n  \"subscriptions\": [\n    {\n      \"kind\": \"skill\",\n      \
             \"id\": \"s\",\n      \"name\": \"n\"\n    }\n  ]\n}"
        );
    }
}
