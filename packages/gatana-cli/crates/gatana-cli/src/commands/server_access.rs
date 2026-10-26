//! Who has access to a server: accounts and teams with a role of their own on it, and the profiles
//! that hold it, which give the role member. Two settings give access without a row here: the
//! visibility of the server, and the base role of the organization.

use super::resolve::{self, Member};
use super::{array_at, text_at};
use crate::cli::ServerCommand;
use crate::context::Context;
use crate::output::{self, Column};
use anyhow::{Result, bail};
use gatana_api::v1::{self, query};
use serde_json::{Value, json};

const ACCESS_COLUMNS: [Column; 3] =
    [Column::path("Kind", "kind"), Column::path("Name", "name"), Column::path("Role", "role")];

/// One row for each account, team and profile with a role on the server.
pub(crate) async fn access_rows(api: &gatana_api::Client, slug: &str) -> Result<Vec<Value>> {
    let members = api.v1().list_mcp_server_members(slug).value().await?;
    let profiles = api.v1().list_profiles(&query::ListProfiles { server_slug: Some(slug.to_string()) }).value().await?;
    let row = |kind: &str, row: &Value, label: &str, role: Option<&Value>| json!({ "kind": kind, "name": row.get(label), "role": role, "id": row.get("id") });
    let mut rows: Vec<Value> =
        array_at(&members, "users").iter().map(|user| row("account", user, "email", user.get("role"))).collect();
    rows.extend(array_at(&members, "teams").iter().map(|team| row("team", team, "name", team.get("role"))));
    // A profile always gives the role member on its servers
    rows.extend(
        array_at(&profiles, "profiles").iter().map(|profile| row("profile", profile, "name", Some(&json!("member")))),
    );
    Ok(rows)
}

pub async fn run(context: &Context, command: ServerCommand) -> Result<()> {
    let api = context.api().await?;
    match command {
        ServerCommand::Access { server } => {
            let rows = access_rows(api, &server).await?;
            let details = api.v2().get_server_v2(&server).value().await?;
            let me = api.v1().get_auth_me().value().await?;
            let visibility = text_at(&details, "/visibility").unwrap_or("private");
            let base_role = text_at(&me, "/tenant/memberDefaultRole").unwrap_or("none");
            if output::machine_readable() {
                output::print(&json!({
                    "server": server,
                    "visibility": visibility,
                    "memberDefaultRole": base_role,
                    "access": rows,
                }));
                return Ok(());
            }
            if rows.is_empty() {
                output::println(&format!("No account, team or profile has a role on server '{server}'."));
            } else {
                for line in output::render_table(&rows, Some(&ACCESS_COLUMNS), false) {
                    output::println(&line);
                }
            }
            for note in access_notes(visibility, base_role) {
                output::println(&format!("\n{note}"));
            }
        }
        ServerCommand::Grant { server, member, role } => {
            let member = resolve::member(api, &member).await?;
            let body = v1::types::UpdateMcpServerMemberBody { role: role.name().parse()? };
            api.v1().update_mcp_server_member(&server, member.path_kind(), member.id(), &body).send().await?;
            output::success(&format!("Gave {} the role {} on server '{server}'.", member.label(), role.name()));
        }
        ServerCommand::Revoke { server, member } => {
            let member = resolve::member(api, &member).await?;
            let members = api.v1().list_mcp_server_members(&server).value().await?;
            if !array_at(&members, member.path_kind()).iter().any(|row| resolve::id(row) == member.id()) {
                let through = match member {
                    Member::Account(_) => " It can still have access through a team or a profile.",
                    Member::Team(_) => " It can still have access through a profile.",
                };
                bail!("The {} has no role of its own on server '{server}'.{through}", member.label());
            }
            api.v1().delete_mcp_server_member(&server, member.path_kind(), member.id()).send().await?;
            output::success(&format!("Took the role on server '{server}' away from {}.", member.label()));
        }
    }
    Ok(())
}

/// The settings that give access to more people than the rows show.
fn access_notes(visibility: &str, base_role: &str) -> Vec<String> {
    let mut notes = Vec::new();
    if visibility == "organization" {
        notes.push("The visibility of the server is organization: every member of the organization can use it.".into());
    }
    if base_role != "none" {
        notes.push(format!(
            "The base role of the organization is {base_role}: every member has at least this role on every server."
        ));
    }
    notes
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn notes_tell_of_access_that_the_rows_do_not_show() {
        assert!(access_notes("private", "none").is_empty());
        let notes = access_notes("organization", "maintainer");
        assert_eq!(notes.len(), 2);
        assert!(notes[1].contains("base role of the organization is maintainer"));
    }
}
