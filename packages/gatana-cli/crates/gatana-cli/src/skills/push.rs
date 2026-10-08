//! Sends local SKILL.md files back to Gatana.

use super::api::{Collection, Skill, SkillWithContent, SkillsApi, is_not_found};
use super::frontmatter::{
    META_COLLECTION, META_ID, META_ORG, META_UPDATED_AT, Revision, frontmatter_for, parse_skill_md, render_skill_md,
};
use super::manifest::{ManifestEntry, read_manifest, sha256, write_manifest};
use super::sync::SkillsIdentity;
use crate::util::iso_millis;
use anyhow::{Result, anyhow, bail};
use gatana_api::v1::types::{CreateSkillBody, UpdateSkillBody};
use serde::Serialize;
use std::collections::HashSet;
use std::path::{Path, PathBuf};
use tokio::sync::OnceCell;

const SKILL_FILE: &str = "SKILL.md";

#[derive(Clone, Debug, Default)]
pub struct PushOptions {
    pub force: bool,
    pub dry_run: bool,
    /// Name of the collection to put the pushed skills in. Without it, a file that names one in its
    /// `gatana-collection` metadata goes there, so a synced file stays in its collection; a file
    /// naming none is created at root and an existing skill keeps its place.
    pub collection: Option<String>,
    /// A path holding no skill is skipped instead of refused. Set when the paths are the default
    /// sync targets rather than something the user typed: an agent folder that does not exist yet,
    /// or holds nothing, is no mistake then.
    pub skip_empty: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum PushAction {
    Created,
    Updated,
    Unchanged,
    Conflict,
    Error,
}

#[derive(Clone, Debug, Serialize)]
pub struct PushResult {
    pub file: PathBuf,
    pub name: String,
    pub action: PushAction,
    pub detail: String,
}

/// A SKILL.md, a folder holding one, or a directory of such folders.
pub fn discover_skill_files(path: &Path, skip_empty: bool) -> Result<Vec<PathBuf>> {
    let target = std::path::absolute(path)?;
    let metadata = match std::fs::metadata(&target) {
        Ok(metadata) => metadata,
        Err(_) if skip_empty => return Ok(Vec::new()),
        Err(error) => return Err(anyhow!("{}: {error}", target.display())),
    };
    if metadata.is_file() {
        return Ok(vec![target]);
    }
    let own = target.join(SKILL_FILE);
    if own.is_file() {
        return Ok(vec![own]);
    }
    let mut files = Vec::new();
    for entry in std::fs::read_dir(&target)? {
        let entry = entry?;
        let file_type = entry.file_type()?;
        if !file_type.is_dir() && !file_type.is_symlink() {
            continue;
        }
        let candidate = target.join(entry.file_name()).join(SKILL_FILE);
        if candidate.is_file() {
            files.push(candidate);
        }
    }
    if files.is_empty() && !skip_empty {
        bail!("No SKILL.md found at {}, in it, or in its sub-folders", target.display());
    }
    files.sort();
    Ok(files)
}

/// The files of every path, each once. Two paths may be the same folder under two names
/// (`~/.agents/skills` is often a symlink to `~/.claude/skills`), and pushing a file twice would
/// report the second pass as unchanged at best.
fn discover_all(paths: &[PathBuf], skip_empty: bool) -> Result<Vec<PathBuf>> {
    let mut seen = HashSet::new();
    let mut files = Vec::new();
    for path in paths {
        for file in discover_skill_files(path, skip_empty)? {
            if seen.insert(std::fs::canonicalize(&file)?) {
                files.push(file);
            }
        }
    }
    Ok(files)
}

fn same_text(a: &str, b: &str) -> bool {
    a.trim_end() == b.trim_end()
}

/// Collection ids by name, fetched once per push and only when a file or the option asks for one.
struct Collections<'a, A: SkillsApi> {
    api: &'a A,
    by_name: OnceCell<Vec<Collection>>,
}

impl<A: SkillsApi> Collections<'_, A> {
    async fn id_of(&self, name: &str) -> Result<Option<String>> {
        let collections = self.by_name.get_or_try_init(|| self.api.list_collections()).await?;
        Ok(collections.iter().find(|collection| collection.name == name).map(|collection| collection.id.clone()))
    }
}

pub async fn push_skills(
    api: &impl SkillsApi,
    identity: &SkillsIdentity,
    paths: &[PathBuf],
    options: &PushOptions,
) -> Result<Vec<PushResult>> {
    let files = discover_all(paths, options.skip_empty)?;
    let listing: OnceCell<Vec<Skill>> = OnceCell::new();
    let collections = Collections { api, by_name: OnceCell::new() };
    if let Some(name) = &options.collection
        && collections.id_of(name).await?.is_none()
    {
        bail!("No collection named \"{name}\" that you can see");
    }
    let mut results = Vec::new();
    for file in files {
        results.push(push_one(api, identity, &file, options, &listing, &collections).await?);
    }
    Ok(results)
}

fn folder_name(file: &Path) -> String {
    file.parent().and_then(Path::file_name).map(|name| name.to_string_lossy().into_owned()).unwrap_or_default()
}

async fn push_one<A: SkillsApi>(
    api: &A,
    identity: &SkillsIdentity,
    file: &Path,
    options: &PushOptions,
    listing: &OnceCell<Vec<Skill>>,
    collections: &Collections<'_, A>,
) -> Result<PushResult> {
    let result = |name: &str, action: PushAction, detail: String| PushResult {
        file: file.to_path_buf(),
        name: name.to_string(),
        action,
        detail,
    };
    let parsed = std::fs::read_to_string(file).map_err(anyhow::Error::from).and_then(|text| Ok(parse_skill_md(&text)?));
    let (frontmatter, body) = match parsed {
        Ok(parsed) => parsed,
        Err(error) => return Ok(result(&folder_name(file), PushAction::Error, error.to_string())),
    };
    let name = frontmatter.name.clone();
    let mut notes = Vec::new();
    if folder_name(file) != name {
        notes.push(format!("folder is named {}, the skill {name}", folder_name(file)));
    }

    let meta_org = frontmatter.meta(META_ORG).filter(|org| !org.is_empty());
    if let Some(org) = meta_org.filter(|org| *org != identity.org_id)
        && !options.force
    {
        return Ok(result(
            &name,
            PushAction::Error,
            format!(
                "belongs to organization {org}, not {}; use --org {org} or --force to create a copy here",
                identity.org_id
            ),
        ));
    }
    let meta_id =
        if meta_org.is_none() || meta_org == Some(identity.org_id.as_str()) { frontmatter.meta(META_ID) } else { None };

    // The manifest of the directory the folder sits in, when the folder came from a sync.
    let manifest_dir = file.parent().and_then(Path::parent).map(Path::to_path_buf).unwrap_or_default();
    let mut manifest = read_manifest(&manifest_dir).ok().flatten();

    let mut remote: Option<SkillWithContent> = None;
    if let Some(id) = meta_id.filter(|id| !id.is_empty()) {
        match api.get(id).await {
            Ok(found) => remote = Some(found),
            Err(error) if is_not_found(&error) => {}
            Err(error) => return Err(error),
        }
    }
    if remote.is_none() {
        let all = listing.get_or_try_init(|| api.list(None, None)).await?;
        if let Some(by_name) = all.iter().find(|skill| skill.name == name) {
            remote = Some(api.get(&by_name.id).await?);
        }
    }

    // Where the skill goes: the option first, else the collection the file names. None leaves an
    // existing skill where it is and creates a new one at root.
    let mut collection_id = None;
    if let Some(collection_name) = options.collection.as_deref().or(frontmatter.meta(META_COLLECTION)) {
        collection_id = collections.id_of(collection_name).await?;
        if collection_id.is_none() {
            notes.push(format!("collection \"{collection_name}\" not found; left where it is"));
        }
    }

    let (saved, action) = match remote {
        Some(remote) => {
            let remote_updated_at =
                iso_millis(&remote.skill.updated_at).unwrap_or_else(|| remote.skill.updated_at.clone());
            let baseline = manifest
                .as_ref()
                .and_then(|manifest| manifest.skills.get(&remote.skill.id))
                .map(|entry| entry.updated_at.clone())
                .or_else(|| frontmatter.meta(META_UPDATED_AT).map(str::to_string))
                .filter(|baseline| !baseline.is_empty());
            if !options.force {
                let Some(baseline) = &baseline else {
                    return Ok(result(
                        &name,
                        PushAction::Conflict,
                        format!(
                            "a skill named {name} exists and this file has no install baseline; run \"gatana skills install\" first, or --force to overwrite"
                        ),
                    ));
                };
                if remote_updated_at.as_str() > baseline.as_str() {
                    return Ok(result(
                        &name,
                        PushAction::Conflict,
                        format!(
                            "changed on the server at {remote_updated_at}, after your copy ({baseline}); sync first, or --force to overwrite"
                        ),
                    ));
                }
            }
            let moves = collection_id.is_some() && collection_id != remote.skill.collection_id;
            let unchanged = remote.skill.name == name
                && same_text(&remote.skill.description, &frontmatter.description)
                && same_text(&remote.content, &body)
                && !moves;
            if unchanged {
                (remote.skill, PushAction::Unchanged)
            } else if options.dry_run {
                return Ok(result(
                    &name,
                    PushAction::Updated,
                    [vec!["would update".to_string()], notes].concat().join("; "),
                ));
            } else {
                let body = UpdateSkillBody {
                    name: Some(name.clone()),
                    description: Some(frontmatter.description.clone()),
                    content: Some(body.clone()),
                    collection_id: if moves { collection_id.clone() } else { None },
                    markdown: None,
                    visibility: None,
                };
                (api.update(&remote.skill.id, &body).await?, PushAction::Updated)
            }
        }
        None if options.dry_run => {
            return Ok(result(
                &name,
                PushAction::Created,
                [vec!["would create".to_string()], notes].concat().join("; "),
            ));
        }
        None => {
            let body = CreateSkillBody {
                name: Some(name.clone()),
                description: Some(frontmatter.description.clone()),
                content: Some(body.clone()),
                collection_id: collection_id.clone(),
                markdown: None,
                visibility: None,
            };
            (api.create(&body).await?, PushAction::Created)
        }
    };

    // Stamp the file with the revision it now matches, keeping any other frontmatter untouched.
    let text = render_skill_md(
        &frontmatter_for(Revision::from(&saved), &identity.org_id, frontmatter.extra.clone(), &frontmatter.metadata),
        &body,
    );
    if !options.dry_run {
        std::fs::write(file, &text)?;
        if let Some(manifest) = manifest.as_mut().filter(|manifest| manifest.org_id == identity.org_id) {
            let updated_at = iso_millis(&saved.updated_at).unwrap_or_else(|| saved.updated_at.clone());
            manifest
                .skills
                .insert(saved.id.clone(), ManifestEntry { name: saved.name.clone(), updated_at, hash: sha256(&text) });
            write_manifest(&manifest_dir, manifest)?;
        }
    }
    Ok(result(&name, action, notes.join("; ")))
}
