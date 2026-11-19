//! Sends local skill folders back to Gatana.

use super::api::{Collection, Skill, SkillWithContent, SkillsApi, SkillsError, is_not_found};
use super::frontmatter::{
    META_COLLECTION, META_ID, META_ORG, META_UPDATED_AT, Revision, frontmatter_for, parse_skill_md, render_skill_md,
};
use super::manifest::{FileEntry, ManifestEntry, read_manifest, sha256, write_atomic, write_manifest};
use super::paths::{SKILL_FILE, check_paths};
use super::sync::SkillsIdentity;
use crate::util::iso_millis;
use anyhow::{Result, anyhow, bail};
use gatana_api::v1::types::{CreateSkillBody, UpdateSkillBody};
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet, HashSet};
use std::path::{Path, PathBuf};
use tokio::sync::OnceCell;
use walkdir::WalkDir;

/// The limits of the backend for one skill, SKILL.md included.
const MAX_FILES: usize = 512;
const MAX_BYTES: u64 = 4 * 1024 * 1024;

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
    /// The file that records the last push of each folder outside a synced directory. None: no
    /// record is read or written.
    pub memory_file: Option<PathBuf>,
}

/// The name of the push record in the home directory, next to `.gatana.config`.
pub const PUSH_MEMORY_FILE: &str = ".gatana.skill-pushes.json";

/// The last push of each skill folder that has no manifest next to it, by organization ID and by
/// the canonical path of the folder. A later push compares the server copy with it, as it does
/// with the manifest entry of a synced folder. It holds no content and no token.
#[derive(Default, Serialize, Deserialize)]
struct PushMemory {
    version: u8,
    folders: BTreeMap<String, BTreeMap<String, PushedFolder>>,
}

#[derive(Serialize, Deserialize)]
struct PushedFolder {
    #[serde(rename = "skillId")]
    skill_id: String,
    /// `updatedAt` of the server copy after the push.
    #[serde(rename = "updatedAt")]
    updated_at: String,
}

/// A missing or unreadable file is an empty record: the cost is one push with --force.
fn read_push_memory(path: &Path) -> PushMemory {
    let memory = std::fs::read_to_string(path).ok().and_then(|text| serde_json::from_str::<PushMemory>(&text).ok());
    memory.filter(|memory| memory.version == 1).unwrap_or_default()
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum PushAction {
    Created,
    Updated,
    Unchanged,
    Conflict,
    Error,
    /// A symlink, which a push never follows, or the folder of a server skill.
    Skipped,
}

#[derive(Clone, Debug, Serialize)]
pub struct PushResult {
    pub file: PathBuf,
    pub name: String,
    pub action: PushAction,
    pub detail: String,
}

/// A SKILL.md, a folder holding one, or a directory of such folders. A skill folder in that
/// directory that is a symlink is not followed: it goes to `symlinks`.
pub fn discover_skill_files(path: &Path, skip_empty: bool, symlinks: &mut Vec<PathBuf>) -> Result<Vec<PathBuf>> {
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
    let mut found_symlink = false;
    for entry in std::fs::read_dir(&target)? {
        let entry = entry?;
        let file_type = entry.file_type()?;
        if !file_type.is_dir() && !file_type.is_symlink() {
            continue;
        }
        let candidate = target.join(entry.file_name()).join(SKILL_FILE);
        if !candidate.is_file() {
            continue;
        }
        if file_type.is_symlink() {
            symlinks.push(target.join(entry.file_name()));
            found_symlink = true;
        } else {
            files.push(candidate);
        }
    }
    if files.is_empty() && !found_symlink && !skip_empty {
        bail!("No SKILL.md found at {} or in its subfolders", target.display());
    }
    files.sort();
    Ok(files)
}

/// The files of every path, each once. Two paths may be the same folder under two names
/// (`~/.agents/skills` is often a symlink to `~/.claude/skills`), and pushing a file twice would
/// report the second pass as unchanged at best.
fn discover_all(paths: &[PathBuf], skip_empty: bool, symlinks: &mut Vec<PathBuf>) -> Result<Vec<PathBuf>> {
    let mut seen = HashSet::new();
    let mut files = Vec::new();
    for path in paths {
        for file in discover_skill_files(path, skip_empty, symlinks)? {
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
    let mut symlinks = Vec::new();
    let files = discover_all(paths, options.skip_empty, &mut symlinks)?;
    let listing: OnceCell<Vec<Skill>> = OnceCell::new();
    let collections = Collections { api, by_name: OnceCell::new() };
    if let Some(name) = &options.collection
        && collections.id_of(name).await?.is_none()
    {
        bail!("No accessible collection named \"{name}\"");
    }
    let mut results: Vec<PushResult> = symlinks
        .into_iter()
        .map(|folder| PushResult {
            name: folder.file_name().unwrap_or_default().to_string_lossy().into_owned(),
            file: folder,
            action: PushAction::Skipped,
            detail: "the folder is a symlink and is not pushed. Push the folder that it points to".into(),
        })
        .collect();
    for file in files {
        results.push(push_one(api, identity, &file, options, &listing, &collections).await?);
    }
    Ok(results)
}

fn folder_name(file: &Path) -> String {
    file.parent().and_then(Path::file_name).map(|name| name.to_string_lossy().into_owned()).unwrap_or_default()
}

/// Files by their path with `/`, each with its content.
type FolderFiles = Vec<(String, Vec<u8>)>;

/// Files whose path has a name that starts with a dot, each with its source. None for a symlink.
type HiddenFiles = Vec<(String, Option<PathBuf>)>;

/// The files of a skill folder other than its SKILL.md, each with its path and content, in byte
/// order of the path. A path with a name that starts with a dot goes to the second list, for
/// `push_one` to decide on, and counts for no limit. Other symlinks are not followed and not
/// pushed, and each gets a note. The inner error says why the folder cannot be pushed as it is.
fn read_folder(
    folder: &Path,
    skill_md_bytes: usize,
    notes: &mut Vec<String>,
) -> Result<Result<(FolderFiles, HiddenFiles), String>> {
    let mut found = Vec::new();
    let mut hidden = Vec::new();
    let mut bytes = skill_md_bytes as u64;
    // A version control folder and the Finder's `.DS_Store` are not part of a skill.
    let walk = WalkDir::new(folder).min_depth(1).into_iter().filter_entry(|entry| entry.file_name() != ".git");
    for entry in walk {
        let entry = entry?;
        let Some(path) = entry.path().strip_prefix(folder)?.to_str() else {
            return Ok(Err(format!("{} has a name that is not valid Unicode", entry.path().display())));
        };
        let path = path.replace(std::path::MAIN_SEPARATOR, "/");
        let is_symlink = entry.path_is_symlink();
        if entry.file_name() == ".DS_Store" || !(is_symlink || entry.file_type().is_file()) {
            continue;
        }
        if path.split('/').any(|segment| segment.starts_with('.')) {
            hidden.push((path, (!is_symlink).then(|| entry.into_path())));
        } else if is_symlink {
            notes.push(format!("symlink {path} not pushed"));
        } else if path != SKILL_FILE {
            bytes += entry.metadata()?.len();
            found.push((path, entry.into_path()));
        }
    }
    if found.len() + 1 > MAX_FILES || bytes > MAX_BYTES {
        return Ok(Err(format!(
            "the folder holds {} files and {bytes} bytes. A skill takes at most {MAX_FILES} files and {MAX_BYTES} bytes (4 MiB), SKILL.md included",
            found.len() + 1
        )));
    }
    let (_, refused) = check_paths(found.iter().map(|(path, _)| path.as_str()).chain([SKILL_FILE]));
    if !refused.is_empty() {
        let reasons: Vec<String> = refused.iter().map(|(path, reason)| format!("{path:?}: {reason}")).collect();
        return Ok(Err(format!("cannot push every file, because a sync could not write it: {}", reasons.join("; "))));
    }
    found.sort_by(|a, b| a.0.as_bytes().cmp(b.0.as_bytes()));
    let mut files = Vec::new();
    for (path, source) in found {
        files.push((path, std::fs::read(source)?));
    }
    Ok(Ok((files, hidden)))
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
    // A request that the server refuses for this skill does not stop the other skills.
    let refusal = |name: &str, context: &str, error: anyhow::Error| match error.downcast_ref::<SkillsError>() {
        Some(SkillsError::Api { status: 400, message }) => {
            Ok(result(name, PushAction::Error, format!("{context}{message}")))
        }
        _ => Err(error),
    };
    if std::fs::symlink_metadata(file).is_ok_and(|metadata| metadata.file_type().is_symlink()) {
        return Ok(result(&folder_name(file), PushAction::Skipped, "the file is a symlink and is not pushed".into()));
    }
    let text = match std::fs::read_to_string(file) {
        Ok(text) => text,
        Err(error) => return Ok(result(&folder_name(file), PushAction::Error, error.to_string())),
    };
    let (frontmatter, body) = match parse_skill_md(&text) {
        Ok(parsed) => parsed,
        Err(error) => return Ok(result(&folder_name(file), PushAction::Error, error.to_string())),
    };
    let name = frontmatter.name.clone();
    let mut notes = Vec::new();
    if folder_name(file) != name {
        notes.push(format!("folder name is {}; skill name is {name}", folder_name(file)));
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
    // CLI 5.2 and older wrote the ID of the skill into the SKILL.md. Such a file is not the document
    // of the server, so it is still compared and sent as name, description and body.
    let stamped = frontmatter.meta(META_ID).is_some();

    // The whole folder goes with a SKILL.md. A file of another name is pushed alone.
    let in_folder = file.file_name().is_some_and(|file_name| file_name == SKILL_FILE);

    // The manifest of the directory the folder sits in, when the folder came from a sync.
    let manifest_dir = file.parent().and_then(Path::parent).map(Path::to_path_buf).unwrap_or_default();
    let mut manifest = read_manifest(&manifest_dir).ok().flatten();
    // Gatana has no import of a server skill into the registry, and the default paths of a push
    // hold the folders that a sync wrote for server skills. This holds for the sync of any
    // organization, and the folder is not read.
    let server_skill = manifest
        .as_ref()
        .filter(|_| in_folder)
        .and_then(|manifest| manifest.server_skills.values().find(|entry| entry.name == folder_name(file)));
    if let Some(entry) = server_skill {
        return Ok(result(
            &name,
            PushAction::Skipped,
            format!("the folder holds a skill of the MCP server \"{}\", which a push does not send", entry.server_slug),
        ));
    }
    // A folder that the sync of another organization wrote. Its manifest names the skills there.
    let synced_from = manifest
        .as_ref()
        .filter(|manifest| manifest.org_id != identity.org_id || manifest.base_url != identity.base_url)
        .map(|manifest| (manifest.org_id.clone(), manifest.base_url.clone()));
    if let Some((org, base_url)) = synced_from {
        if !options.force {
            return Ok(result(
                &name,
                PushAction::Error,
                format!(
                    "the folder was synced from organization {org} ({base_url}), not {} ({}). Use --org {org} to push it there, or --force to create a copy here",
                    identity.org_id, identity.base_url
                ),
            ));
        }
        // A copy in this organization. The manifest of the other one stays as it is.
        manifest = None;
    }
    let tracked_id = manifest
        .as_ref()
        .filter(|_| in_folder)
        .and_then(|manifest| manifest.skills.iter().find(|(_, entry)| entry.name == folder_name(file)))
        .map(|(id, _)| id.clone());
    // What the push record knows this folder by. A lone file is known by its own path.
    let memory_key = std::fs::canonicalize(file.parent().filter(|_| in_folder).unwrap_or(file))
        .map(|path| path.to_string_lossy().into_owned())
        .unwrap_or_default();

    let (mut others, hidden) = match file.parent().filter(|_| in_folder) {
        Some(folder) => match read_folder(folder, text.len(), &mut notes)? {
            Ok(files) => files,
            Err(detail) => return Ok(result(&name, PushAction::Error, detail)),
        },
        None => (Vec::new(), Vec::new()),
    };
    let digest_of = |content: &[u8]| format!("sha256:{}", sha256(content));
    let server_stores_no_files = |count: usize| {
        format!(
            "the server stores only the SKILL.md: {count} other files not pushed. Update the Gatana server to push them"
        )
    };

    let mut remote: Option<SkillWithContent> = None;
    if let Some(id) = tracked_id.as_deref().or(meta_id).filter(|id| !id.is_empty()) {
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
            notes.push(format!("collection \"{collection_name}\" not found; kept the current collection"));
        }
    }

    // The files of the server copy. A lone file is no folder, so it goes as name, description and
    // body: the file route would replace every file of the skill with this one.
    let server_files = match &remote {
        Some(remote) if in_folder => api.list_files(&remote.skill.id).await?,
        _ => None,
    };
    // A name that starts with a dot is often a secret, such as `.env`, or the state of a tool. Such a
    // file goes only when the server copy has it, so that the push does not delete it there.
    let mut left_out = BTreeSet::new();
    for (path, source) in hidden {
        match source.filter(|_| server_files.iter().flatten().any(|file| file.path == path)) {
            Some(source) => others.push((path, std::fs::read(source)?)),
            None => {
                let segments: Vec<&str> = path.split('/').collect();
                let end = segments.iter().position(|segment| segment.starts_with('.')).unwrap_or_default();
                left_out.insert(segments[..=end].join("/"));
            }
        }
    }
    others.sort_by(|a, b| a.0.as_bytes().cmp(b.0.as_bytes()));
    if !left_out.is_empty() {
        let names: Vec<String> = left_out.into_iter().collect();
        notes.push(format!(
            "{} not pushed: a file whose name starts with a dot goes only when the skill on the server has it",
            names.join(", ")
        ));
    }

    // A request that failed after the server stored something. The manifest or the push record
    // gets what the server holds first, so that the next push has a baseline.
    let mut failure: Option<(&str, anyhow::Error)> = None;
    // Whether the server took the SKILL.md as a document and the other files: what the manifest
    // can record digests for.
    let (saved, action, document_stored, files_stored) = match remote {
        Some(remote) => {
            let id = remote.skill.id.clone();
            let document = server_files.is_some() && !stamped;
            let (document_unchanged, others_unchanged) = match &server_files {
                Some(server_files) => {
                    let digest =
                        |path: &str| server_files.iter().find(|file| file.path == path).map(|file| &file.digest);
                    (
                        digest(SKILL_FILE) == Some(&digest_of(text.as_bytes())),
                        server_files.len() == others.len() + 1
                            && others.iter().all(|(path, content)| digest(path) == Some(&digest_of(content))),
                    )
                }
                None => (false, true),
            };
            let skill_md_unchanged = if document {
                document_unchanged
            } else {
                remote.skill.name == name
                    && same_text(&remote.skill.description, &frontmatter.description)
                    && same_text(&remote.content, &body)
            };
            if server_files.is_none() && !others.is_empty() {
                notes.push(server_stores_no_files(others.len()));
            }
            let content_unchanged = skill_md_unchanged && others_unchanged;

            let remote_updated_at =
                iso_millis(&remote.skill.updated_at).unwrap_or_else(|| remote.skill.updated_at.clone());
            let baseline = manifest
                .as_ref()
                .and_then(|manifest| manifest.skills.get(&id))
                .map(|entry| entry.updated_at.clone())
                .or_else(|| frontmatter.meta(META_UPDATED_AT).map(str::to_string))
                .filter(|baseline| !baseline.is_empty())
                // The record of the last push from this machine. It counts only for the skill that
                // the push went to: a skill that was deleted and created again has no baseline.
                .or_else(|| {
                    let mut memory = read_push_memory(options.memory_file.as_deref()?);
                    let pushed = memory.folders.get_mut(&identity.org_id)?.remove(&memory_key)?;
                    (pushed.skill_id == id).then_some(pushed.updated_at)
                });
            // A folder that is equal to the server copy overwrites nothing, so it needs no baseline.
            if !options.force && !content_unchanged {
                let Some(baseline) = &baseline else {
                    return Ok(result(
                        &name,
                        PushAction::Conflict,
                        if manifest.is_some() {
                            format!(
                                "a skill named {name} exists, but this folder has no saved version to compare. Run \"gatana skills install\" first, or use --force to overwrite"
                            )
                        } else {
                            format!(
                                "a skill named {name} exists, and this machine has no record of a push of this folder to it. Check that the folder is the newer copy, then use --force to overwrite"
                            )
                        },
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
            let files_change = server_files.is_some() && (!others_unchanged || (document && !skill_md_unchanged));
            // The file route replaces the whole set, so a file of the server that the push does not
            // send is deleted there. That is the intent for a file that the folder had. A file that
            // the folder never got, or that a sync cannot write, stays unless --force.
            if files_change && !options.force {
                let sent: HashSet<&str> = others.iter().map(|(path, _)| path.as_str()).chain([SKILL_FILE]).collect();
                let server_paths: Vec<&str> = server_files.iter().flatten().map(|file| file.path.as_str()).collect();
                let unwritable = check_paths(server_paths.iter().copied())
                    .1
                    .into_iter()
                    .map(|(path, _)| path)
                    .find(|path| !sent.contains(path));
                let had = manifest.as_ref().and_then(|manifest| manifest.skills.get(&id));
                let never_got = had.and_then(|entry| {
                    server_paths.iter().find(|path| !sent.contains(**path) && !entry.files.contains_key(**path))
                });
                let detail = match (unwritable, never_got) {
                    (Some(path), _) => Some(format!(
                        "the server holds the file {path:?}, which a sync does not write. A push would delete it. Use --force to push anyway"
                    )),
                    (None, Some(path)) => Some(format!(
                        "the server holds the file {path:?}, which this folder never got. A push would delete it. Run \"gatana skills sync\" to get the file, or use --force to push anyway"
                    )),
                    (None, None) => None,
                };
                if let Some(detail) = detail {
                    return Ok(result(&name, PushAction::Error, detail));
                }
            }
            if content_unchanged && !moves {
                (remote.skill, PushAction::Unchanged, document, server_files.is_some())
            } else if options.dry_run {
                return Ok(result(
                    &name,
                    PushAction::Updated,
                    [vec!["would update".to_string()], notes].concat().join("; "),
                ));
            } else {
                let fields = |collection_id: Option<String>| UpdateSkillBody {
                    name: None,
                    description: None,
                    content: None,
                    collection_id,
                    markdown: None,
                    visibility: None,
                };
                // The last answer of the server, and whether it took the files, also when a later
                // request fails.
                let mut saved: Option<Skill> = None;
                let mut files_saved = false;
                let outcome = async {
                    if !document && (!skill_md_unchanged || moves) {
                        let body = UpdateSkillBody {
                            name: Some(name.clone()),
                            description: Some(frontmatter.description.clone()),
                            content: Some(body.clone()),
                            ..fields(collection_id.clone().filter(|_| moves))
                        };
                        saved = Some(api.update(&id, &body).await?);
                    }
                    if files_change {
                        let mut files = others.clone();
                        if document {
                            files.push((SKILL_FILE.to_string(), text.clone().into_bytes()));
                        }
                        // The file route answers the `updatedAt` that its write set. A read after
                        // the write could return the time of a later change by someone else.
                        let updated_at = api
                            .replace_files(&id, &files)
                            .await?
                            .ok_or_else(|| anyhow!("the server no longer has the file route that listed the files"))?;
                        let mut skill = saved.take().unwrap_or_else(|| remote.skill.clone());
                        if document {
                            (skill.name, skill.description) = (name.clone(), frontmatter.description.clone());
                        }
                        saved = Some(Skill { updated_at, ..skill });
                        files_saved = true;
                    }
                    if document && moves {
                        saved = Some(api.update(&id, &fields(collection_id.clone())).await?);
                    }
                    anyhow::Ok(())
                }
                .await;
                match (outcome, saved) {
                    (Ok(()), saved) => (
                        saved.unwrap_or_else(|| remote.skill.clone()),
                        PushAction::Updated,
                        document,
                        server_files.is_some(),
                    ),
                    (Err(error), None) => return refusal(&name, "", error),
                    (Err(error), Some(saved)) => {
                        failure = Some(("updated in part, because the server refused the next request: ", error));
                        (saved, PushAction::Error, document && files_saved, files_saved)
                    }
                }
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
            // The document, so that a server with file routes stores it byte for byte.
            let create = CreateSkillBody {
                name: stamped.then(|| name.clone()),
                description: stamped.then(|| frontmatter.description.clone()),
                content: stamped.then(|| body.clone()),
                collection_id: collection_id.clone(),
                markdown: (!stamped).then(|| text.clone()),
                visibility: None,
            };
            let created = match api.create(&create).await {
                Ok(created) => created,
                Err(error) => return refusal(&name, "", error),
            };
            if others.is_empty() {
                (created, PushAction::Created, false, false)
            } else {
                match api.replace_files(&created.id, &others).await {
                    Ok(Some(updated_at)) => (Skill { updated_at, ..created }, PushAction::Created, !stamped, true),
                    Ok(None) => {
                        notes.push(server_stores_no_files(others.len()));
                        (created, PushAction::Created, false, false)
                    }
                    Err(error) => {
                        failure = Some(("created, but the server refused its other files: ", error));
                        (created, PushAction::Error, false, false)
                    }
                }
            }
        }
    };

    if !options.dry_run {
        let mut text = text;
        if stamped {
            // Stamp the file with the revision it now matches, keeping any other frontmatter untouched.
            text = render_skill_md(
                &frontmatter_for(
                    Revision::from(&saved),
                    &identity.org_id,
                    frontmatter.extra.clone(),
                    &frontmatter.metadata,
                ),
                &body,
            );
            std::fs::write(file, &text)?;
        }
        if let Some(manifest) = manifest.as_mut() {
            let updated_at = iso_millis(&saved.updated_at).unwrap_or_else(|| saved.updated_at.clone());
            let skill_md = FileEntry {
                hash: sha256(text.as_bytes()),
                digest: document_stored.then(|| digest_of(text.as_bytes())),
            };
            let mut files = BTreeMap::from([(SKILL_FILE.to_string(), skill_md)]);
            if files_stored {
                for (path, content) in &others {
                    files.insert(path.clone(), FileEntry { hash: sha256(content), digest: Some(digest_of(content)) });
                }
                // The folder is in line with the file list of the skill now.
                manifest.files_unchecked.remove(&saved.id);
            } else if let Some(entry) = manifest.skills.get(&saved.id) {
                // The server kept its other files, so the entry keeps what the folder had of them.
                let kept = entry.files.iter().filter(|(path, _)| *path != SKILL_FILE);
                files.extend(kept.map(|(path, file)| (path.clone(), file.clone())));
            }
            // The entry names the folder, so that a sync moves it when the push renamed the skill.
            let folder = if in_folder { folder_name(file) } else { saved.name.clone() };
            manifest.skills.insert(saved.id.clone(), ManifestEntry { name: folder, updated_at, files });
            write_manifest(&manifest_dir, manifest)?;
        } else if let Some(memory_file) = options.memory_file.as_ref().filter(|_| !memory_key.is_empty()) {
            // No manifest records this folder, so the push record does.
            let mut memory = read_push_memory(memory_file);
            memory.version = 1;
            let updated_at = iso_millis(&saved.updated_at).unwrap_or_else(|| saved.updated_at.clone());
            let pushed = PushedFolder { skill_id: saved.id.clone(), updated_at };
            memory.folders.entry(identity.org_id.clone()).or_default().insert(memory_key, pushed);
            // A folder that is gone needs no record.
            for folders in memory.folders.values_mut() {
                folders.retain(|path, _| Path::new(path).exists());
            }
            memory.folders.retain(|_, folders| !folders.is_empty());
            write_atomic(memory_file, format!("{}\n", serde_json::to_string_pretty(&memory)?).as_bytes())?;
        }
    }
    if let Some((context, error)) = failure {
        return refusal(&name, context, error);
    }
    Ok(result(&name, action, notes.join("; ")))
}
