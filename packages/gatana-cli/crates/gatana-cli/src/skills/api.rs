//! The skill operations sync and push use. A trait rather than the generated client so the tests
//! run against an in-memory registry; the real one is a thin wrapper over `gatana_api::v1`.

use anyhow::Result;
use gatana_api::v1::{query, types};
use serde_json::Value;

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
}

/// The skills API of an organization.
pub struct HttpSkillsApi<'a> {
    client: &'a gatana_api::Client,
    /// For messages, as configured.
    base_url: String,
}

impl<'a> HttpSkillsApi<'a> {
    pub fn new(client: &'a gatana_api::Client, base_url: &str) -> Self {
        Self { client, base_url: base_url.to_string() }
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
}

fn skill_from_dto(dto: types::SkillDto, raw: Value) -> Skill {
    Skill {
        id: dto.id,
        name: dto.name,
        description: dto.description,
        updated_at: dto.updated_at,
        collection_id: dto.collection_id,
        collection_name: dto.collection_name,
        raw,
    }
}

impl SkillsApi for HttpSkillsApi<'_> {
    async fn list(&self, text: Option<&str>, collection: Option<&str>) -> Result<Vec<Skill>> {
        let params = query::ListSkills {
            query: text.map(str::trim).filter(|text| !text.is_empty()).map(str::to_string),
            collection: collection.filter(|name| !name.is_empty()).map(str::to_string),
        };
        let response = self.client.v1().list_skills(&params).send().await.map_err(|error| self.fail(error))?;
        let typed = response.typed()?;
        let raw = response.value.get("skills").and_then(Value::as_array).cloned().unwrap_or_default();
        Ok(typed.skills.into_iter().zip(raw).map(|(dto, raw)| skill_from_dto(dto, raw)).collect())
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
        let response = match self.client.v1().get_skill(id).send().await {
            Ok(response) => response,
            Err(gatana_api::Error::Status { status, message, .. })
                if status.as_u16() == 404 || (status.as_u16() == 400 && message == "Skill not found") =>
            {
                // The service reports a missing or unreadable skill as 400 "Skill not found".
                return Err(SkillsError::NotFound(id.to_string()).into());
            }
            Err(error) => return Err(self.fail(error)),
        };
        let dto = response.typed()?;
        Ok(SkillWithContent {
            skill: Skill {
                id: dto.id,
                name: dto.name,
                description: dto.description,
                updated_at: dto.updated_at,
                collection_id: dto.collection_id,
                collection_name: dto.collection_name,
                raw: response.value.clone(),
            },
            content: dto.content,
        })
    }

    async fn create(&self, body: &types::CreateSkillBody) -> Result<Skill> {
        let response = self.client.v1().create_skill(body).send().await.map_err(|error| self.fail(error))?;
        Ok(skill_from_dto(response.typed()?, response.value))
    }

    async fn update(&self, id: &str, body: &types::UpdateSkillBody) -> Result<Skill> {
        let response = self.client.v1().update_skill(id, body).send().await.map_err(|error| self.fail(error))?;
        Ok(skill_from_dto(response.typed()?, response.value))
    }
}
