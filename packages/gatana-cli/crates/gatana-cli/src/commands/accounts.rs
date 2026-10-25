//! Accounts: users, service accounts, and the personal access tokens of a service account.
//!
//! Your own tokens are not managed here. The backend takes them only from a browser session, so
//! that a token cannot mint its holder a key outside its own limits; the CLI points to the
//! dashboard for them instead.

use super::{MASK, array_at, resolve, text_at};
use crate::cli::{AccountKind, CreateAccountArgs, CreatePatArgs, CreateServiceAccountArgs, Role};
use crate::context::Context;
use crate::output::{self, Column, Options};
use crate::util::format_age;
use anyhow::{Result, bail};
use gatana_api::v1::{self, query};
use serde_json::{Value, json};

const ACCOUNT_COLUMNS: [Column; 7] = [
    Column::path("Email", "email"),
    Column::path("Name", "name"),
    Column::path("Role", "role"),
    Column::computed("Kind", |row| json!(kind(row))),
    Column::computed("Status", |row| json!(status(row))),
    Column::path("SCIM", "isScimManaged"),
    Column::computed("Age", |row| json!(format_age(row.get("createdAt")))),
];

const TOKEN_COLUMNS: [Column; 5] = [
    Column::path("ID", "id"),
    Column::path("Name", "name"),
    Column::computed("Profiles", |row| json!(row.get("profileIds").and_then(Value::as_array).map_or(0, Vec::len))),
    Column::computed("Last Used", |row| json!(last_used(row))),
    Column::computed("Age", |row| json!(format_age(row.get("createdAt")))),
];

fn is_service_account(account: &Value) -> bool {
    account.get("isServiceAccount") == Some(&Value::Bool(true))
}

fn kind(account: &Value) -> &'static str {
    if is_service_account(account) { "service-account" } else { "user" }
}

fn status(account: &Value) -> &'static str {
    if account.get("isDisabled") == Some(&Value::Bool(true)) {
        "disabled"
    } else if account.get("isInvited") == Some(&Value::Bool(true)) {
        "invited"
    } else {
        "active"
    }
}

/// How long ago a token was used, or "never".
fn last_used(token: &Value) -> String {
    match token.get("lastUsedAt") {
        None | Some(Value::Null) => "never".to_string(),
        used => format_age(used),
    }
}

fn email(account: &Value) -> &str {
    text_at(account, "/email").unwrap_or_default()
}

pub async fn get(context: &Context, name: Option<&str>, kind: Option<AccountKind>) -> Result<()> {
    let api = context.api().await?;
    if let Some(name) = name {
        output::output(&resolve::account(api, name).await?, Options::yaml());
        return Ok(());
    }
    let type_ = kind.map(|kind| match kind {
        AccountKind::User => "user".to_string(),
        AccountKind::ServiceAccount => "service-account".to_string(),
        AccountKind::All => "all".to_string(),
    });
    let list = api.v1().list_users(&query::ListUsers { type_ }).value().await?;
    output::output(&json!({ "accounts": array_at(&list, "users") }), Options::columns(&ACCOUNT_COLUMNS));
    Ok(())
}

/// The account with what it has: profiles, teams and, for a service account, its tokens without
/// their keys.
pub async fn describe(context: &Context, name: &str) -> Result<()> {
    let api = context.api().await?;
    let account = resolve::account(api, name).await?;
    let id = resolve::id(&account).to_string();

    let profiles = array_at(&api.v1().list_profiles(&query::ListProfiles::default()).value().await?, "profiles");
    let profile_name = |profile_id: &str| {
        profiles
            .iter()
            .find(|profile| resolve::id(profile) == profile_id)
            .and_then(|profile| profile.get("name").cloned())
            .unwrap_or_else(|| json!(profile_id))
    };
    let assigned: Vec<Value> = array_at(&account, "profileIds")
        .iter()
        .map(|assignment| {
            json!({
                "profile": profile_name(text_at(assignment, "/profileId").unwrap_or_default()),
                "locked": assignment.get("isLockedByOrgOwner").cloned().unwrap_or(Value::Bool(false)),
            })
        })
        .collect();
    let teams: Vec<Value> =
        array_at(&api.v1().list_teams(&query::ListTeams { user_id: Some(id.clone()) }).value().await?, "teams")
            .iter()
            .filter_map(|team| team.get("name").cloned())
            .collect();

    let mut shown = json!({ "account": account, "profiles": assigned, "teams": teams });
    if is_service_account(&account)
        && let Ok(list) = api.v1().list_service_account_personal_access_tokens(&id).value().await
    {
        let tokens: Vec<Value> = array_at(&list, "tokens")
            .iter()
            .map(|token| {
                json!({
                    "id": token.get("id"),
                    "name": token.get("name"),
                    "lastUsed": last_used(token),
                    "age": format_age(token.get("createdAt")),
                })
            })
            .collect();
        shown["tokens"] = Value::Array(tokens);
    }
    output::output(&shown, Options::yaml());
    Ok(())
}

pub async fn create(context: &Context, args: CreateAccountArgs) -> Result<()> {
    let name = args.name.unwrap_or_else(|| args.email.split('@').next().unwrap_or_default().to_string());
    let body = v1::types::CreateUserRequest {
        email: args.email.clone(),
        name,
        role: role(args.role),
        is_service_account: false,
    };
    let created = context.api().await?.v1().create_user(&body).value().await?;
    if output::machine_readable() {
        output::print(created.get("user").unwrap_or(&created));
    } else {
        output::success(&format!("Invited {}. Gatana sent an email with a link to set a password.", args.email));
    }
    Ok(())
}

pub async fn create_service_account(context: &Context, args: CreateServiceAccountArgs) -> Result<()> {
    let email = service_account_email(&args.name, &context.config()?.org_id)?;
    let api = context.api().await?;
    let body = v1::types::CreateUserRequest {
        email: email.clone(),
        name: args.name.clone(),
        role: role(args.role),
        is_service_account: true,
    };
    let created = api.v1().create_user(&body).value().await?;
    let account = created.get("user").cloned().unwrap_or(created);
    let id = resolve::id(&account).to_string();

    // Gatana gives every new account a first token, so the key is there already
    let token = match api.v1().list_service_account_personal_access_tokens(&id).value().await {
        Ok(list) => array_at(&list, "tokens").into_iter().next(),
        Err(error) => {
            gatana_api::debug!("gatana", "could not read the tokens of the new service account: {error}");
            None
        }
    };
    if output::machine_readable() {
        output::print(&json!({ "account": account, "token": token }));
        return Ok(());
    }
    output::success(&format!("Created service account '{}' ({email}).", args.name));
    match token.as_ref().and_then(|token| text_at(token, "/apiKey")) {
        Some(key) => output::println(&format!("API key: {key}")),
        None => output::println(&format!("Create its API key with: gatana create pat --account {email} --name <name>")),
    }
    Ok(())
}

/// The address the dashboard gives a new service account (NewAccountPage): the name in lowercase,
/// with only letters, digits and spaces, and a hyphen for each run of spaces.
pub(crate) fn service_account_email(name: &str, org_id: &str) -> Result<String> {
    let kept: String = name
        .to_lowercase()
        .chars()
        .filter(|ch| ch.is_ascii_lowercase() || ch.is_ascii_digit() || ch.is_whitespace())
        .collect();
    let slug = kept.split_whitespace().collect::<Vec<_>>().join("-");
    if slug.is_empty() {
        bail!("The name of a service account needs at least one letter or digit (a to z, 0 to 9).");
    }
    Ok(format!("{slug}@service-account.{org_id}.gatana"))
}

fn role(role: Role) -> v1::types::CreateUserRequestRole {
    match role {
        Role::Member => v1::types::CreateUserRequestRole::Member,
        Role::Owner => v1::types::CreateUserRequestRole::Owner,
    }
}

pub async fn patch(context: &Context, name: &str, body: Value) -> Result<()> {
    let api = context.api().await?;
    let account = resolve::account(api, name).await?;
    // Every field of the update is optional, so the keys left out keep their values
    api.v1().update_user_raw(resolve::id(&account), body).send().await?;
    output::success(&format!("Updated account '{}'.", email(&account)));
    Ok(())
}

pub async fn delete(context: &Context, name: &str) -> Result<()> {
    let api = context.api().await?;
    let account = resolve::account(api, name).await?;
    api.v1().delete_user(resolve::id(&account)).send().await?;
    output::success(&format!("Deleted account '{}'.", email(&account)));
    Ok(())
}

/// The service account `name`, or why its tokens cannot be managed from here.
async fn service_account(context: &Context, api: &gatana_api::Client, name: &str) -> Result<Value> {
    let account = resolve::account(api, name).await?;
    if is_service_account(&account) {
        return Ok(account);
    }
    let page = format!("{}/dashboard/connected-clients", context.config()?.base_url.trim_end_matches('/'));
    let me = api.v1().get_auth_me().value().await?;
    if text_at(&me, "/user/id") == Some(resolve::id(&account)) {
        bail!("Your own tokens need a browser session. Manage them on {page}");
    }
    bail!("'{}' is a user, not a service account. A user manages their own tokens on {page}", email(&account));
}

/// A token without its key, unless the key is asked for.
fn hide_key(mut token: Value, show_secrets: bool) -> Value {
    if !show_secrets && let Some(key) = token.get_mut("apiKey") {
        *key = json!(MASK);
    }
    token
}

pub async fn get_tokens(context: &Context, account: &str, show_secrets: bool) -> Result<()> {
    let api = context.api().await?;
    let account = service_account(context, api, account).await?;
    let list = api.v1().list_service_account_personal_access_tokens(resolve::id(&account)).value().await?;
    let tokens: Vec<Value> = array_at(&list, "tokens").into_iter().map(|token| hide_key(token, show_secrets)).collect();
    output::output(&json!({ "tokens": tokens }), Options::columns(&TOKEN_COLUMNS));
    Ok(())
}

pub async fn create_token(context: &Context, args: CreatePatArgs) -> Result<()> {
    let api = context.api().await?;
    let account = service_account(context, api, &args.account).await?;
    let mut profile_ids = Vec::new();
    for profile in &args.profiles {
        profile_ids.push(resolve::id(&resolve::profile(api, profile).await?).to_string());
    }
    let body = v1::types::CreatePersonalAccessTokenRequest { name: args.name.clone(), profile_ids };
    let created = api.v1().create_service_account_personal_access_token(resolve::id(&account), &body).value().await?;
    let token = created.get("token").cloned().unwrap_or(created);
    if output::machine_readable() {
        output::print(&token);
        return Ok(());
    }
    output::success(&format!("Created token '{}' for '{}'.", args.name, email(&account)));
    output::println(&format!("API key: {}", text_at(&token, "/apiKey").unwrap_or("<none>")));
    Ok(())
}

pub async fn delete_token(context: &Context, account: &str, token: &str) -> Result<()> {
    let api = context.api().await?;
    let account = service_account(context, api, account).await?;
    let id = resolve::id(&account).to_string();
    let list = api.v1().list_service_account_personal_access_tokens(&id).value().await?;
    let found =
        resolve::find(&array_at(&list, "tokens"), token, "name", "token", "\"gatana get pats --account <account>\"")?;
    api.v1().delete_service_account_personal_access_token(&id, resolve::id(&found)).send().await?;
    output::success(&format!(
        "Deleted token '{}' of '{}'.",
        text_at(&found, "/name").unwrap_or(token),
        email(&account)
    ));
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn service_account_addresses_match_the_dashboard() {
        assert_eq!(service_account_email("Deploy bot", "acme").unwrap(), "deploy-bot@service-account.acme.gatana");
        assert_eq!(
            service_account_email("  CI / CD  runner-2 ", "acme").unwrap(),
            "ci-cd-runner2@service-account.acme.gatana"
        );
        assert!(service_account_email("Ö!", "acme").is_err());
    }

    #[test]
    fn keys_are_hidden_unless_asked_for() {
        let token = json!({ "id": "pat_1", "apiKey": "gk_1_secret" });
        assert_eq!(hide_key(token.clone(), false)["apiKey"], json!(MASK));
        assert_eq!(hide_key(token, true)["apiKey"], json!("gk_1_secret"));
    }

    #[test]
    fn status_reads_disabled_before_invited() {
        assert_eq!(status(&json!({ "isDisabled": true, "isInvited": true })), "disabled");
        assert_eq!(status(&json!({ "isDisabled": false, "isInvited": true })), "invited");
        assert_eq!(status(&json!({})), "active");
    }
}
