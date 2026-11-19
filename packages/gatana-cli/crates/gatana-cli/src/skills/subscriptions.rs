//! What a name given to `gatana skills install` points at.

use super::api::SkillsApi;
use super::manifest::{Subscription, SubscriptionKind};
use anyhow::{Result, bail};

/// Describes a subscription for messages: `collection release`, `skill deploy`.
pub fn describe_subscription(subscription: &Subscription) -> String {
    format!("{} {}", subscription.kind.as_str(), subscription.name)
}

/// A collection, or a skill. Collections and skills are named in separate namespaces, so one name
/// may exist in both; then the caller has to say which, rather than the CLI guessing. `kind`
/// narrows the search to one namespace. A server is found only when the caller asks for one: a
/// directory then takes every skill that the server publishes.
pub async fn resolve_subscription(
    api: &impl SkillsApi,
    name: &str,
    kind: Option<SubscriptionKind>,
) -> Result<Subscription> {
    let wanted = name.trim();
    if kind == Some(SubscriptionKind::Server) {
        let Some(listing) = api.list_server_skills().await? else {
            bail!("This Gatana server does not give the skills of MCP servers to the CLI: update the server");
        };
        let Some(found) = listing.iter().find(|skill| skill.server_slug == wanted) else {
            let mut slugs: Vec<&str> = listing.iter().map(|skill| skill.server_slug.as_str()).collect();
            slugs.sort();
            slugs.dedup();
            if slugs.is_empty() {
                bail!("No MCP server publishes skills that you can use");
            }
            bail!(
                "No MCP server \"{wanted}\" publishes skills that you can use. Servers with skills: {}",
                slugs.join(", ")
            );
        };
        return Ok(Subscription {
            kind: SubscriptionKind::Server,
            id: found.server_id.clone(),
            name: found.server_slug.clone(),
        });
    }
    let collection = match kind {
        Some(SubscriptionKind::Skill) => None,
        _ => api.list_collections().await?.into_iter().find(|candidate| candidate.name == wanted),
    };
    let skill = match kind {
        Some(SubscriptionKind::Collection) => None,
        _ => api.list(None, None).await?.into_iter().find(|candidate| candidate.name == wanted),
    };
    match (collection, skill) {
        (Some(_), Some(_)) => {
            bail!("\"{wanted}\" is both a collection and a skill. Choose one with --collection or --skill")
        }
        (Some(collection), None) => {
            Ok(Subscription { kind: SubscriptionKind::Collection, id: collection.id, name: collection.name })
        }
        (None, Some(skill)) => Ok(Subscription { kind: SubscriptionKind::Skill, id: skill.id, name: skill.name }),
        (None, None) => {
            let mut collections: Vec<String> = match kind {
                Some(SubscriptionKind::Skill) => Vec::new(),
                _ => api.list_collections().await?.into_iter().map(|collection| collection.name).collect(),
            };
            collections.sort();
            let what = kind.map(SubscriptionKind::as_str).unwrap_or("collection or skill");
            if collections.is_empty() {
                bail!("No {what} named \"{wanted}\". See \"gatana skills ls\" and \"gatana skills ls --collections\"");
            }
            bail!(
                "No {what} named \"{wanted}\". Available collections: {}. Skills: \"gatana skills ls\"",
                collections.join(", ")
            )
        }
    }
}
