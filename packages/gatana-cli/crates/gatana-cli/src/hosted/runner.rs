//! Runs hosted server source code on this machine with Node.js, for `hosted verify` and
//! `hosted run`. The code is JavaScript, so this is the one part of the CLI that needs `node`.
//!
//! The hosted runtime provides `zod`. When the source folder cannot resolve it, the CLI installs
//! it once into its cache folder with npm and links it into the source folder for the run, as the
//! TypeScript CLI did with its own copy.

use anyhow::{Context, Result, anyhow, bail};
use serde_json::Value;
use std::path::{Path, PathBuf};
use std::process::Stdio;
use tokio::process::Command;

const RUNNER: &str = include_str!("runner.mjs");
/// Dependencies the hosted runtime has pre-installed.
const RUNTIME_DEPS: [&str; 1] = ["zod"];

/// `node` is not on the PATH.
#[derive(Debug, thiserror::Error)]
#[error(
    "Node.js is needed to run hosted server code on this machine. Install it from https://nodejs.org and try again."
)]
pub struct NodeMissing;

pub fn is_node_missing(error: &anyhow::Error) -> bool {
    error.downcast_ref::<NodeMissing>().is_some()
}

pub enum Mode<'a> {
    Verify,
    Run { tool: &'a str, input: &'a Value },
}

/// What the runner reported.
pub struct Outcome {
    pub ok: bool,
    pub result: Value,
    pub error: Option<String>,
    pub stage: Option<String>,
    pub issues: Vec<(String, String)>,
    pub expected: Option<Value>,
}

fn npm() -> &'static str {
    if cfg!(windows) { "npm.cmd" } else { "npm" }
}

async fn node_available() -> bool {
    Command::new("node")
        .arg("--version")
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .await
        .is_ok_and(|status| status.success())
}

fn cache_dir() -> PathBuf {
    let home = std::env::home_dir().unwrap_or_default();
    if let Some(dir) = std::env::var_os("XDG_CACHE_HOME").filter(|dir| !dir.is_empty()) {
        return PathBuf::from(dir).join("gatana");
    }
    if cfg!(target_os = "macos") {
        return home.join("Library/Caches/gatana");
    }
    if cfg!(windows)
        && let Some(dir) = std::env::var_os("LOCALAPPDATA")
    {
        return PathBuf::from(dir).join("gatana");
    }
    home.join(".cache/gatana")
}

/// True when Node would resolve the package from the folder: a node_modules in it or above.
fn resolvable(source: &Path, package: &str) -> bool {
    source.ancestors().any(|dir| dir.join("node_modules").join(package).join("package.json").is_file())
}

/// The cached copy of a runtime dependency, installed on first use.
async fn cached_dependency(package: &str) -> Result<PathBuf> {
    let root = cache_dir().join("hosted-runtime");
    let path = root.join("node_modules").join(package);
    if path.join("package.json").is_file() {
        return Ok(path);
    }
    std::fs::create_dir_all(&root)?;
    crate::output::eprintln(&format!("Installing {package} for local runs into {} (once)...", root.display()));
    let status = Command::new(npm())
        .args(["install", "--prefix"])
        .arg(&root)
        .args(["--no-audit", "--no-fund", "--no-package-lock", "--silent", &format!("{package}@^4")])
        .stdin(Stdio::null())
        .status()
        .await
        .with_context(|| format!("could not run npm to install {package}"))?;
    if !status.success() || !path.join("package.json").is_file() {
        bail!("npm could not install {package}. Install it in the source folder instead: npm install {package}");
    }
    Ok(path)
}

/// Links the runtime dependencies the source folder lacks; the links are removed again on drop.
struct LinkedDependencies {
    links: Vec<PathBuf>,
    created_node_modules: Option<PathBuf>,
}

impl LinkedDependencies {
    async fn link(source: &Path) -> Result<Self> {
        let mut linked = Self { links: Vec::new(), created_node_modules: None };
        for package in RUNTIME_DEPS {
            if resolvable(source, package) {
                continue;
            }
            let target = cached_dependency(package).await?;
            let node_modules = source.join("node_modules");
            if !node_modules.exists() {
                std::fs::create_dir_all(&node_modules)?;
                linked.created_node_modules = Some(node_modules.clone());
            }
            let link = node_modules.join(package);
            #[cfg(unix)]
            std::os::unix::fs::symlink(&target, &link)?;
            #[cfg(windows)]
            std::os::windows::fs::symlink_dir(&target, &link)?;
            linked.links.push(link);
        }
        Ok(linked)
    }
}

impl Drop for LinkedDependencies {
    fn drop(&mut self) {
        for link in &self.links {
            let _ = std::fs::remove_file(link).or_else(|_| std::fs::remove_dir(link));
        }
        if let Some(node_modules) = &self.created_node_modules {
            // Only when empty: something else may have been installed meanwhile.
            let _ = std::fs::remove_dir(node_modules);
        }
    }
}

pub async fn run(source: &Path, mode: Mode<'_>) -> Result<Outcome> {
    if !node_available().await {
        return Err(NodeMissing.into());
    }
    let scratch = tempfile::tempdir()?;
    let runner = scratch.path().join("runner.mjs");
    let result_file = scratch.path().join("result.json");
    std::fs::write(&runner, RUNNER)?;

    let mut command = Command::new("node");
    command.arg(&runner);
    match &mode {
        Mode::Verify => {
            command.arg("verify").arg(source).arg(&result_file);
        }
        Mode::Run { tool, input } => {
            let input_file = scratch.path().join("input.json");
            std::fs::write(&input_file, serde_json::to_string(input)?)?;
            command.arg("run").arg(source).arg(&result_file).arg(tool).arg(&input_file);
        }
    }
    let linked = LinkedDependencies::link(source).await?;
    let status = command.stdin(Stdio::inherit()).status().await.context("could not start node")?;
    drop(linked);

    let text = std::fs::read_to_string(&result_file)
        .map_err(|_| anyhow!("node exited ({status}) without a result; the module may have crashed while loading"))?;
    let value: Value = serde_json::from_str(&text).context("the runner wrote an unreadable result")?;
    let issues = value
        .get("issues")
        .and_then(Value::as_array)
        .map(|issues| {
            issues
                .iter()
                .map(|issue| {
                    let text = |key: &str| issue.get(key).and_then(Value::as_str).unwrap_or_default().to_string();
                    (text("path"), text("message"))
                })
                .collect()
        })
        .unwrap_or_default();
    Ok(Outcome {
        ok: value.get("ok").and_then(Value::as_bool).unwrap_or(false),
        result: value.get("result").cloned().unwrap_or(Value::Null),
        error: value.get("error").and_then(Value::as_str).map(str::to_string),
        stage: value.get("stage").and_then(Value::as_str).map(str::to_string),
        issues,
        expected: value.get("expected").cloned(),
    })
}
