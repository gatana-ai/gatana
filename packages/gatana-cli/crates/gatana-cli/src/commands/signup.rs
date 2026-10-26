//! `gatana signup`: create an organization and sign in to it.
//!
//! In the terminal by default: the CLI asks for the name, the organization ID and the email
//! address, the backend sends a code to the address, and the person types the code here. The
//! backend then creates the organization and hands the CLI a refresh token of the organization's
//! CLI client for the new owner (TenantController.cliSignup in the backend), so the CLI ends up
//! signed in as after a device login. With `--browser`, the sign-up page does it all (apex.rs).
//!
//! The sign-up requests go to the apex, not to the host of the new organization: that host does
//! not exist yet, and for a reserved ID (docs, status, www) another service answers there.
//!
//! Without a terminal (an agent, a script), nobody can type the code. The run then stops after the
//! code went out and prints the command that finishes the sign-up with `--code`.

use super::Silent;
use super::config::{apex_login, logged_in};
use crate::apex::{SignUpForm, Start};
use crate::cli::SignupArgs;
use crate::config::{login_command, set_organization_login};
use crate::context::Context;
use crate::output;
use anyhow::{Context as _, Result, anyhow, bail};
use reqwest::StatusCode;
use serde_json::{Value, json};
use std::io::IsTerminal;

/// What the backend accepts (cliSignupSchema).
const MAX_NAME_LENGTH: usize = 50;
const MAX_ORG_ID_LENGTH: usize = 40;
const MAX_EMAIL_LENGTH: usize = 50;
/// The backend voids a code after 5 wrong tries, and after 30 minutes (065_email_verification_codes.sql).
const CODE_ATTEMPTS: usize = 5;
const CODE_VALID_MINUTES: u32 = 30;

pub async fn run(context: &Context, args: SignupArgs) -> Result<()> {
    let result = if args.browser {
        let SignupArgs { base_url, email, org_name, .. } = args;
        let form = SignUpForm { email, organization_name: org_name };
        apex_login(context, base_url, true, Start::CreateOrganization(form)).await.map(|()| true)
    } else {
        in_terminal(context, args).await
    };
    match result {
        Ok(true) => output::println("Next, run \"gatana install\" to connect your AI agents to the organization."),
        Ok(false) => {}
        Err(error) => {
            output::error(&format!("Sign-up failed: {error:#}"));
            return Err(Silent.into());
        }
    }
    Ok(())
}

/// True when the CLI is signed in at the end; false when it stopped after the code went out.
async fn in_terminal(context: &Context, args: SignupArgs) -> Result<bool> {
    let SignupArgs { org_name, org_id, email, code, base_url, .. } = args;
    let apex_url = base_url.as_deref().unwrap_or(crate::apex::DEFAULT_APEX_URL);
    let apex = url::Url::parse(apex_url).with_context(|| format!("invalid URL {apex_url}"))?;
    let url = signup_url(&apex);
    let interactive = std::io::stdin().is_terminal();

    let mut code = code.map(|code| answer(Some(code), "--code", "", None, check_code)).transpose()?;
    let name = answer(org_name, "--org-name", "Organization name", None, check_name)?;
    let mut org_id = answer(org_id, "--org-id", "Organization ID", Some(org_id_from_name(&name)), check_org_id)?;
    let email = answer(email, "--email", "Your email address", None, check_email)?;

    // With --code, an earlier run sent the code. Without it, the backend checks the ID before it
    // sends an email, so a taken ID costs no code.
    let verification_required = code.is_some()
        || loop {
            let send_code = format!("{url}/send-code");
            match post(context.http(), &send_code, &json!({ "tenantSlug": org_id, "email": email })).await {
                Ok(body) => break body.get("verificationRequired").and_then(Value::as_bool).unwrap_or(true),
                Err(error) if interactive && is_organization_id_refusal(&error) => {
                    output::error(&format!("{error}"));
                    org_id = answer(None, "--org-id", "Another organization ID", None, check_org_id)?;
                }
                Err(error) if is_unknown_route(&error) => {
                    bail!("{apex_url} does not support sign-up in the terminal. Run: gatana signup --browser")
                }
                Err(error) => return Err(error),
            }
        };

    let mut body = json!({ "tenantDisplayName": name, "tenantSlug": org_id, "email": email });
    let created = if verification_required {
        if code.is_none() {
            if !interactive {
                output::println(&format!(
                    "Gatana sent a code to {email}. It is valid for {CODE_VALID_MINUTES} minutes. To finish the sign-up, run this command with the code from the email:"
                ));
                output::println(&format!("  {}", finishing_command(&name, &org_id, &email, base_url.as_deref())));
                return Ok(false);
            }
            output::println(&format!(
                "Gatana sent a code to {}. It can take a minute to arrive.",
                output::bold(&email)
            ));
        }
        let mut attempt = 1;
        loop {
            let current = match code.take() {
                Some(code) => code,
                None => ask_code()?,
            };
            body["verificationCode"] = Value::String(current);
            match post(context.http(), &url, &body).await {
                Ok(created) => break created,
                Err(error) if interactive && attempt < CODE_ATTEMPTS && is_code_refusal(&error) => {
                    // The backend says the same for a wrong code and for an expired one
                    output::error(&format!(
                        "The code is wrong or has expired. Try again ({} tries left), or press Ctrl+C and run gatana signup again for a new code.",
                        CODE_ATTEMPTS - attempt
                    ));
                    attempt += 1;
                }
                Err(error) if is_code_refusal(&error) => bail!(
                    "The code is wrong or has expired. Check the code in the email and run the command again with --code. Without --code, the command sends a new code"
                ),
                Err(error) => return Err(error),
            }
        }
    } else {
        post(context.http(), &url, &body).await?
    };

    let field = |name: &str| {
        created.get(name).and_then(Value::as_str).ok_or_else(|| anyhow!("the answer of the server has no {name}"))
    };
    let (org_id, client_id, refresh_token) = (field("tenantId")?, field("clientId")?, field("refreshToken")?);
    let base_url = crate::apex::organization_url(&apex, org_id)?;
    output::success(&format!("Created {name} at {base_url}"));

    let tokens =
        crate::oidc::refresh(context.http(), &base_url, client_id, refresh_token).await.with_context(|| {
            format!("The organization exists, but the sign-in failed. Run: {}", login_command(org_id, &base_url))
        })?;
    let stored = json!({
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token.as_deref().unwrap_or(refresh_token),
        "expires_at": tokens.expires_at(),
    });
    // No clientId: without one, the CLI uses the organization's own `<org>-cli`, which this token is for
    let saved_as = set_organization_login(org_id, &base_url, json!({ "tokens": stored }))?;
    logged_in(&saved_as)?;
    Ok(true)
}

/// The sign-up routes are tenant-agnostic in the backend, and the apex sends `/api/` to it.
fn signup_url(apex: &url::Url) -> String {
    format!("{}/api/v1/cli-signup", apex.origin().ascii_serialization())
}

/// The command that finishes a sign-up whose code went out: the same answers, and the code. The
/// ID is spelled out, so that the second run cannot make another one from the name.
fn finishing_command(name: &str, org_id: &str, email: &str, base_url: Option<&str>) -> String {
    let mut command = format!(
        "gatana signup --org-name {} --org-id {} --email {}",
        shell_word(name),
        shell_word(org_id),
        shell_word(email)
    );
    if let Some(base_url) = base_url {
        command.push_str(&format!(" --base-url {}", shell_word(base_url)));
    }
    command.push_str(" --code <code>");
    command
}

/// `value` as one shell word: as it is when that is safe, else in single quotes.
fn shell_word(value: &str) -> String {
    let plain = !value.is_empty() && value.bytes().all(|b| b.is_ascii_alphanumeric() || b"@%+=:,./_-".contains(&b));
    if plain { value.to_string() } else { format!("'{}'", value.replace('\'', r"'\''")) }
}

/// The value given on the command line, or one typed at a prompt. Without a terminal, a default
/// that passes the check stands in for the prompt.
fn answer(
    given: Option<String>,
    flag: &str,
    prompt: &str,
    default: Option<String>,
    check: fn(&str) -> Result<(), String>,
) -> Result<String> {
    if let Some(value) = given {
        let value = value.trim().to_string();
        check(&value).map_err(|problem| anyhow!("{flag}: {problem}"))?;
        return Ok(value);
    }
    let default = default.filter(|value| check(value).is_ok());
    if !std::io::stdin().is_terminal() {
        return default.ok_or_else(|| anyhow!("Give {flag}, or run gatana signup in a terminal"));
    }
    let mut input =
        dialoguer::Input::<String>::new().with_prompt(prompt).validate_with(|value: &String| check(value.trim()));
    if let Some(default) = default {
        input = input.default(default);
    }
    Ok(input.interact_text()?.trim().to_string())
}

fn ask_code() -> Result<String> {
    let code = dialoguer::Input::<String>::new()
        .with_prompt("Code from the email")
        .validate_with(|value: &String| check_code(value.trim()))
        .interact_text()?;
    Ok(code.trim().to_string())
}

fn check_code(code: &str) -> Result<(), String> {
    if code.len() == 6 && code.bytes().all(|b| b.is_ascii_digit()) {
        Ok(())
    } else {
        Err("Enter the 6 digits of the code".into())
    }
}

fn check_name(name: &str) -> Result<(), String> {
    match name.chars().count() {
        0 => Err("Enter a name".into()),
        length if length > MAX_NAME_LENGTH => Err(format!("Use at most {MAX_NAME_LENGTH} characters")),
        _ => Ok(()),
    }
}

/// The ID becomes a host name, and the TLS stack of the CLI refuses a label that starts or ends
/// with a hyphen.
fn check_org_id(id: &str) -> Result<(), String> {
    let allowed = |b: u8| b.is_ascii_lowercase() || b.is_ascii_digit() || b == b'-';
    if id.is_empty() || id.len() > MAX_ORG_ID_LENGTH || !id.bytes().all(allowed) {
        return Err(format!("Use 1 to {MAX_ORG_ID_LENGTH} lowercase letters, digits and hyphens"));
    }
    if id.starts_with('-') || id.ends_with('-') {
        return Err("Do not start or end the ID with a hyphen".into());
    }
    Ok(())
}

/// A first check only: the backend checks the address, and the code proves it.
fn check_email(email: &str) -> Result<(), String> {
    let shaped = matches!(email.split_once('@'), Some((local, domain)) if !local.is_empty() && domain.contains('.'));
    if !shaped || email.len() > MAX_EMAIL_LENGTH || email.contains(char::is_whitespace) {
        return Err(format!("Enter an email address of at most {MAX_EMAIL_LENGTH} characters"));
    }
    Ok(())
}

/// The organization ID the sign-up page makes from a name (sign-up-form.tsx in the frontend).
fn org_id_from_name(name: &str) -> String {
    let id: String = name
        .to_lowercase()
        .replace(' ', "-")
        .chars()
        .filter(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || *c == '-')
        .collect();
    id.trim_matches('-').to_string()
}

/// The backend refused a request, with its reason.
#[derive(Debug)]
struct Refused {
    status: StatusCode,
    message: String,
}

impl std::fmt::Display for Refused {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.message)
    }
}

impl std::error::Error for Refused {}

/// Taken (409), or not allowed (400, "The organization ID 'admin' is not allowed").
fn is_organization_id_refusal(error: &anyhow::Error) -> bool {
    error.downcast_ref::<Refused>().is_some_and(|refused| {
        refused.status == StatusCode::CONFLICT
            || (refused.status == StatusCode::BAD_REQUEST && refused.message.contains("rganization ID"))
    })
}

fn is_code_refusal(error: &anyhow::Error) -> bool {
    error.downcast_ref::<Refused>().is_some_and(|refused| {
        refused.status == StatusCode::BAD_REQUEST && refused.message.contains("verification code")
    })
}

/// A backend without the CLI routes finds no route on the apex: 404, or 400 "Invalid tenant" from
/// an older backend (getTenant in the backend).
fn is_unknown_route(error: &anyhow::Error) -> bool {
    error.downcast_ref::<Refused>().is_some_and(|refused| {
        refused.status == StatusCode::NOT_FOUND
            || (refused.status == StatusCode::BAD_REQUEST && refused.message == "Invalid tenant")
    })
}

/// The JSON answer, or a `Refused` with the reason the backend gave.
async fn post(http: &reqwest::Client, url: &str, body: &Value) -> Result<Value> {
    let response = http.post(url).json(body).send().await.with_context(|| format!("could not reach {url}"))?;
    let status = response.status();
    let value: Value = response.json().await.unwrap_or(Value::Null);
    if status.is_success() {
        return Ok(value);
    }
    Err(Refused { status, message: refusal_message(&value, status) }.into())
}

/// The backend's reason: a validation error names the field in `details`, any other error says it
/// in `message`.
fn refusal_message(value: &Value, status: StatusCode) -> String {
    value
        .pointer("/details/0/message")
        .or_else(|| value.get("message"))
        .and_then(Value::as_str)
        .map(str::to_string)
        .unwrap_or_else(|| format!("The server answered {status}"))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_id_comes_from_the_name_as_on_the_sign_up_page() {
        assert_eq!(org_id_from_name("Acme Inc"), "acme-inc");
        assert_eq!(org_id_from_name("Café & Co. 2"), "caf--co-2");
        assert!(check_org_id(&org_id_from_name("Acme Inc")).is_ok());
        assert_eq!(org_id_from_name("Ünïcödé"), "ncd");
        // Nothing left: the prompt then has no default
        assert!(check_org_id(&org_id_from_name("日本")).is_err());
        assert_eq!(org_id_from_name("Acme &"), "acme");
        assert_eq!(org_id_from_name("& Co 🚀"), "co");
    }

    #[test]
    fn the_sign_up_requests_go_to_the_apex() {
        let apex = url::Url::parse("https://gatana.example.com/some/path").unwrap();
        assert_eq!(signup_url(&apex), "https://gatana.example.com/api/v1/cli-signup");
        let local = url::Url::parse("http://127.0.0.1:3500").unwrap();
        assert_eq!(signup_url(&local), "http://127.0.0.1:3500/api/v1/cli-signup");
    }

    #[test]
    fn answers_are_checked_as_the_backend_checks_them() {
        assert!(check_name("").is_err());
        assert!(check_name(&"x".repeat(51)).is_err());
        assert!(check_org_id("Acme").is_err());
        assert!(check_org_id(&"a".repeat(41)).is_err());
        assert!(check_org_id("acme-2").is_ok());
        assert!(check_org_id("acme-").is_err());
        assert!(check_org_id("-co").is_err());
        assert!(check_email("you@acme.com").is_ok());
        assert!(check_email("you@acme").is_err());
        assert!(check_email("you @acme.com").is_err());
    }

    #[test]
    fn the_finishing_command_repeats_the_answers_as_shell_words() {
        assert_eq!(
            finishing_command("Acme Inc", "acme-inc", "you@acme.com", None),
            "gatana signup --org-name 'Acme Inc' --org-id acme-inc --email you@acme.com --code <code>"
        );
        assert_eq!(
            finishing_command("O'Hara", "ohara", "o@x.io", Some("https://gatana.example.com")),
            "gatana signup --org-name 'O'\\''Hara' --org-id ohara --email o@x.io --base-url https://gatana.example.com --code <code>"
        );
        assert!(check_code("012345").is_ok());
        assert!(check_code("12345").is_err());
        assert!(check_code("12345a").is_err());
    }

    #[test]
    fn the_reason_is_the_field_of_a_validation_error_or_the_message() {
        let status = StatusCode::BAD_REQUEST;
        let validation =
            json!({ "message": "Validation Error", "details": [{ "message": "\"email\" must be a valid email" }] });
        assert_eq!(refusal_message(&validation, status), "\"email\" must be a valid email");
        assert_eq!(refusal_message(&json!({ "message": "Taken" }), status), "Taken");
        assert_eq!(refusal_message(&Value::Null, status), "The server answered 400 Bad Request");
    }
}
