//! An in-memory skills registry with the rules of the backend that matter to sync, push and
//! following collections.

#![allow(dead_code)]

use anyhow::Result;
use chrono::{DateTime, Duration, SecondsFormat, Utc};
use gatana_api::v1::types::{CreateSkillBody, UpdateSkillBody};
use gatana_cli::skills::api::{
    Collection, ServerSkill, ServerSkillFile, Skill, SkillFile, SkillWithContent, SkillsApi, SkillsError,
};
use gatana_cli::skills::frontmatter::parse_skill_md;
use gatana_cli::skills::manifest::{MANIFEST_FILE, sha256};
use gatana_cli::util::iso_millis;
use serde_json::json;
use std::cell::{Cell, RefCell};
use std::collections::BTreeMap;
use std::path::Path;

/// A supporting file of the skill that `cli_5_2_folder` seeds.
pub const OLD_GUIDE: &str = "references/guide.md";

/// What CLI 5.2 left in `dir` for the skill `beta`, which had a supporting file on the server
/// already: a stamped SKILL.md with this body, and a version 2 manifest that knows only the
/// SKILL.md with the body `# Old`. Answers the ID of the skill.
pub fn cli_5_2_folder(api: &FakeSkillsApi, dir: &Path, body: &str) -> String {
    let id = api.seed("beta", "# Old\n").id;
    api.put_files(&id, &[(OLD_GUIDE, b"guide\n")]);
    let updated_at = iso_millis(&api.find("beta").unwrap().updated_at).unwrap();
    let file = |body: &str| {
        format!(
            "---\nname: beta\ndescription: \"Use for beta\"\nmetadata:\n  gatana-id: \"{id}\"\n  gatana-org: \"acme\"\n  gatana-updated-at: \"{updated_at}\"\n---\n\n{body}"
        )
    };
    std::fs::create_dir_all(dir.join("beta")).unwrap();
    std::fs::write(dir.join("beta/SKILL.md"), file(body)).unwrap();
    let entry = json!({ "name": "beta", "updatedAt": updated_at, "hash": sha256(file("# Old\n").as_bytes()) });
    let manifest = json!({
        "version": 2, "orgId": "acme", "baseUrl": "https://acme.example", "syncedAt": "x",
        "skills": { id.clone(): entry }, "subscriptions": null,
    });
    std::fs::write(dir.join(MANIFEST_FILE), manifest.to_string()).unwrap();
    id
}

#[derive(Clone)]
struct FakeSkill {
    id: String,
    name: String,
    description: String,
    content: String,
    /// The stored SKILL.md. None for a skill that was written as fields: its document is rendered.
    markdown: Option<String>,
    /// The files other than SKILL.md, by path.
    files: BTreeMap<String, Vec<u8>>,
    collection_id: Option<String>,
    created_at: String,
    updated_at: String,
}

impl FakeSkill {
    fn markdown(&self) -> String {
        self.markdown.clone().unwrap_or_else(|| {
            format!("---\nname: {}\ndescription: {}\n---\n\n{}", self.name, self.description, self.content)
        })
    }

    fn file_list(&self) -> Vec<SkillFile> {
        let digest = |content: &[u8]| format!("sha256:{}", sha256(content));
        let mut files = vec![SkillFile { path: "SKILL.md".into(), digest: digest(self.markdown().as_bytes()) }];
        files
            .extend(self.files.iter().map(|(path, content)| SkillFile { path: path.clone(), digest: digest(content) }));
        files
    }
}

#[derive(Clone)]
struct FakeCollection {
    id: String,
    name: String,
}

struct Registry {
    skills: Vec<FakeSkill>,
    collections: Vec<FakeCollection>,
    counter: u32,
    clock: DateTime<Utc>,
}

pub struct FakeSkillsApi {
    registry: RefCell<Registry>,
    pub calls: RefCell<Vec<String>>,
    /// Removes this skill right after the next listing, as if someone deleted it meanwhile.
    pub remove_after_list: RefCell<Option<String>>,
    /// False for a backend without the file routes (v1.53.5 and older): they answer 404.
    pub file_routes: Cell<bool>,
    /// The connected servers with skills, by slug. The ID of a server is `srvr_<slug>`.
    pub servers: RefCell<BTreeMap<String, FakeServer>>,
    /// What the listing of server skills does.
    pub server_listing: Cell<ServerListing>,
    /// Makes every request for the files of this organization skill fail, as a network error does.
    pub fail_files_of: RefCell<Option<String>>,
    /// Makes the file route answer 400 with this message, as the backend does for a set it refuses.
    pub refuse_files: RefCell<Option<String>>,
    /// Runs at each read of a file, before the answer, with the call as `calls` records it.
    #[allow(clippy::type_complexity)]
    pub on_file_read: RefCell<Option<Box<dyn Fn(&str)>>>,
}

#[derive(Clone, Copy, PartialEq)]
pub enum ServerListing {
    Works,
    /// A backend without the route (v1.53.5 and older) answers 404.
    NoRoute,
    /// A network error or a 5xx.
    Fails,
}

/// A server that publishes skills. Nothing checks a name or a path: the sync must not trust it.
#[derive(Clone, Default)]
pub struct FakeServer {
    /// Each skill by the path of its folder on the server, with its files by path as the URI
    /// writes it.
    pub skills: BTreeMap<String, BTreeMap<String, Vec<u8>>>,
    /// The caller has no credentials: a file read answers the authorize link.
    pub needs_credentials: bool,
    /// What a read answers in place of a file, by URI: content that does not match the listing.
    pub tampered: BTreeMap<String, Vec<u8>>,
}

/// A change made elsewhere; `collection_id: Some(None)` moves the skill to root.
#[derive(Default)]
pub struct Change {
    pub name: Option<String>,
    pub description: Option<String>,
    pub content: Option<String>,
    pub collection_id: Option<Option<String>>,
}

impl Default for FakeSkillsApi {
    fn default() -> Self {
        Self::new()
    }
}

impl FakeSkillsApi {
    pub fn new() -> Self {
        let clock = DateTime::parse_from_rfc3339("2026-09-10T08:00:00.000Z").unwrap().with_timezone(&Utc);
        Self {
            registry: RefCell::new(Registry { skills: Vec::new(), collections: Vec::new(), counter: 0, clock }),
            calls: RefCell::new(Vec::new()),
            remove_after_list: RefCell::new(None),
            file_routes: Cell::new(true),
            servers: RefCell::new(BTreeMap::new()),
            server_listing: Cell::new(ServerListing::Works),
            fail_files_of: RefCell::new(None),
            refuse_files: RefCell::new(None),
            on_file_read: RefCell::new(None),
        }
    }

    fn tick(registry: &mut Registry) -> String {
        registry.clock += Duration::seconds(60);
        registry.clock.to_rfc3339_opts(SecondsFormat::Millis, true)
    }

    pub fn calls(&self) -> Vec<String> {
        self.calls.borrow().clone()
    }

    pub fn clear_calls(&self) {
        self.calls.borrow_mut().clear();
    }

    /// Publishes a skill on a server, or replaces it. The name is the last part of the path.
    pub fn serve(&self, slug: &str, skill_path: &str, files: &[(&str, &[u8])]) {
        let files = files.iter().map(|(path, content)| (path.to_string(), content.to_vec())).collect();
        self.servers.borrow_mut().entry(slug.to_string()).or_default().skills.insert(skill_path.to_string(), files);
    }

    pub fn seed_collection(&self, name: &str) -> Collection {
        let mut registry = self.registry.borrow_mut();
        Self::tick(&mut registry);
        registry.counter += 1;
        let collection = FakeCollection { id: format!("coll_{}", registry.counter), name: name.to_string() };
        registry.collections.push(collection.clone());
        Self::collection_view(&collection)
    }

    pub fn rename_collection(&self, id: &str, name: &str) {
        let mut registry = self.registry.borrow_mut();
        Self::tick(&mut registry);
        if let Some(collection) = registry.collections.iter_mut().find(|collection| collection.id == id) {
            collection.name = name.to_string();
        }
    }

    pub fn remove_collection(&self, id: &str) {
        let mut registry = self.registry.borrow_mut();
        registry.collections.retain(|collection| collection.id != id);
        for skill in registry.skills.iter_mut().filter(|skill| skill.collection_id.as_deref() == Some(id)) {
            skill.collection_id = None;
        }
    }

    pub fn seed(&self, name: &str, content: &str) -> Skill {
        self.seed_in(name, content, None)
    }

    pub fn seed_in(&self, name: &str, content: &str, collection_id: Option<&str>) -> Skill {
        self.insert(name, content, collection_id, None)
    }

    fn insert(&self, name: &str, content: &str, collection_id: Option<&str>, description: Option<&str>) -> Skill {
        let skill = {
            let mut registry = self.registry.borrow_mut();
            let now = Self::tick(&mut registry);
            registry.counter += 1;
            let collection_id =
                collection_id.filter(|id| registry.collections.iter().any(|c| c.id == *id)).map(str::to_string);
            let skill = FakeSkill {
                id: format!("skill_{}", registry.counter),
                name: name.to_string(),
                description: description.map(str::to_string).unwrap_or_else(|| format!("Use for {name}")),
                content: content.to_string(),
                markdown: None,
                files: BTreeMap::new(),
                collection_id,
                created_at: now.clone(),
                updated_at: now,
            };
            registry.skills.push(skill.clone());
            skill
        };
        self.view(&skill)
    }

    pub fn change(&self, id: &str, change: Change) -> Result<Skill> {
        let skill = {
            let mut registry = self.registry.borrow_mut();
            if let Some(Some(collection)) = &change.collection_id
                && !registry.collections.iter().any(|c| &c.id == collection)
            {
                return Err(SkillsError::Api { status: 400, message: "Collection not found".into() }.into());
            }
            let now = Self::tick(&mut registry);
            let Some(skill) = registry.skills.iter_mut().find(|skill| skill.id == id) else {
                return Err(SkillsError::Api { status: 400, message: "Skill not found".into() }.into());
            };
            if let Some(name) = change.name {
                skill.name = name;
            }
            if let Some(description) = change.description {
                skill.description = description;
            }
            if let Some(content) = change.content {
                skill.content = content;
            }
            // A write of fields renders the document again.
            skill.markdown = None;
            if let Some(collection_id) = change.collection_id {
                skill.collection_id = collection_id;
            }
            skill.updated_at = now;
            skill.clone()
        };
        Ok(self.view(&skill))
    }

    pub fn remove(&self, id: &str) {
        self.registry.borrow_mut().skills.retain(|skill| skill.id != id);
    }

    /// Stores a document and files as the file route does, with no path rule: what a server that
    /// the sync must not trust can list. Without SKILL.md in the set, the stored one stays.
    pub fn put_files(&self, id: &str, files: &[(&str, &[u8])]) {
        let mut registry = self.registry.borrow_mut();
        let now = Self::tick(&mut registry);
        let skill = registry.skills.iter_mut().find(|skill| skill.id == id).expect("skill exists");
        skill.files.clear();
        for (path, content) in files {
            if *path == "SKILL.md" {
                let text = String::from_utf8(content.to_vec()).expect("SKILL.md is text");
                let (frontmatter, body) = parse_skill_md(&text).expect("SKILL.md parses");
                (skill.name, skill.description, skill.content) = (frontmatter.name, frontmatter.description, body);
                skill.markdown = Some(text);
            } else {
                skill.files.insert(path.to_string(), content.to_vec());
            }
        }
        skill.updated_at = now;
    }

    pub fn markdown_of(&self, id: &str) -> Option<String> {
        self.registry.borrow().skills.iter().find(|skill| skill.id == id).map(FakeSkill::markdown)
    }

    pub fn files_of(&self, id: &str) -> BTreeMap<String, Vec<u8>> {
        let skill = self.registry.borrow().skills.iter().find(|skill| skill.id == id).cloned();
        skill.map(|skill| skill.files).unwrap_or_default()
    }

    pub fn content_of(&self, id: &str) -> Option<String> {
        self.registry.borrow().skills.iter().find(|skill| skill.id == id).map(|skill| skill.content.clone())
    }

    pub fn find(&self, name: &str) -> Option<Skill> {
        let skill = self.registry.borrow().skills.iter().find(|skill| skill.name == name).cloned();
        skill.map(|skill| self.view(&skill))
    }

    fn collection_view(collection: &FakeCollection) -> Collection {
        Collection {
            id: collection.id.clone(),
            name: collection.name.clone(),
            raw: json!({ "id": collection.id, "name": collection.name }),
        }
    }

    fn view(&self, skill: &FakeSkill) -> Skill {
        let collection_name = skill
            .collection_id
            .as_ref()
            .and_then(|id| self.registry.borrow().collections.iter().find(|c| &c.id == id).map(|c| c.name.clone()));
        Skill {
            id: skill.id.clone(),
            name: skill.name.clone(),
            description: skill.description.clone(),
            updated_at: skill.updated_at.clone(),
            collection_id: skill.collection_id.clone(),
            collection_name: collection_name.clone(),
            raw: json!({
                "id": skill.id,
                "name": skill.name,
                "description": skill.description,
                "visibility": "organization",
                "collectionId": skill.collection_id,
                "collectionName": collection_name,
                "contentBytes": skill.content.len(),
                "createdByUserEmail": "tester@example.com",
                "createdAt": skill.created_at,
                "updatedAt": skill.updated_at,
            }),
        }
    }
}

impl SkillsApi for FakeSkillsApi {
    async fn list(&self, query: Option<&str>, collection: Option<&str>) -> Result<Vec<Skill>> {
        self.calls.borrow_mut().push("list".into());
        let needle = query.map(str::to_lowercase);
        let mut skills: Vec<FakeSkill> = self
            .registry
            .borrow()
            .skills
            .iter()
            .filter(|skill| {
                needle.as_ref().is_none_or(|needle| {
                    skill.name.contains(needle.as_str()) || skill.description.to_lowercase().contains(needle.as_str())
                })
            })
            .cloned()
            .collect();
        skills.sort_by(|a, b| a.name.cmp(&b.name));
        let mut views: Vec<Skill> = skills.iter().map(|skill| self.view(skill)).collect();
        if let Some(collection) = collection {
            views.retain(|skill| skill.collection_name.as_deref() == Some(collection));
        }
        if let Some(id) = self.remove_after_list.borrow_mut().take() {
            self.remove(&id);
        }
        Ok(views)
    }

    async fn list_collections(&self) -> Result<Vec<Collection>> {
        self.calls.borrow_mut().push("listCollections".into());
        let mut collections = self.registry.borrow().collections.clone();
        collections.sort_by(|a, b| a.name.cmp(&b.name));
        Ok(collections.iter().map(Self::collection_view).collect())
    }

    async fn get(&self, id: &str) -> Result<SkillWithContent> {
        self.calls.borrow_mut().push(format!("get {id}"));
        let skill = self.registry.borrow().skills.iter().find(|skill| skill.id == id).cloned();
        match skill {
            Some(skill) => Ok(SkillWithContent {
                skill: self.view(&skill),
                content: skill.content.clone(),
                markdown: skill.markdown(),
            }),
            None => Err(SkillsError::NotFound(id.to_string()).into()),
        }
    }

    async fn create(&self, body: &CreateSkillBody) -> Result<Skill> {
        // A document gives the three fields, as on the backend.
        let parsed = body.markdown.as_deref().map(|text| parse_skill_md(text).expect("SKILL.md parses"));
        let (name, description, content) = match &parsed {
            Some((frontmatter, text)) => {
                (frontmatter.name.clone(), Some(frontmatter.description.as_str()), text.as_str())
            }
            None => (
                body.name.clone().unwrap_or_default(),
                body.description.as_deref(),
                body.content.as_deref().unwrap_or_default(),
            ),
        };
        self.calls.borrow_mut().push(format!("create {name}"));
        if self.registry.borrow().skills.iter().any(|skill| skill.name == name) {
            return Err(SkillsError::Api { status: 400, message: "A skill with this name exists".into() }.into());
        }
        if let Some(collection) = &body.collection_id
            && !self.registry.borrow().collections.iter().any(|c| &c.id == collection)
        {
            return Err(SkillsError::Api { status: 400, message: "Collection not found".into() }.into());
        }
        let created = self.insert(&name, content, body.collection_id.as_deref(), description);
        if let Some(skill) = self.registry.borrow_mut().skills.iter_mut().find(|skill| skill.id == created.id) {
            skill.markdown = body.markdown.clone();
        }
        Ok(created)
    }

    async fn update(&self, id: &str, body: &UpdateSkillBody) -> Result<Skill> {
        self.calls.borrow_mut().push(format!("update {id}"));
        // A move alone keeps the stored document.
        if body.name.is_none() && body.description.is_none() && body.content.is_none() {
            let stored = self.registry.borrow().skills.iter().find(|skill| skill.id == id).cloned();
            let moved =
                self.change(id, Change { collection_id: body.collection_id.clone().map(Some), ..Change::default() })?;
            if let Some(skill) = self.registry.borrow_mut().skills.iter_mut().find(|skill| skill.id == id) {
                skill.markdown = stored.and_then(|stored| stored.markdown);
            }
            return Ok(moved);
        }
        self.change(
            id,
            Change {
                name: body.name.clone(),
                description: body.description.clone(),
                content: body.content.clone(),
                collection_id: body.collection_id.clone().map(Some),
            },
        )
    }

    async fn list_files(&self, id: &str) -> Result<Option<Vec<SkillFile>>> {
        self.calls.borrow_mut().push(format!("listFiles {id}"));
        if self.fail_files_of.borrow().as_deref() == Some(id) {
            anyhow::bail!("connection reset");
        }
        if !self.file_routes.get() {
            return Ok(None);
        }
        match self.registry.borrow().skills.iter().find(|skill| skill.id == id) {
            Some(skill) => Ok(Some(skill.file_list())),
            None => Err(SkillsError::NotFound(id.to_string()).into()),
        }
    }

    async fn get_file(&self, id: &str, path: &str) -> Result<Vec<u8>> {
        self.calls.borrow_mut().push(format!("getFile {id} {path}"));
        if let Some(hook) = self.on_file_read.borrow().as_ref() {
            hook(&format!("getFile {id} {path}"));
        }
        let skill = self.registry.borrow().skills.iter().find(|skill| skill.id == id).cloned();
        let content = skill.and_then(|skill| match path {
            "SKILL.md" => Some(skill.markdown().into_bytes()),
            path => skill.files.get(path).cloned(),
        });
        content.ok_or_else(|| SkillsError::NotFound(id.to_string()).into())
    }

    async fn replace_files(&self, id: &str, files: &[(String, Vec<u8>)]) -> Result<Option<String>> {
        self.calls.borrow_mut().push(format!("replaceFiles {id}"));
        if !self.file_routes.get() {
            return Ok(None);
        }
        if files.iter().any(|(path, _)| path.to_lowercase().ends_with("/skill.md")) {
            let message = "A file named SKILL.md is allowed only at the root of the skill".to_string();
            return Err(SkillsError::Api { status: 400, message }.into());
        }
        if let Some(message) = self.refuse_files.borrow().clone() {
            return Err(SkillsError::Api { status: 400, message }.into());
        }
        let files: Vec<(&str, &[u8])> =
            files.iter().map(|(path, content)| (path.as_str(), content.as_slice())).collect();
        self.put_files(id, &files);
        let skill = self.registry.borrow().skills.iter().find(|skill| skill.id == id).cloned();
        Ok(skill.map(|skill| skill.updated_at))
    }

    async fn list_server_skills(&self) -> Result<Option<Vec<ServerSkill>>> {
        self.calls.borrow_mut().push("listServerSkills".into());
        match self.server_listing.get() {
            ServerListing::Works => {}
            ServerListing::NoRoute => return Ok(None),
            ServerListing::Fails => anyhow::bail!("502 Bad Gateway"),
        }
        let mut listing = Vec::new();
        for (slug, server) in self.servers.borrow().iter() {
            for (skill_path, files) in &server.skills {
                listing.push(ServerSkill {
                    server_id: format!("srvr_{slug}"),
                    server_slug: slug.clone(),
                    uri: format!("skill://{skill_path}/SKILL.md"),
                    name: skill_path.rsplit('/').next().unwrap_or_default().to_string(),
                    files: files
                        .iter()
                        .map(|(path, content)| ServerSkillFile {
                            path: path.clone(),
                            digest: format!("sha256:{}", sha256(content)),
                            uri: format!("skill://{skill_path}/{path}"),
                        })
                        .collect(),
                });
            }
        }
        Ok(Some(listing))
    }

    async fn get_server_skill_file(&self, server_slug: &str, uri: &str) -> Result<Vec<u8>> {
        self.calls.borrow_mut().push(format!("getServerFile {server_slug} {uri}"));
        if let Some(hook) = self.on_file_read.borrow().as_ref() {
            hook(&format!("getServerFile {server_slug} {uri}"));
        }
        let servers = self.servers.borrow();
        let unknown = || SkillsError::Api { status: 400, message: "Skill file does not exist".into() };
        let server = servers.get(server_slug).ok_or_else(unknown)?;
        if server.needs_credentials {
            let authorize_url = format!("https://acme.example/authorize/{server_slug}");
            let message = format!(
                "Server \"{server_slug}\" needs authorization to read skills. Open {authorize_url} to authorize, then try again."
            );
            return Err(SkillsError::NeedsCredentials { message, authorize_url: Some(authorize_url) }.into());
        }
        if let Some(content) = server.tampered.get(uri) {
            return Ok(content.clone());
        }
        let found = server
            .skills
            .iter()
            .find_map(|(skill_path, files)| files.get(uri.strip_prefix(&format!("skill://{skill_path}/"))?));
        Ok(found.ok_or_else(unknown)?.clone())
    }
}
