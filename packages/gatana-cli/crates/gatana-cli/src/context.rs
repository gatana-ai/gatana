//! The organization and API client a command works against, resolved on first use: commands that
//! do not talk to Gatana (`config ls`, `faas run`, `skills hook`) never need a configuration.

use crate::config::{self, Credentials, ResolvedConfig, Strategy};
use anyhow::{Context as _, Result, anyhow};
use std::time::Duration;
use tokio::sync::OnceCell;

pub struct Context {
    strategies: Vec<Strategy>,
    http: reqwest::Client,
    config: std::sync::OnceLock<Result<ResolvedConfig, String>>,
    api: OnceCell<gatana_api::Client>,
}

pub fn http_client() -> Result<reqwest::Client> {
    reqwest::Client::builder()
        .user_agent(concat!("gatana-cli/", env!("CARGO_PKG_VERSION")))
        .connect_timeout(Duration::from_secs(30))
        .build()
        .context("could not set up the HTTP client")
}

impl Context {
    /// Environment variables first, then the config file.
    pub fn new() -> Result<Self> {
        Self::with_strategies(vec![Strategy::Env, Strategy::File { selector: None }])
    }

    /// One organization from the config file, by its saved name or address: `--org`.
    pub fn for_org(selector: &str) -> Result<Self> {
        Self::with_strategies(vec![Strategy::File { selector: Some(selector.to_string()) }])
    }

    fn with_strategies(strategies: Vec<Strategy>) -> Result<Self> {
        Ok(Self { strategies, http: http_client()?, config: std::sync::OnceLock::new(), api: OnceCell::new() })
    }

    pub fn strategies(&self) -> &[Strategy] {
        &self.strategies
    }

    pub fn http(&self) -> &reqwest::Client {
        &self.http
    }

    pub fn config(&self) -> Result<&ResolvedConfig> {
        self.config
            .get_or_init(|| config::resolve(&self.strategies).map_err(|error| error.to_string()))
            .as_ref()
            .map_err(|message| anyhow!("{message}"))
    }

    /// The authenticated client; the token is fetched (or refreshed) on the first call.
    pub async fn api(&self) -> Result<&gatana_api::Client> {
        self.api
            .get_or_try_init(|| async {
                let config = self.config()?;
                gatana_api::debug!("gatana", "using {} at {}", config.org_id, config.base_url);
                let token = config.token(&self.http).await?;
                Ok(gatana_api::Client::new(self.http.clone(), &config.base_url, token)?)
            })
            .await
    }

    /// Gatana answers a revoked or unknown token with a bare "Unauthorized". When the error is that
    /// answer to this context's credentials, it says which credentials they are and how to replace them.
    pub fn explain_unauthorized(&self, error: anyhow::Error) -> anyhow::Error {
        let Some(Ok(config)) = self.config.get() else {
            return error;
        };
        let base = url::Url::parse(&config.base_url).ok();
        let refused = error.chain().filter_map(|cause| cause.downcast_ref::<gatana_api::Error>()).any(|cause| {
            matches!(cause, gatana_api::Error::Status { status, url, .. }
                if *status == reqwest::StatusCode::UNAUTHORIZED
                    && base.as_ref().is_some_and(|base| base.origin() == url.origin()))
        });
        if !refused {
            return error;
        }
        let advice = match &config.credentials {
            Credentials::ApiKey(_) => "Gatana does not accept the key in GATANA_API_KEY".to_string(),
            Credentials::File { name, .. } => format!(
                "The login saved for {name} no longer works. Run \"{}\" to sign in again",
                config::login_command(&config.org_id, &config.base_url)
            ),
        };
        anyhow!("{error:#}. {advice}")
    }
}
