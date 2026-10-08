//! An in-memory skills registry with the rules of the backend that matter to sync, push and
//! following collections.

#![allow(dead_code)]

use anyhow::Result;
use chrono::{DateTime, Duration, SecondsFormat, Utc};
use gatana_api::v1::types::{CreateSkillBody, UpdateSkillBody};
use gatana_cli::skills::api::{Collection, Skill, SkillWithContent, SkillsApi, SkillsError};
use serde_json::json;
use std::cell::RefCell;

#[derive(Clone)]
struct FakeSkill {
    id: String,
    name: String,
    description: String,
    content: String,
    collection_id: Option<String>,
    created_at: String,
    updated_at: String,
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
            Some(skill) => Ok(SkillWithContent { skill: self.view(&skill), content: skill.content.clone() }),
            None => Err(SkillsError::NotFound(id.to_string()).into()),
        }
    }

    async fn create(&self, body: &CreateSkillBody) -> Result<Skill> {
        let name = body.name.clone().unwrap_or_default();
        self.calls.borrow_mut().push(format!("create {name}"));
        if self.registry.borrow().skills.iter().any(|skill| skill.name == name) {
            return Err(SkillsError::Api { status: 400, message: "A skill with this name exists".into() }.into());
        }
        if let Some(collection) = &body.collection_id
            && !self.registry.borrow().collections.iter().any(|c| &c.id == collection)
        {
            return Err(SkillsError::Api { status: 400, message: "Collection not found".into() }.into());
        }
        Ok(self.insert(
            &name,
            body.content.as_deref().unwrap_or_default(),
            body.collection_id.as_deref(),
            body.description.as_deref(),
        ))
    }

    async fn update(&self, id: &str, body: &UpdateSkillBody) -> Result<Skill> {
        self.calls.borrow_mut().push(format!("update {id}"));
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
}
