//! Profiles: the profile itself through get, describe, create, patch and delete, and what it holds
//! and who has it through "gatana profile".

use super::{array_at, resolve, text_at};
use crate::cli::{ClaimCommand, CreateProfileArgs, MaintainerCommand, ProfileCommand, ProfileMember};
use crate::context::Context;
use crate::output::{self, Column, Options};
use crate::util::format_age;
use anyhow::{Result, anyhow, bail};
use gatana_api::v1::{self, query};
use serde_json::{Value, json};

const PROFILE_COLUMNS: [Column; 8] = [
    Column::path("Name", "name"),
    Column::path("Open To All", "isOpenToAllUsers"),
    Column::path("Restrictive", "isRestrictive"),
    Column::path("Code Mode", "isCodeModeForced"),
    Column::path("Servers", "numServers"),
    Column::path("Users", "numAssignedUsers"),
    Column::path("Teams", "numAssignedTeams"),
    Column::computed("Age", |row| json!(format_age(row.get("createdAt")))),
];

fn name_of(profile: &Value) -> &str {
    text_at(profile, "/name").unwrap_or_default()
}

pub async fn get(context: &Context, name: Option<&str>, server: Option<String>) -> Result<()> {
    let api = context.api().await?;
    let Some(name) = name else {
        let list = api.v1().list_profiles(&query::ListProfiles { server_slug: server }).value().await?;
        output::output(&json!({ "profiles": array_at(&list, "profiles") }), Options::columns(&PROFILE_COLUMNS));
        return Ok(());
    };
    let profile = resolve::profile(api, name).await?;
    let details = api.v1().get_profile(resolve::id(&profile)).value().await?;
    output::output(details.get("profile").unwrap_or(&details), Options::yaml());
    Ok(())
}

/// The profile with everyone who has it or maintains it.
pub async fn describe(context: &Context, name: &str) -> Result<()> {
    let api = context.api().await?;
    let id = resolve::id(&resolve::profile(api, name).await?).to_string();
    let details = api.v1().get_profile(&id).value().await?;
    let assignments = api.v1().list_profile_direct_assignments(&id).value().await?;
    let maintainers = api.v1().list_profile_maintainers(&id).value().await?;
    let mappings = api.v1().list_profile_claim_mappings(&id).value().await?;

    let member = |row: &Value, label: &str| json!({ label: row.get(label), "locked": row.get("isLockedByOrgOwner") });
    let shown = json!({
        "profile": details.get("profile").unwrap_or(&details),
        "accounts": array_at(&assignments, "accounts").iter().map(|row| member(row, "email")).collect::<Vec<_>>(),
        "teams": array_at(&assignments, "teams").iter().map(|row| member(row, "name")).collect::<Vec<_>>(),
        "maintainers": array_at(&maintainers, "maintainers").iter().filter_map(|row| row.get("email").cloned()).collect::<Vec<_>>(),
        "claimMappings": array_at(&mappings, "claimMappings").iter().map(claim_text).collect::<Vec<_>>(),
    });
    output::output(&shown, Options::yaml());
    Ok(())
}

fn claim_text(mapping: &Value) -> Value {
    json!(format!(
        "{}={}",
        text_at(mapping, "/claimKey").unwrap_or_default(),
        text_at(mapping, "/claimValue").unwrap_or_default()
    ))
}

pub async fn create(context: &Context, args: CreateProfileArgs) -> Result<()> {
    let api = context.api().await?;
    let body = v1::types::CreateProfileBody {
        name: args.name.clone(),
        description: args.description,
        is_open_to_all_users: args.open_to_all,
        is_restrictive: args.restrictive,
        is_code_mode_forced: Some(args.code_mode),
    };
    let created = api.v1().create_profile(&body).value().await?;
    let id = text_at(&created, "/profile/id").ok_or_else(|| anyhow!("The created profile has no id"))?.to_string();
    // A new profile holds no servers: the create operation takes none
    if !args.servers.is_empty() {
        set_servers(api, &id, &args.servers).await?;
    }
    if output::machine_readable() {
        output::print(&api.v1().get_profile(&id).value().await?);
        return Ok(());
    }
    let with = if args.servers.is_empty() { String::new() } else { format!(" with {}", args.servers.join(", ")) };
    output::success(&format!("Created profile '{}'{with}.", args.name));
    output::println(&format!(
        "Give it to someone: gatana profile assign '{}' --account <email> | --team <name>",
        args.name
    ));
    Ok(())
}

pub async fn patch(context: &Context, name: &str, body: Value) -> Result<()> {
    let api = context.api().await?;
    let profile = resolve::profile(api, name).await?;
    // Every field of the update is optional, so the keys left out keep their values
    api.v1().update_profile_raw(resolve::id(&profile), body).send().await?;
    output::success(&format!("Updated profile '{}'.", name_of(&profile)));
    Ok(())
}

pub async fn delete(context: &Context, name: &str) -> Result<()> {
    let api = context.api().await?;
    let profile = resolve::profile(api, name).await?;
    api.v1().delete_profile(resolve::id(&profile)).send().await?;
    output::success(&format!("Deleted profile '{}'.", name_of(&profile)));
    Ok(())
}

/// Replaces the servers of a profile. Sent raw: the generated body leaves out an empty list, and an
/// empty list is how the last server leaves.
async fn set_servers(api: &gatana_api::Client, profile_id: &str, slugs: &[String]) -> Result<()> {
    api.v1().update_profile_raw(profile_id, json!({ "serverIds": slugs })).send().await?;
    Ok(())
}

/// The slugs of the servers in a profile.
async fn server_slugs(api: &gatana_api::Client, profile_id: &str) -> Result<Vec<String>> {
    let details = api.v1().get_profile(profile_id).value().await?;
    Ok(details
        .pointer("/profile/servers")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(|server| text_at(server, "/slug").map(str::to_string))
        .collect())
}

pub async fn run(context: &Context, command: ProfileCommand) -> Result<()> {
    let api = context.api().await?;
    match command {
        ProfileCommand::AddServer { profile, servers } => {
            let profile = resolve::profile(api, &profile).await?;
            let id = resolve::id(&profile);
            let mut slugs = server_slugs(api, id).await?;
            let added: Vec<String> = servers.into_iter().filter(|slug| !slugs.contains(slug)).collect();
            if added.is_empty() {
                output::success(&format!("Profile '{}' already holds these servers.", name_of(&profile)));
                return Ok(());
            }
            slugs.extend(added.iter().cloned());
            set_servers(api, id, &slugs).await?;
            output::success(&format!("Added {} to profile '{}'.", added.join(", "), name_of(&profile)));
        }
        ProfileCommand::RemoveServer { profile, servers } => {
            let profile = resolve::profile(api, &profile).await?;
            let id = resolve::id(&profile);
            let slugs = server_slugs(api, id).await?;
            if let Some(missing) = servers.iter().find(|slug| !slugs.contains(slug)) {
                bail!("Server '{missing}' is not in profile '{}'.", name_of(&profile));
            }
            let kept: Vec<String> = slugs.into_iter().filter(|slug| !servers.contains(slug)).collect();
            set_servers(api, id, &kept).await?;
            output::success(&format!("Removed {} from profile '{}'.", servers.join(", "), name_of(&profile)));
        }
        ProfileCommand::Assign { profile, member, lock } => {
            let profile = resolve::profile(api, &profile).await?;
            let profile_id = resolve::id(&profile).to_string();
            let is_locked_by_org_owner = lock.then_some(true);
            let who = match member_of(api, &member).await? {
                Member::Account(account) => {
                    let body = v1::types::CreateUserProfileAssignmentRequest { profile_id, is_locked_by_org_owner };
                    api.v1().create_user_profile(resolve::id(&account), &body).send().await?;
                    format!("account '{}'", text_at(&account, "/email").unwrap_or_default())
                }
                Member::Team(team) => {
                    let body = v1::types::CreateTeamProfileAssignmentRequest { profile_id, is_locked_by_org_owner };
                    api.v1().create_team_profile(resolve::id(&team), &body).send().await?;
                    format!("team '{}'", name_of(&team))
                }
            };
            output::success(&format!("Gave profile '{}' to {who}.", name_of(&profile)));
        }
        ProfileCommand::Unassign { profile, member } => {
            let profile = resolve::profile(api, &profile).await?;
            let profile_id = resolve::id(&profile);
            let who = match member_of(api, &member).await? {
                Member::Account(account) => {
                    api.v1().delete_user_profile(resolve::id(&account), profile_id).send().await?;
                    format!("account '{}'", text_at(&account, "/email").unwrap_or_default())
                }
                Member::Team(team) => {
                    api.v1().delete_team_profile(resolve::id(&team), profile_id).send().await?;
                    format!("team '{}'", name_of(&team))
                }
            };
            output::success(&format!("Took profile '{}' from {who}.", name_of(&profile)));
        }
        ProfileCommand::Maintainers { command } => match command {
            MaintainerCommand::Add { profile, account } => {
                let profile = resolve::profile(api, &profile).await?;
                let account = resolve::account(api, &account).await?;
                let body = v1::types::CreateProfileMaintainerBody { user_id: resolve::id(&account).to_string() };
                api.v1().create_profile_maintainer(resolve::id(&profile), &body).send().await?;
                output::success(&format!(
                    "'{}' now maintains profile '{}'.",
                    text_at(&account, "/email").unwrap_or_default(),
                    name_of(&profile)
                ));
            }
            MaintainerCommand::Rm { profile, account } => {
                let profile = resolve::profile(api, &profile).await?;
                let account = resolve::account(api, &account).await?;
                api.v1().delete_profile_maintainer(resolve::id(&profile), resolve::id(&account)).send().await?;
                output::success(&format!(
                    "'{}' no longer maintains profile '{}'.",
                    text_at(&account, "/email").unwrap_or_default(),
                    name_of(&profile)
                ));
            }
        },
        ProfileCommand::Claims { command } => match command {
            ClaimCommand::Add { profile, claim } => {
                let (claim_key, claim_value) = split_claim(&claim)?;
                let profile = resolve::profile(api, &profile).await?;
                let body = v1::types::CreateProfileClaimMappingBody { claim_key, claim_value };
                api.v1().create_profile_claim_mapping(resolve::id(&profile), &body).send().await?;
                output::success(&format!("Everyone with the claim {claim} now gets profile '{}'.", name_of(&profile)));
            }
            ClaimCommand::Rm { profile, claim } => {
                let (key, value) = split_claim(&claim)?;
                let profile = resolve::profile(api, &profile).await?;
                let id = resolve::id(&profile);
                let mappings = array_at(&api.v1().list_profile_claim_mappings(id).value().await?, "claimMappings");
                let Some(mapping) = mappings.iter().find(|mapping| {
                    text_at(mapping, "/claimKey") == Some(key.as_str())
                        && text_at(mapping, "/claimValue") == Some(value.as_str())
                }) else {
                    bail!("Profile '{}' has no claim mapping {claim}.", name_of(&profile));
                };
                api.v1().delete_profile_claim_mapping(id, resolve::id(mapping)).send().await?;
                output::success(&format!("Removed the claim mapping {claim} from profile '{}'.", name_of(&profile)));
            }
        },
        ProfileCommand::Tools { profile, server, file } => {
            let profile = resolve::profile(api, &profile).await?;
            let id = resolve::id(&profile);
            if let Some(raw) = super::resources::file_or_stdin(file.as_deref())? {
                let body: Value =
                    serde_json::from_str(raw.trim()).map_err(|_| anyhow!("Failed to parse JSON input."))?;
                api.v1().update_profile_server_tools_raw(id, &server, body).send().await?;
                output::success(&format!(
                    "Replaced the tool settings of profile '{}' for server '{server}'.",
                    name_of(&profile)
                ));
                return Ok(());
            }
            let list = api.v1().list_profile_tools(id).value().await?;
            let Some(settings) = array_at(&list, "servers")
                .into_iter()
                .find(|entry| text_at(entry, "/serverSlug") == Some(server.as_str()))
            else {
                bail!("Server '{server}' is not in profile '{}'.", name_of(&profile));
            };
            output::output(&settings, Options::yaml());
        }
    }
    Ok(())
}

enum Member {
    Account(Value),
    Team(Value),
}

async fn member_of(api: &gatana_api::Client, member: &ProfileMember) -> Result<Member> {
    match (&member.account, &member.team) {
        (Some(account), _) => Ok(Member::Account(resolve::account(api, account).await?)),
        (None, Some(team)) => Ok(Member::Team(resolve::team(api, team).await?)),
        // clap requires one of the two
        (None, None) => bail!("Give --account or --team."),
    }
}

/// `department=engineering` as the claim key and the value that matches. The value may hold `=`.
fn split_claim(claim: &str) -> Result<(String, String)> {
    match claim.split_once('=') {
        Some((key, value)) if !key.is_empty() && !value.is_empty() => Ok((key.to_string(), value.to_string())),
        _ => bail!("Invalid claim: \"{claim}\". Expected format: KEY=VALUE, for example department=engineering"),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn claims_split_at_the_first_equals_sign() {
        assert_eq!(split_claim("department=engineering").unwrap(), ("department".into(), "engineering".into()));
        assert_eq!(split_claim("groups=a=b").unwrap(), ("groups".into(), "a=b".into()));
        assert!(split_claim("department").is_err());
        assert!(split_claim("=engineering").is_err());
    }
}
