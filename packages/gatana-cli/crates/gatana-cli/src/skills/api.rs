//! The skill operations sync and push use. A trait rather than the generated client so the tests
//! run against an in-memory registry; the real one is a thin wrapper over `gatana_api::v1`.

use anyhow::Result;
use base64::Engine;
use base64::engine::general_purpose::STANDARD;
use gatana_api::v1::{query, types};
use serde::Deserialize;
use serde_json::Value;
use std::sync::atomic::{AtomicBool, Ordering};

/// A skill as listed: what sync and push act on, plus the record as the server sent it for output.
#[derive(Clone, Debug)]
pub struct Skill {
    pub id: String,
    pub name: String,
    pub description: String,
    pub updated_at: String,
    pub collection_id: Option<String>,
    pub collection_name: Option<String>,
    pub raw: Value,
}

#[derive(Clone, Debug)]
pub struct SkillWithContent {
    pub skill: Skill,
    /// The Markdown body, without frontmatter.
    pub content: String,
    /// The whole SKILL.md. A server with file routes stores it and returns it byte for byte; an older
    /// one renders it from the name, the description and the body.
    pub markdown: String,
}

/// A file of a skill as the server lists it. The digest is `sha256:` and the hash in hex.
#[derive(Clone, Debug)]
pub struct SkillFile {
    pub path: String,
    pub digest: String,
}

/// A skill that a connected MCP server publishes, as Gatana caches it.
#[derive(Clone, Debug)]
pub struct ServerSkill {
    pub server_id: String,
    pub server_slug: String,
    /// The URI of the SKILL.md as the server publishes it. With the server ID it identifies the skill.
    pub uri: String,
    pub name: String,
    pub files: Vec<ServerSkillFile>,
}

#[derive(Clone, Debug)]
pub struct ServerSkillFile {
    /// The path in the skill folder, as the URI writes it: percent-encoded.
    pub path: String,
    pub digest: String,
    /// What the file route reads the file by.
    pub uri: String,
}

#[derive(Clone, Debug)]
pub struct Collection {
    pub id: String,
    pub name: String,
    pub raw: Value,
}

#[derive(Debug, thiserror::Error)]
pub enum SkillsError {
    /// The skill is gone or the caller may not read it.
    #[error("Skill {0} not found")]
    NotFound(String),
    #[error("{message}")]
    Api { status: u16, message: String },
    /// The caller has no credentials for the server of a skill file. The link stores them, when
    /// the caller may set them.
    #[error("{message}")]
    NeedsCredentials { message: String, authorize_url: Option<String> },
}

/// True when the error says the skill does not exist (any more) for this caller.
pub fn is_not_found(error: &anyhow::Error) -> bool {
    matches!(error.downcast_ref::<SkillsError>(), Some(SkillsError::NotFound(_)))
}

#[allow(async_fn_in_trait)]
pub trait SkillsApi {
    /// Every skill the caller can read, without bodies; narrowed by a text and/or to one collection.
    async fn list(&self, query: Option<&str>, collection: Option<&str>) -> Result<Vec<Skill>>;
    /// Every collection the caller can see.
    async fn list_collections(&self) -> Result<Vec<Collection>>;
    /// One skill with its body. Fails with `SkillsError::NotFound` when it is gone or not readable.
    async fn get(&self, id: &str) -> Result<SkillWithContent>;
    async fn create(&self, body: &types::CreateSkillBody) -> Result<Skill>;
    async fn update(&self, id: &str, body: &types::UpdateSkillBody) -> Result<Skill>;
    /// Every file of a skill, SKILL.md included. None when the server has no file routes: backend
    /// v1.53.5 and older store only the SKILL.md.
    async fn list_files(&self, id: &str) -> Result<Option<Vec<SkillFile>>>;
    /// The bytes of one file. Fails with `SkillsError::NotFound` when the skill or the file is gone.
    async fn get_file(&self, id: &str, path: &str) -> Result<Vec<u8>>;
    /// Replaces the files of a skill with this set in one transaction. Without SKILL.md in the set,
    /// the stored one stays. Answers the `updatedAt` of the skill as the write left it. None when the
    /// server has no file routes.
    async fn replace_files(&self, id: &str, files: &[(String, Vec<u8>)]) -> Result<Option<String>>;
    /// The skills of every connected server that the caller can use, without content. None when the
    /// server has no such route: every backend up to v1.53.5.
    async fn list_server_skills(&self) -> Result<Option<Vec<ServerSkill>>>;
    /// The bytes of one file of a server skill. Gatana reads it from the server with the credentials
    /// of the caller and verifies it. Fails with `SkillsError::NeedsCredentials` without credentials.
    async fn get_server_skill_file(&self, server_slug: &str, uri: &str) -> Result<Vec<u8>>;
}

/// The skills API of an organization.
pub struct HttpSkillsApi<'a> {
    client: &'a gatana_api::Client,
    /// For messages, as configured.
    base_url: String,
    /// Set by the first 404 of a file route, so that a sync asks an older server once, not per skill.
    no_file_routes: AtomicBool,
}

impl<'a> HttpSkillsApi<'a> {
    pub fn new(client: &'a gatana_api::Client, base_url: &str) -> Self {
        Self { client, base_url: base_url.to_string(), no_file_routes: AtomicBool::new(false) }
    }

    fn fail(&self, error: gatana_api::Error) -> anyhow::Error {
        match error {
            gatana_api::Error::Status { status, url, message, .. } => {
                // A server without the skills routes answers 404 for the collection itself.
                let path = url.path();
                if status.as_u16() == 404 && (path.ends_with("/skills") || path.ends_with("/skill-collections")) {
                    return SkillsError::Api {
                        status: 404,
                        message: format!("Skills are not available on {}: update the server", self.base_url),
                    }
                    .into();
                }
                SkillsError::Api { status: status.as_u16(), message }.into()
            }
            other => other.into(),
        }
    }

    /// What a failed file route means: a 404 is a server without the route, and the service reports
    /// a missing or unreadable skill or file as a 400.
    fn file_route_failed<T>(&self, id: &str, error: gatana_api::Error) -> Result<Option<T>> {
        match error {
            gatana_api::Error::Status { status, .. } if status.as_u16() == 404 => {
                self.no_file_routes.store(true, Ordering::Relaxed);
                Ok(None)
            }
            gatana_api::Error::Status { status, message, .. }
                if status.as_u16() == 400
                    && (message == "Skill not found" || message == "Skill file does not exist") =>
            {
                Err(SkillsError::NotFound(id.to_string()).into())
            }
            error => Err(self.fail(error)),
        }
    }
}

/// The fields of a skill that sync and push decide on. Read from the JSON, not through the generated
/// `SkillDto`: that type requires every field of the newest backend, and an older one sends fewer.
#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct SkillFields {
    id: String,
    name: String,
    description: String,
    updated_at: String,
    collection_id: Option<String>,
    collection_name: Option<String>,
}

fn skill_from_json(raw: Value) -> Result<Skill> {
    let fields: SkillFields = serde_json::from_value(raw.clone())?;
    Ok(Skill {
        id: fields.id,
        name: fields.name,
        description: fields.description,
        updated_at: fields.updated_at,
        collection_id: fields.collection_id,
        collection_name: fields.collection_name,
        raw,
    })
}

fn files_from_dto(files: Vec<types::SkillFileDto>) -> Vec<SkillFile> {
    files.into_iter().map(|file| SkillFile { path: file.path, digest: file.digest }).collect()
}

impl SkillsApi for HttpSkillsApi<'_> {
    async fn list(&self, text: Option<&str>, collection: Option<&str>) -> Result<Vec<Skill>> {
        let params = query::ListSkills {
            query: text.map(str::trim).filter(|text| !text.is_empty()).map(str::to_string),
            collection: collection.filter(|name| !name.is_empty()).map(str::to_string),
        };
        let response = self.client.v1().list_skills(&params).value().await.map_err(|error| self.fail(error))?;
        let raw = response.get("skills").and_then(Value::as_array).cloned().unwrap_or_default();
        raw.into_iter().map(skill_from_json).collect()
    }

    async fn list_collections(&self) -> Result<Vec<Collection>> {
        let response = self.client.v1().list_skill_collections().send().await.map_err(|error| self.fail(error))?;
        let typed = response.typed()?;
        let raw = response.value.get("collections").and_then(Value::as_array).cloned().unwrap_or_default();
        Ok(typed
            .collections
            .into_iter()
            .zip(raw)
            .map(|(dto, raw)| Collection { id: dto.id, name: dto.name, raw })
            .collect())
    }

    async fn get(&self, id: &str) -> Result<SkillWithContent> {
        let response = match self.client.v1().get_skill(id).value().await {
            Ok(response) => response,
            Err(gatana_api::Error::Status { status, message, .. })
                if status.as_u16() == 404 || (status.as_u16() == 400 && message == "Skill not found") =>
            {
                // The service reports a missing or unreadable skill as 400 "Skill not found".
                return Err(SkillsError::NotFound(id.to_string()).into());
            }
            Err(error) => return Err(self.fail(error)),
        };
        let text = |key: &str| response.get(key).and_then(Value::as_str).unwrap_or_default().to_string();
        Ok(SkillWithContent { content: text("content"), markdown: text("markdown"), skill: skill_from_json(response)? })
    }

    async fn create(&self, body: &types::CreateSkillBody) -> Result<Skill> {
        skill_from_json(self.client.v1().create_skill(body).value().await.map_err(|error| self.fail(error))?)
    }

    async fn update(&self, id: &str, body: &types::UpdateSkillBody) -> Result<Skill> {
        skill_from_json(self.client.v1().update_skill(id, body).value().await.map_err(|error| self.fail(error))?)
    }

    async fn list_files(&self, id: &str) -> Result<Option<Vec<SkillFile>>> {
        if self.no_file_routes.load(Ordering::Relaxed) {
            return Ok(None);
        }
        match self.client.v1().list_skill_files(id).typed().await {
            Ok(response) => Ok(Some(files_from_dto(response.files))),
            Err(error) => self.file_route_failed(id, error),
        }
    }

    async fn get_file(&self, id: &str, path: &str) -> Result<Vec<u8>> {
        let file = match self.client.v1().get_skill_file(id, path).typed().await {
            Ok(response) => response.file,
            // The listing came first, so a 404 here is a path that the route does not match.
            Err(gatana_api::Error::Status { status, .. }) if status.as_u16() == 404 => {
                return Err(SkillsError::NotFound(id.to_string()).into());
            }
            Err(error) => return self.file_route_failed::<()>(id, error).map(|_| Vec::new()),
        };
        match file.encoding {
            types::GetSkillFileResponseFileEncoding::Utf8 => Ok(file.content.into_bytes()),
            types::GetSkillFileResponseFileEncoding::Base64 => Ok(STANDARD.decode(file.content)?),
        }
    }

    async fn replace_files(&self, id: &str, files: &[(String, Vec<u8>)]) -> Result<Option<String>> {
        if self.no_file_routes.load(Ordering::Relaxed) {
            return Ok(None);
        }
        let files = files
            .iter()
            .map(|(path, content)| match std::str::from_utf8(content) {
                Ok(text) => types::ReplaceSkillFilesBodyFilesItem {
                    path: path.clone(),
                    content: text.to_string(),
                    encoding: types::ReplaceSkillFilesBodyFilesItemEncoding::Utf8,
                },
                Err(_) => types::ReplaceSkillFilesBodyFilesItem {
                    path: path.clone(),
                    content: STANDARD.encode(content),
                    encoding: types::ReplaceSkillFilesBodyFilesItemEncoding::Base64,
                },
            })
            .collect();
        match self.client.v1().replace_skill_files(id, &types::ReplaceSkillFilesBody { files }).typed().await {
            Ok(response) => Ok(Some(response.updated_at)),
            Err(error) => self.file_route_failed(id, error),
        }
    }

    async fn list_server_skills(&self) -> Result<Option<Vec<ServerSkill>>> {
        let response = match self.client.v1().list_server_skills().typed().await {
            Ok(response) => response,
            Err(gatana_api::Error::Status { status, .. }) if status.as_u16() == 404 => return Ok(None),
            Err(error) => return Err(self.fail(error)),
        };
        let skills = response.skills.into_iter().map(|skill| ServerSkill {
            server_id: skill.server_id,
            server_slug: skill.server_slug,
            uri: skill.uri,
            name: skill.name,
            files: skill
                .files
                .into_iter()
                .map(|file| ServerSkillFile { path: file.path, digest: file.digest, uri: file.uri })
                .collect(),
        });
        Ok(Some(skills.collect()))
    }

    async fn get_server_skill_file(&self, server_slug: &str, uri: &str) -> Result<Vec<u8>> {
        let response = self
            .client
            .v1()
            .get_mcp_server_skill_file(server_slug, uri)
            .typed()
            .await
            .map_err(|error| self.fail(error))?;
        let Some(file) = response.file else {
            let (message, authorize_url) = match response.credential_prompt {
                Some(prompt) => (prompt.message, prompt.authorize_url),
                None => (format!("Server \"{server_slug}\" returned no file"), None),
            };
            return Err(SkillsError::NeedsCredentials { message, authorize_url }.into());
        };
        match file.encoding {
            types::GetMcpServerSkillFileResponseFileEncoding::Utf8 => Ok(file.content.into_bytes()),
            types::GetMcpServerSkillFileResponseFileEncoding::Base64 => Ok(STANDARD.decode(file.content)?),
        }
    }
}
