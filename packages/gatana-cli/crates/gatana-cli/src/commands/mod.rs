//! What each command does.

mod config;
mod resources;
mod servers;
mod skills;

use crate::cli::{Cli, Command};
use crate::context::Context;
use anyhow::Result;
use serde_json::Value;

/// An error that was already reported: the process exits with 1 and prints nothing more.
#[derive(Debug)]
pub struct Silent;

impl std::fmt::Display for Silent {
    fn fmt(&self, _: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        Ok(())
    }
}

impl std::error::Error for Silent {}

pub async fn run(cli: Cli) -> Result<()> {
    let context = Context::new()?;
    match cli.command {
        Command::Get { resource } => resources::get(&context, resource).await,
        Command::Describe { resource } => resources::describe(&context, resource).await,
        Command::Create { resource } => resources::create(&context, resource).await,
        Command::Delete { resource } => resources::delete(&context, resource).await,
        Command::Patch { resource } => resources::patch(&context, resource).await,
        Command::Tools(args) => servers::call_tool(&context, args).await,
        Command::Deployment { command } => servers::deployment(&context, command).await,
        Command::Creds(args) => servers::effective_credentials(&context, args).await,
        Command::Hosted { command } => servers::hosted(&context, command).await,
        Command::Sandbox { command } => servers::sandbox(&context, command).await,
        Command::Skills { command } => skills::run(&context, command).await,
        Command::Config { command } => config::run(&context, command).await,
        Command::AuthInfo => config::auth_info(&context).await,
        Command::Schema { command } => config::schema(&context, command).await,
    }
}

/// A string at a JSON pointer, for the few fields read from responses kept raw.
pub(crate) fn text_at<'a>(value: &'a Value, pointer: &str) -> Option<&'a str> {
    value.pointer(pointer).and_then(Value::as_str)
}
