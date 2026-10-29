//! `gatana create server email`: a mailbox, as the Email card of the Add Server page creates it
//! (email-presets.ts and email-server-fields.tsx in the frontend).
//!
//! The provider sets the connection and the ways to sign in. Only another IMAP or JMAP server needs
//! an address. Each user signs in to their own mailbox, and the tool list needs no sign-in.

use super::{
    NewServer, ask, ask_slug, check_url, free_slug, help_of, new_server_request, next_steps, slug_from_url, with_scheme,
};
use crate::cli::{EmailAccess, EmailLogin, EmailProvider, EmailServerArgs};
use crate::output;
use anyhow::{Result, anyhow, bail};
use clap::ValueEnum;
use gatana_api::v2::types::{
    EmailAccessLevel, EmailImapConnection, EmailImapConnectionProtocol, EmailImapConnectionSecurity,
    EmailJmapConnection, EmailJmapConnectionProtocol, EmailPreset, EmailSmtpServer, EmailSmtpServerSecurity,
    OAuthGrantType, ServerAuthorization, ServerAuthorizationCredentialsScope, ServerAuthorizationMethod,
    ServerOAuthClientConfiguration, ServerOAuthMetadata, ServerOAuthMetadataAs, ToolRefreshCredentialPolicy,
    V2CreateServerRequest, V2CreateServerRequestTransportConfig as TransportConfig,
    V2CreateServerRequestTransportConfigConnection as Connection,
};
use std::io::IsTerminal;

/// The header that sends the API token of each user to a JMAP server (the default of the backend).
const JMAP_TOKEN_HEADER: (&str, &str) = ("Authorization", "Bearer {{ credentials.keys.token }}");
const IMAP_PORT: i64 = 993;
/// The SMTP port that a host typed by the user gets, with TLS from the start.
const SMTP_PORT: i64 = 465;

/// The answers of the user. The provider supplies the other settings.
#[derive(Debug)]
struct Mailbox {
    provider: EmailProvider,
    /// The IMAP host for the provider imap, or the session URL for the provider jmap.
    address: String,
    /// The SMTP host for the provider imap. None: the server cannot send.
    smtp_host: Option<String>,
    login: EmailLogin,
    access: EmailAccess,
}

impl NewServer<'_> {
    pub(super) async fn with_mailbox(&self, args: EmailServerArgs) -> Result<()> {
        let taken = self.taken_slugs();
        let implied = if args.session_url.is_some() {
            Some(EmailProvider::Jmap)
        } else if args.imap_host.is_some() || args.smtp_host.is_some() {
            Some(EmailProvider::Imap)
        } else {
            None
        };
        let provider = match args.provider.or(implied) {
            Some(provider) => provider,
            None => choose_provider()?,
        };
        check_address_flags(provider, &args)?;

        let (address, smtp_host) = match provider {
            EmailProvider::Imap => (
                ask(args.imap_host, "--imap-host", "IMAP host (for example imap.example.com)", None, check_host)?,
                ask_optional(args.smtp_host, "SMTP host to send mail, empty for none (for example smtp.example.com)")?,
            ),
            EmailProvider::Jmap => {
                let prompt = "Session URL (for example https://mail.example.com/.well-known/jmap)";
                (with_scheme(&ask(args.session_url, "--session-url", prompt, None, check_url)?), None)
            }
            _ => (String::new(), None),
        };
        let default = match default_slug(provider) {
            "" => slug_from_url(&address),
            slug => slug.to_string(),
        };
        let slug = ask_slug(args.server.slug.clone(), free_slug(&default, &taken), &taken)?;
        let login = choose_login(provider, args.login)?;
        let access = match args.access {
            Some(access) => access,
            None if std::io::stdin().is_terminal() => {
                let labels: Vec<String> = EmailAccess::value_variants().iter().map(|access| help_of(*access)).collect();
                choose("What can the tools do?", EmailAccess::value_variants(), &labels)?
            }
            None => EmailAccess::default(),
        };

        let mailbox = Mailbox { provider, address, smtp_host, login, access };
        self.send(email_request(&slug, &mailbox), &args.server).await?;
        if provider == EmailProvider::Imap && mailbox.smtp_host.is_none() {
            output::info("The server has no SMTP server, so it cannot send mail.");
        }
        next_steps(&self.mailbox_steps(&slug, &mailbox));
        Ok(())
    }

    fn mailbox_steps(&self, slug: &str, mailbox: &Mailbox) -> Vec<String> {
        let page = self.page(slug);
        let mut steps = Vec::new();
        if mailbox.provider == EmailProvider::Imap {
            steps.push(format!(
                "If the IMAP server does not use port {IMAP_PORT} with TLS, change it: {page}?tab=settings"
            ));
        }
        match mailbox.login {
            EmailLogin::Oauth => {
                let at =
                    if mailbox.provider == EmailProvider::Microsoft365 { "Microsoft Entra ID" } else { "Google Cloud" };
                steps.push(format!(
                    "Register an OAuth app in {at}, then enter its client ID and secret: {page}?tab=settings#oauth-issuer"
                ));
                steps.push(format!("Sign in to your mailbox: gatana create creds {slug}"));
            }
            EmailLogin::Password | EmailLogin::Token => {
                steps.extend(secret_step(mailbox));
                let (what, file, example) = if mailbox.login == EmailLogin::Token {
                    ("API token", "token.json", r#"[["token","<API token>"]]"#)
                } else {
                    (
                        "username and password",
                        "login.json",
                        r#"[["username","you@example.com"],["password","<password>"]]"#,
                    )
                };
                steps.push(format!("Write your {what} to a file, for example {file}: {example}"));
                steps.push(format!("Sign in to your mailbox with it: gatana create creds {slug} -f {file}"));
            }
        }
        if mailbox.provider == EmailProvider::Microsoft365 && mailbox.access == EmailAccess::Send {
            steps.push(
                "To send, an administrator must turn on Authenticated SMTP for each mailbox: https://learn.microsoft.com/en-us/exchange/clients-and-mobile-in-exchange-online/authenticated-client-smtp-submission"
                    .to_string(),
            );
        }
        steps.push(format!("Choose who can use it: {page}"));
        steps
    }
}

/// Where the user gets the password or the token, for the providers that need a special one.
fn secret_step(mailbox: &Mailbox) -> Option<String> {
    match (mailbox.provider, mailbox.login) {
        (EmailProvider::Gmail, EmailLogin::Password) => Some(
            "Create a Google app password. It needs 2-Step Verification: https://myaccount.google.com/apppasswords"
                .to_string(),
        ),
        (EmailProvider::Icloud, _) => Some(
            "Create an app-specific password for Gatana at https://account.apple.com, in Sign-In and Security"
                .to_string(),
        ),
        (EmailProvider::Fastmail, _) => {
            let can = if mailbox.access == EmailAccess::Send { "read and send mail" } else { "read mail" };
            Some(format!(
                "Create a Fastmail API token that can {can}: https://app.fastmail.com/settings/security/tokens"
            ))
        }
        _ => None,
    }
}

/// The address flags of one provider are an error with another one.
fn check_address_flags(provider: EmailProvider, args: &EmailServerArgs) -> Result<()> {
    let name = name_of(provider);
    if provider != EmailProvider::Imap && (args.imap_host.is_some() || args.smtp_host.is_some()) {
        bail!("--imap-host and --smtp-host are for the provider imap only. The provider {name} sets its own servers");
    }
    if provider != EmailProvider::Jmap && args.session_url.is_some() {
        bail!("--session-url is for the provider jmap only. The provider {name} sets its own servers");
    }
    Ok(())
}

fn choose_provider() -> Result<EmailProvider> {
    if !std::io::stdin().is_terminal() {
        bail!("Name the email provider, for example: gatana create server email gmail");
    }
    let providers = EmailProvider::value_variants();
    let labels: Vec<String> = providers
        .iter()
        .map(|provider| format!("{} {}", label_of(*provider), output::dim(&format!("({})", help_of(*provider)))))
        .collect();
    choose("Which email provider?", providers, &labels)
}

/// The login given, or a menu when the provider permits more than one. Without a terminal, the
/// first login of the provider.
fn choose_login(provider: EmailProvider, given: Option<EmailLogin>) -> Result<EmailLogin> {
    let allowed = logins_of(provider);
    match given {
        Some(login) if allowed.contains(&login) => Ok(login),
        Some(login) => {
            let names: Vec<String> = allowed.iter().map(|login| name_of(*login)).collect();
            bail!("{} does not permit the login {}. Use: {}", label_of(provider), name_of(login), names.join(", "))
        }
        None if allowed.len() > 1 && std::io::stdin().is_terminal() => {
            let labels: Vec<String> = allowed
                .iter()
                .map(|login| format!("{} {}", login_label(*login), output::dim(&format!("({})", help_of(*login)))))
                .collect();
            choose("How do users sign in?", allowed, &labels)
        }
        None => Ok(allowed[0]),
    }
}

fn choose<T: Copy>(prompt: &str, values: &[T], labels: &[impl std::fmt::Display]) -> Result<T> {
    let index = dialoguer::Select::new().with_prompt(prompt).items(labels).default(0).interact()?;
    Ok(values[index])
}

/// An optional value: the argument, or a prompt that accepts an empty answer. An empty value means
/// none, and so does a missing one without a terminal.
fn ask_optional(given: Option<String>, prompt: &str) -> Result<Option<String>> {
    let value = match given {
        Some(value) => value,
        None if std::io::stdin().is_terminal() => dialoguer::Input::<String>::new()
            .with_prompt(prompt)
            .allow_empty(true)
            .validate_with(|value: &String| if value.trim().is_empty() { Ok(()) } else { check_host(value.trim()) })
            .interact_text()?,
        None => return Ok(None),
    };
    let value = value.trim();
    if value.is_empty() {
        return Ok(None);
    }
    check_host(value).map_err(|problem| anyhow!("{problem}"))?;
    Ok(Some(value.to_string()))
}

/// A host name only: Gatana adds the port and the encryption.
fn check_host(value: &str) -> Result<(), String> {
    if value.is_empty() || value.contains(char::is_whitespace) || value.contains('/') {
        return Err("Enter a host name, for example mail.example.com, without a scheme or a path".into());
    }
    Ok(())
}

/// The create request, as emailServerRequest in the frontend makes it.
fn email_request(slug: &str, mailbox: &Mailbox) -> V2CreateServerRequest {
    let transport = TransportConfig::Email {
        access: Some(match mailbox.access {
            EmailAccess::Send => EmailAccessLevel::Send,
            EmailAccess::Organize => EmailAccessLevel::Organize,
            EmailAccess::Read => EmailAccessLevel::Read,
        }),
        connection: connection(mailbox),
        preset: Some(match mailbox.provider {
            EmailProvider::Gmail => EmailPreset::Gmail,
            EmailProvider::Microsoft365 => EmailPreset::Microsoft365,
            EmailProvider::Fastmail => EmailPreset::Fastmail,
            EmailProvider::Icloud => EmailPreset::Icloud,
            EmailProvider::Imap => EmailPreset::Imap,
            EmailProvider::Jmap => EmailPreset::Jmap,
        }),
    };
    let mut request = new_server_request(slug, transport);
    // Each user signs in for themselves, and the tool list needs no sign-in to refresh.
    request.authorization = Some(ServerAuthorization {
        method: match mailbox.login {
            EmailLogin::Oauth => ServerAuthorizationMethod::Oauth,
            EmailLogin::Password | EmailLogin::Token => ServerAuthorizationMethod::Apikey,
        },
        credentials_scope: ServerAuthorizationCredentialsScope::User,
        apikeys: match mailbox.login {
            EmailLogin::Password => vec!["username".to_string(), "password".to_string()],
            EmailLogin::Token => vec!["token".to_string()],
            EmailLogin::Oauth => Vec::new(),
        },
        tool_refresh_credential_policy: Some(ToolRefreshCredentialPolicy::Skip),
    });
    if let (EmailLogin::Oauth, Some((metadata, client))) = (mailbox.login, oauth(mailbox.provider)) {
        request.oauth_metadata = Some(metadata);
        request.oauth_client_configuration = Some(client);
    }
    request
}

fn connection(mailbox: &Mailbox) -> Connection {
    use EmailSmtpServerSecurity::{Starttls, Tls};
    let imap = |host: &str, smtp: Option<(&str, i64, EmailSmtpServerSecurity)>, save_sent_copy: bool| {
        Connection::ImapConnection(EmailImapConnection {
            protocol: EmailImapConnectionProtocol::Imap,
            host: Some(host.to_string()),
            port: Some(IMAP_PORT),
            security: Some(EmailImapConnectionSecurity::Tls),
            smtp: smtp.map(|(host, port, security)| EmailSmtpServer {
                host: host.to_string(),
                port: Some(port),
                security: Some(security),
            }),
            save_sent_copy: Some(save_sent_copy),
            // The defaults of the backend: the login that each user gives.
            username: None,
            password: None,
        })
    };
    let jmap = |session_url: &str| {
        Connection::JmapConnection(EmailJmapConnection {
            protocol: EmailJmapConnectionProtocol::Jmap,
            session_url: Some(session_url.to_string()),
            headers: vec![(JMAP_TOKEN_HEADER.0.to_string(), JMAP_TOKEN_HEADER.1.to_string())],
            account_id: None,
        })
    };
    match mailbox.provider {
        // Gmail files every message sent through its SMTP server in Sent by itself.
        EmailProvider::Gmail => imap("imap.gmail.com", Some(("smtp.gmail.com", 465, Tls)), false),
        // Exchange Online files mail sent through SMTP in Sent Items by itself.
        EmailProvider::Microsoft365 => {
            imap("outlook.office365.com", Some(("smtp.office365.com", 587, Starttls)), false)
        }
        EmailProvider::Fastmail => jmap("https://api.fastmail.com/jmap/session"),
        EmailProvider::Icloud => imap("imap.mail.me.com", Some(("smtp.mail.me.com", 587, Starttls)), true),
        EmailProvider::Imap => {
            imap(&mailbox.address, mailbox.smtp_host.as_deref().map(|host| (host, SMTP_PORT, Tls)), true)
        }
        EmailProvider::Jmap => jmap(&mailbox.address),
    }
}

/// The OAuth endpoints and scopes of the providers that take OAuth. The client ID and secret stay
/// empty: each organization registers its own app (GOOGLE_OAUTH and MICROSOFT_OAUTH in the frontend).
fn oauth(provider: EmailProvider) -> Option<(ServerOAuthMetadata, ServerOAuthClientConfiguration)> {
    let strings = |values: &[&str]| values.iter().map(|value| value.to_string()).collect::<Vec<_>>();
    let client = |client_auth_method: &str, scopes: &[&str]| ServerOAuthClientConfiguration {
        client_id: Some(String::new()),
        client_secret: Some(String::new()),
        grant_type: OAuthGrantType::AuthorizationCode,
        client_auth_method: client_auth_method.to_string(),
        scopes: Some(scopes.join(" ")),
    };
    let (issuer, client) = match provider {
        EmailProvider::Gmail => {
            // "email" names the mailbox to open. "https://mail.google.com/" is the only scope that IMAP
            // and SMTP accept.
            let scopes = ["openid", "email", "https://mail.google.com/"];
            let issuer = ServerOAuthMetadataAs {
                issuer: Some("https://accounts.google.com".to_string()),
                authorize_endpoint: Some("https://accounts.google.com/o/oauth2/v2/auth".to_string()),
                token_endpoint: Some("https://oauth2.googleapis.com/token".to_string()),
                // Google gives a refresh token only for offline access, and again only on consent.
                extra_authorization_parameters: Some("access_type=offline&prompt=consent".to_string()),
                supports_pkce: Some(true),
                supported_client_auth_methods: strings(&["client_secret_post", "client_secret_basic"]),
                available_scopes: strings(&scopes),
                service_documentation: Some(
                    "https://developers.google.com/workspace/gmail/imap/xoauth2-protocol".to_string(),
                ),
                ..ServerOAuthMetadataAs::default()
            };
            (issuer, client("client_secret_post", &scopes))
        }
        EmailProvider::Microsoft365 => {
            let scopes = [
                "openid",
                "email",
                "offline_access",
                "https://outlook.office.com/IMAP.AccessAsUser.All",
                "https://outlook.office.com/SMTP.Send",
            ];
            // "organizations" stands in for the directory of the organization, which the settings page
            // tells the administrator to put in.
            let issuer = ServerOAuthMetadataAs {
                issuer: Some("https://login.microsoftonline.com/organizations/v2.0".to_string()),
                authorize_endpoint: Some(
                    "https://login.microsoftonline.com/organizations/oauth2/v2.0/authorize".to_string(),
                ),
                token_endpoint: Some("https://login.microsoftonline.com/organizations/oauth2/v2.0/token".to_string()),
                supports_pkce: Some(true),
                supported_client_auth_methods: strings(&["client_secret_post"]),
                available_scopes: strings(&scopes),
                service_documentation: Some("https://learn.microsoft.com/en-us/exchange/client-developer/legacy-protocols/how-to-authenticate-an-imap-pop-smtp-application-by-using-oauth".to_string()),
                ..ServerOAuthMetadataAs::default()
            };
            (issuer, client("client_secret_post", &scopes))
        }
        _ => return None,
    };
    Some((ServerOAuthMetadata { as_: Some(issuer), resource: None }, client))
}

/// The name on the dashboard.
fn label_of(provider: EmailProvider) -> &'static str {
    match provider {
        EmailProvider::Gmail => "Gmail",
        EmailProvider::Microsoft365 => "Microsoft 365",
        EmailProvider::Fastmail => "Fastmail",
        EmailProvider::Icloud => "iCloud Mail",
        EmailProvider::Imap => "Other IMAP server",
        EmailProvider::Jmap => "Other JMAP server",
    }
}

/// The slug that the server gets. Empty: the slug comes from the address that the user types.
fn default_slug(provider: EmailProvider) -> &'static str {
    match provider {
        EmailProvider::Gmail => "gmail",
        EmailProvider::Microsoft365 => "outlook",
        EmailProvider::Fastmail => "fastmail",
        EmailProvider::Icloud => "icloud",
        EmailProvider::Imap | EmailProvider::Jmap => "",
    }
}

/// The ways to sign in that the provider permits. The first one is the default.
fn logins_of(provider: EmailProvider) -> &'static [EmailLogin] {
    match provider {
        EmailProvider::Gmail => &[EmailLogin::Password, EmailLogin::Oauth],
        EmailProvider::Microsoft365 => &[EmailLogin::Oauth],
        EmailProvider::Fastmail | EmailProvider::Jmap => &[EmailLogin::Token],
        EmailProvider::Icloud | EmailProvider::Imap => &[EmailLogin::Password],
    }
}

fn login_label(login: EmailLogin) -> &'static str {
    match login {
        EmailLogin::Password => "Email and password",
        EmailLogin::Token => "API token",
        EmailLogin::Oauth => "OAuth",
    }
}

/// The value as the command line takes it.
fn name_of(value: impl ValueEnum) -> String {
    value.to_possible_value().map(|value| value.get_name().to_string()).unwrap_or_default()
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::{Value, json};

    fn mailbox(provider: EmailProvider, login: EmailLogin) -> Mailbox {
        Mailbox { provider, address: String::new(), smtp_host: None, login, access: EmailAccess::Send }
    }

    fn request_json(slug: &str, mailbox: &Mailbox) -> Value {
        serde_json::to_value(email_request(slug, mailbox)).unwrap()
    }

    #[test]
    fn gmail_with_a_password_is_the_request_of_the_dashboard() {
        let request = request_json("gmail", &mailbox(EmailProvider::Gmail, EmailLogin::Password));
        assert_eq!(
            request["transportConfig"],
            json!({
                "type": "email",
                "preset": "gmail",
                "access": "send",
                "connection": {
                    "protocol": "imap",
                    "host": "imap.gmail.com",
                    "port": 993,
                    "security": "tls",
                    "smtp": { "host": "smtp.gmail.com", "port": 465, "security": "tls" },
                    "saveSentCopy": false,
                },
            })
        );
        assert_eq!(
            request["authorization"],
            json!({
                "method": "apikey",
                "credentialsScope": "user",
                "apikeys": ["username", "password"],
                "toolRefreshCredentialPolicy": "skip",
            })
        );
        assert!(request.get("oauthMetadata").is_none());
    }

    #[test]
    fn oauth_sends_the_endpoints_and_an_empty_client() {
        let request = request_json("outlook", &mailbox(EmailProvider::Microsoft365, EmailLogin::Oauth));
        assert_eq!(request["authorization"]["method"], "oauth");
        assert!(request["authorization"].get("apikeys").is_none());
        assert_eq!(request["oauthMetadata"]["as"]["issuer"], "https://login.microsoftonline.com/organizations/v2.0");
        assert_eq!(request["oauthClientConfiguration"]["clientId"], "");
        assert_eq!(request["oauthClientConfiguration"]["grantType"], "authorization_code");
        let scopes = request["oauthClientConfiguration"]["scopes"].as_str().unwrap();
        assert!(scopes.ends_with("https://outlook.office.com/SMTP.Send"), "{scopes}");
        assert_eq!(request["transportConfig"]["connection"]["smtp"]["security"], "starttls");
    }

    #[test]
    fn another_imap_server_sends_only_with_an_smtp_host() {
        let mut other = mailbox(EmailProvider::Imap, EmailLogin::Password);
        other.address = "imap.example.com".to_string();
        other.access = EmailAccess::Organize;
        let request = request_json("example", &other);
        let connection = &request["transportConfig"]["connection"];
        assert_eq!(connection["host"], "imap.example.com");
        assert!(connection.get("smtp").is_none());
        assert_eq!(request["transportConfig"]["access"], "organize");
        other.smtp_host = Some("smtp.example.com".to_string());
        let request = request_json("example", &other);
        assert_eq!(
            request["transportConfig"]["connection"]["smtp"],
            json!({ "host": "smtp.example.com", "port": 465, "security": "tls" })
        );
    }

    #[test]
    fn jmap_sends_the_token_of_each_user() {
        let mut other = mailbox(EmailProvider::Jmap, EmailLogin::Token);
        other.address = "https://mail.example.com/.well-known/jmap".to_string();
        let request = request_json("example", &other);
        assert_eq!(
            request["transportConfig"]["connection"],
            json!({
                "protocol": "jmap",
                "sessionUrl": "https://mail.example.com/.well-known/jmap",
                "headers": [["Authorization", "Bearer {{ credentials.keys.token }}"]],
            })
        );
        assert_eq!(request["authorization"]["apikeys"], json!(["token"]));
    }

    #[test]
    fn a_login_that_the_provider_does_not_permit_is_an_error() {
        assert_eq!(choose_login(EmailProvider::Gmail, Some(EmailLogin::Oauth)).unwrap(), EmailLogin::Oauth);
        let error = choose_login(EmailProvider::Microsoft365, Some(EmailLogin::Password)).unwrap_err().to_string();
        assert_eq!(error, "Microsoft 365 does not permit the login password. Use: oauth");
        // Only one login: no menu, also in a terminal
        assert_eq!(choose_login(EmailProvider::Fastmail, None).unwrap(), EmailLogin::Token);
    }

    #[test]
    fn address_flags_belong_to_their_provider() {
        let args = EmailServerArgs { smtp_host: Some("smtp.example.com".into()), ..EmailServerArgs::default() };
        assert!(check_address_flags(EmailProvider::Imap, &args).is_ok());
        let error = check_address_flags(EmailProvider::Gmail, &args).unwrap_err().to_string();
        assert!(error.contains("The provider gmail sets its own servers"), "{error}");
        let args =
            EmailServerArgs { session_url: Some("https://mail.example.com".into()), ..EmailServerArgs::default() };
        assert!(check_address_flags(EmailProvider::Jmap, &args).is_ok());
        assert!(check_address_flags(EmailProvider::Fastmail, &args).is_err());
    }

    #[test]
    fn hosts_have_no_scheme_or_path() {
        assert!(check_host("imap.example.com").is_ok());
        assert!(check_host("imaps://imap.example.com").is_err());
        assert!(check_host("imap example.com").is_err());
        assert!(check_host("").is_err());
    }

    #[test]
    fn every_login_of_a_provider_has_a_name() {
        for provider in EmailProvider::value_variants() {
            assert!(!logins_of(*provider).is_empty());
            for login in logins_of(*provider) {
                assert!(!name_of(*login).is_empty());
            }
            // The providers with OAuth have its endpoints
            assert_eq!(logins_of(*provider).contains(&EmailLogin::Oauth), oauth(*provider).is_some());
        }
    }
}
