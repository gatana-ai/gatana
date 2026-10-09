//! The Gatana CLI. `main.rs` parses the command line and hands it to `commands::run`.

pub mod apex;
pub mod cli;
pub mod commands;
pub mod config;
pub mod connect;
pub mod context;
pub mod faas;
pub mod oidc;
pub mod output;
pub mod skills;
pub mod sse;
pub mod util;
pub mod yaml;
