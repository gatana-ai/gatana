//! The organization and API client a command works against, resolved on first use: commands that
//! do not talk to Gatana (`config ls`, `hosted run`, `skills hook`) never need a configuration.

use crate::config::{self, ResolvedConfig, Strategy};
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
        Self::with_strategies(vec![Strategy::Env, Strategy::File { org_id: None }])
    }

    /// One organization from the config file: `--org`.
    pub fn for_org(org_id: &str) -> Result<Self> {
        Self::with_strategies(vec![Strategy::File { org_id: Some(org_id.to_string()) }])
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
}
