//! Teams: the team itself through get, describe, create, patch and delete, and its members,
//! invitations and claim mappings through "gatana team". A team gets its access from a role on a
//! server ("gatana server grant") or from a profile ("gatana profile assign").

use super::profiles::split_claim;
use super::{array_at, resolve, text_at};
use crate::cli::{CreateTeamArgs, InvitationCommand, TeamClaimCommand, TeamCommand};
use crate::context::Context;
use crate::output::{self, Column, Options};
use crate::util::{format_age, parse_date};
use anyhow::{Result, anyhow, bail};
use gatana_api::v1::{self, query};
use serde_json::{Value, json};

const TEAM_COLUMNS: [Column; 5] = [
    Column::path("Name", "name"),
    Column::path("Members", "memberCount"),
    Column::path("Has Profile", "hasProfileAttached"),
    Column::path("SCIM", "isScimManaged"),
    Column::computed("Age", |row| json!(format_age(row.get("createdAt")))),
];

fn name_of(team: &Value) -> &str {
    text_at(team, "/name").unwrap_or_default()
}

fn email(account: &Value) -> &str {
    text_at(account, "/email").unwrap_or_default()
}

pub async fn get(context: &Context, name: Option<&str>, account: Option<&str>) -> Result<()> {
    let api = context.api().await?;
    if let Some(name) = name {
        output::output(&resolve::team(api, name).await?, Options::yaml());
        return Ok(());
    }
    let user_id = match account {
        Some(account) => Some(resolve::id(&resolve::account(api, account).await?).to_string()),
        None => None,
    };
    let list = api.v1().list_teams(&query::ListTeams { user_id }).value().await?;
    output::output(&json!({ "teams": array_at(&list, "teams") }), Options::columns(&TEAM_COLUMNS));
    Ok(())
}

/// The team with its members and what it gives them. Only those who manage the team read its
/// invitations, so they are left out for the others.
pub async fn describe(context: &Context, name: &str) -> Result<()> {
    let api = context.api().await?;
    let team = resolve::team(api, name).await?;
    let id = resolve::id(&team).to_string();
    let members = api.v1().list_team_members(&id).value().await?;
    let servers = api.v1().list_team_servers(&id).value().await?;
    let assignments = api.v1().list_team_profiles(&id).value().await?;
    let mappings = api.v1().list_team_claim_mappings(&id).value().await?;

    let profiles = array_at(&api.v1().list_profiles(&query::ListProfiles::default()).value().await?, "profiles");
    let profile_name = |profile_id: &str| {
        profiles
            .iter()
            .find(|profile| resolve::id(profile) == profile_id)
            .and_then(|profile| profile.get("name").cloned())
            .unwrap_or_else(|| json!(profile_id))
    };

    let mut shown = json!({
        "team": team,
        "members": array_at(&members, "members")
            .iter()
            .map(|row| json!({ "email": row.pointer("/user/email"), "role": row.pointer("/member/role") }))
            .collect::<Vec<_>>(),
        "servers": array_at(&servers, "permissions")
            .iter()
            .map(|row| json!({ "server": row.get("serverSlug"), "role": row.pointer("/permission/role") }))
            .collect::<Vec<_>>(),
        "profiles": array_at(&assignments, "profileAssignments")
            .iter()
            .map(|row| {
                json!({
                    "profile": profile_name(text_at(row, "/profileId").unwrap_or_default()),
                    "locked": row.get("isLockedByOrgOwner").cloned().unwrap_or(Value::Bool(false)),
                })
            })
            .collect::<Vec<_>>(),
        "claimMappings": array_at(&mappings, "claimMappings").iter().map(claim_text).collect::<Vec<_>>(),
    });
    if let Ok(list) = api.v1().list_team_invitations(&id).value().await {
        let open: Vec<Value> = array_at(&list, "invitations")
            .iter()
            .filter(|invitation| invitation.get("acceptedAt").is_none_or(Value::is_null))
            .map(|invitation| {
                let expires = text_at(invitation, "/expiresAt").unwrap_or_default();
                let expired = parse_date(expires).is_some_and(|date| date < chrono::Utc::now());
                json!({
                    "email": invitation.get("email"),
                    "role": invitation.get("role"),
                    "expires": expires.get(..10).unwrap_or(expires),
                    "status": if expired { "expired" } else { "open" },
                })
            })
            .collect();
        shown["invitations"] = Value::Array(open);
    }
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

pub async fn create(context: &Context, args: CreateTeamArgs) -> Result<()> {
    let api = context.api().await?;
    // Found before the team exists, so that a wrong name leaves nothing half made
    let accounts = resolve::accounts(api, &args.accounts).await?;
    let body = v1::types::CreateTeamBody { name: args.name.clone(), description: args.description };
    let created = api.v1().create_team(&body).value().await?;
    let id = text_at(&created, "/team/id").ok_or_else(|| anyhow!("The created team has no id"))?.to_string();
    for account in &accounts {
        let body = v1::types::CreateTeamMemberBody {
            role: v1::types::CreateTeamMemberBodyRole::Member,
            user_id: resolve::id(account).to_string(),
        };
        api.v1().create_team_member(&id, &body).send().await?;
    }
    if output::machine_readable() {
        output::print(&api.v1().get_team(&id).value().await?);
        return Ok(());
    }
    let with = if accounts.is_empty() {
        String::new()
    } else {
        format!(" with {}", accounts.iter().map(email).collect::<Vec<_>>().join(", "))
    };
    output::success(&format!("Created team '{}'{with}.", args.name));
    output::println(&format!(
        "Give it access: gatana server grant <slug> --team '{0}', or gatana profile assign <profile> --team '{0}'",
        args.name
    ));
    Ok(())
}

pub async fn patch(context: &Context, name: &str, body: Value) -> Result<()> {
    let api = context.api().await?;
    let team = resolve::team(api, name).await?;
    let Value::Object(patch) = body else { bail!("The patch must be a JSON object.") };
    // The update takes the name and the description together, so the stored values fill in the keys
    // that the patch leaves out
    let mut full = json!({ "name": team.get("name"), "description": team.get("description") });
    for (key, value) in patch {
        full[key] = value;
    }
    api.v1().update_team_raw(resolve::id(&team), full).send().await?;
    output::success(&format!("Updated team '{}'.", name_of(&team)));
    Ok(())
}

pub async fn delete(context: &Context, name: &str) -> Result<()> {
    let api = context.api().await?;
    let team = resolve::team(api, name).await?;
    api.v1().delete_team(resolve::id(&team)).send().await?;
    output::success(&format!("Deleted team '{}'.", name_of(&team)));
    Ok(())
}

/// The role of each member of a team, by user ID.
async fn member_roles(api: &gatana_api::Client, team_id: &str) -> Result<Vec<(String, String)>> {
    let members = api.v1().list_team_members(team_id).value().await?;
    Ok(array_at(&members, "members")
        .iter()
        .filter_map(|row| {
            Some((text_at(row, "/member/userId")?.to_string(), text_at(row, "/member/role")?.to_string()))
        })
        .collect())
}

pub async fn run(context: &Context, command: TeamCommand) -> Result<()> {
    let api = context.api().await?;
    match command {
        TeamCommand::AddMember { team, accounts, role } => {
            let team = resolve::team(api, &team).await?;
            let id = resolve::id(&team);
            let accounts = resolve::accounts(api, &accounts).await?;
            let roles = member_roles(api, id).await?;
            for account in &accounts {
                let user_id = resolve::id(account);
                let current = roles.iter().find(|(member, _)| member == user_id).map(|(_, role)| role.as_str());
                let message = match current {
                    Some(current) if current == role.name() => {
                        format!("'{}' is already a {} of team '{}'.", email(account), role.name(), name_of(&team))
                    }
                    // Adding an existing member fails, so a member gets the new role through the update
                    Some(_) => {
                        let body = v1::types::UpdateTeamMemberBody { role: role.name().parse()? };
                        api.v1().update_team_member(id, user_id, &body).send().await?;
                        format!("'{}' is now a {} of team '{}'.", email(account), role.name(), name_of(&team))
                    }
                    None => {
                        let body = v1::types::CreateTeamMemberBody {
                            role: role.name().parse()?,
                            user_id: user_id.to_string(),
                        };
                        api.v1().create_team_member(id, &body).send().await?;
                        format!("Added '{}' to team '{}' as a {}.", email(account), name_of(&team), role.name())
                    }
                };
                output::success(&message);
            }
        }
        TeamCommand::RemoveMember { team, accounts } => {
            let team = resolve::team(api, &team).await?;
            let id = resolve::id(&team);
            let accounts = resolve::accounts(api, &accounts).await?;
            let roles = member_roles(api, id).await?;
            if let Some(account) =
                accounts.iter().find(|account| !roles.iter().any(|(user_id, _)| user_id == resolve::id(account)))
            {
                bail!("'{}' is not a member of team '{}'.", email(account), name_of(&team));
            }
            for account in &accounts {
                api.v1().delete_team_member(id, resolve::id(account)).send().await?;
            }
            let removed: Vec<&str> = accounts.iter().map(email).collect();
            output::success(&format!("Removed {} from team '{}'.", removed.join(", "), name_of(&team)));
        }
        TeamCommand::Invitations { command } => invitations(api, command).await?,
        TeamCommand::Claims { command } => match command {
            TeamClaimCommand::Add { team, claim } => {
                let (claim_key, claim_value) = split_claim(&claim)?;
                let team = resolve::team(api, &team).await?;
                let body = v1::types::CreateTeamClaimMappingBody { claim_key, claim_value };
                api.v1().create_team_claim_mapping(resolve::id(&team), &body).send().await?;
                output::success(&format!(
                    "Everyone with the claim {claim} now joins team '{}' when they sign in.",
                    name_of(&team)
                ));
            }
            TeamClaimCommand::Rm { team, claim } => {
                let (key, value) = split_claim(&claim)?;
                let team = resolve::team(api, &team).await?;
                let id = resolve::id(&team);
                let mappings = array_at(&api.v1().list_team_claim_mappings(id).value().await?, "claimMappings");
                let Some(mapping) = mappings.iter().find(|mapping| {
                    text_at(mapping, "/claimKey") == Some(key.as_str())
                        && text_at(mapping, "/claimValue") == Some(value.as_str())
                }) else {
                    bail!("Team '{}' has no claim mapping {claim}.", name_of(&team));
                };
                api.v1().delete_team_claim_mapping(id, resolve::id(mapping)).send().await?;
                output::success(&format!("Removed the claim mapping {claim} from team '{}'.", name_of(&team)));
            }
        },
    }
    Ok(())
}

async fn invitations(api: &gatana_api::Client, command: InvitationCommand) -> Result<()> {
    match command {
        InvitationCommand::Add { team, emails, role } => {
            let team = resolve::team(api, &team).await?;
            for address in &emails {
                let body = v1::types::CreateTeamInvitationBody { email: address.clone(), role: role.name().parse()? };
                api.v1().create_team_invitation(resolve::id(&team), &body).send().await?;
                output::success(&format!(
                    "Invited '{address}' to team '{}' as a {}. The invitation expires after 7 days.",
                    name_of(&team),
                    role.name()
                ));
            }
        }
        InvitationCommand::Rm { team, email: address } => {
            let team = resolve::team(api, &team).await?;
            let id = resolve::id(&team);
            let list = api.v1().list_team_invitations(id).value().await?;
            let open: Vec<Value> = array_at(&list, "invitations")
                .into_iter()
                .filter(|invitation| invitation.get("acceptedAt").is_none_or(Value::is_null))
                .filter(|invitation| {
                    text_at(invitation, "/email").is_some_and(|text| text.eq_ignore_ascii_case(&address))
                })
                .collect();
            if open.is_empty() {
                bail!("Team '{}' has no open invitation for '{address}'.", name_of(&team));
            }
            for invitation in &open {
                api.v1().delete_team_invitation(id, resolve::id(invitation)).send().await?;
            }
            output::success(&format!("Deleted the invitation of '{address}' to team '{}'.", name_of(&team)));
        }
    }
    Ok(())
}
