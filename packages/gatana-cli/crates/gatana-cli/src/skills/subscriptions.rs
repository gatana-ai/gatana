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
/// narrows the search to one namespace.
pub async fn resolve_subscription(
    api: &impl SkillsApi,
    name: &str,
    kind: Option<SubscriptionKind>,
) -> Result<Subscription> {
    let wanted = name.trim();
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
            bail!("\"{wanted}\" is both a collection and a skill. Say which: --collection or --skill")
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
                "No {what} named \"{wanted}\". Collections you can see: {}. Skills: \"gatana skills ls\"",
                collections.join(", ")
            )
        }
    }
}
