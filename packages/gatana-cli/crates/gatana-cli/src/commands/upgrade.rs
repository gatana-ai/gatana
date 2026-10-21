//! `gatana upgrade`: replace this gatana with the latest release, through the channel it came from.
//!
//! The path of the running binary tells the channel. npm, pnpm and bun keep it in a package folder,
//! Homebrew keeps it in its Cellar, and install.sh puts a plain file in a bin folder. Every release
//! goes to all of them, and the GitHub release is the first, so the version check asks GitHub.

use crate::cli::UpgradeArgs;
use crate::context::Context;
use crate::output;
use anyhow::{Context as _, Result, anyhow, bail};
use sha2::{Digest, Sha256};
use std::cmp::Ordering;
use std::io::Read;
use std::path::{Path, PathBuf};
use std::process::Stdio;
use tokio::process::Command;

const REPO: &str = "https://github.com/gatana-ai/gatana";
const CURRENT: &str = env!("CARGO_PKG_VERSION");

/// How this binary was installed, and so how it is upgraded.
#[derive(Debug, PartialEq)]
enum Install {
    /// install.sh, or a release binary put in place by hand: the file is replaced with a new download.
    Download,
    /// `npm install -g` into this prefix. The upgrade goes to the same prefix, also when a Node
    /// version manager (nvm, fnm) has made another Node the active one since.
    Npm {
        prefix: PathBuf,
    },
    Pnpm,
    Bun,
    /// Homebrew with this prefix, so that brew runs and not another one on the PATH.
    Homebrew {
        prefix: PathBuf,
    },
    /// A copy that the upgrade does not change: why, and what to do instead.
    Unmanaged(String),
}

impl Install {
    fn describe(&self) -> String {
        match self {
            Install::Download => "installed with install.sh (a release download)".to_string(),
            Install::Npm { prefix } => format!("installed with npm (global, prefix {})", output::tilde(prefix)),
            Install::Pnpm => "installed with pnpm (global)".to_string(),
            Install::Bun => "installed with bun (global)".to_string(),
            Install::Homebrew { .. } => "installed with Homebrew (gatana-ai/tap/gatana)".to_string(),
            Install::Unmanaged(_) => "not installed by a package manager that gatana can run".to_string(),
        }
    }

    /// The commands that upgrade a package-manager install, in order.
    fn commands(&self) -> Vec<(PathBuf, Vec<String>)> {
        let args = |args: &[&str]| args.iter().map(|arg| arg.to_string()).collect::<Vec<_>>();
        match self {
            Install::Npm { prefix } => {
                let mut npm_args = args(&["install", "--global", "--prefix"]);
                npm_args.push(prefix.display().to_string());
                npm_args.push("gatana@latest".to_string());
                vec![(own_tool(prefix, "npm"), npm_args)]
            }
            Install::Pnpm => vec![(PathBuf::from("pnpm"), args(&["add", "--global", "gatana@latest"]))],
            Install::Bun => vec![(PathBuf::from("bun"), args(&["add", "--global", "gatana@latest"]))],
            // brew upgrade updates the taps only when its last update is older than a day, so it
            // would miss a release from today: update first.
            Install::Homebrew { prefix } => vec![
                (own_tool(prefix, "brew"), args(&["update", "--quiet"])),
                (own_tool(prefix, "brew"), args(&["upgrade", "gatana-ai/tap/gatana"])),
            ],
            Install::Download | Install::Unmanaged(_) => Vec::new(),
        }
    }
}

/// `<prefix>/bin/<tool>` when it is there, else the tool from the PATH.
fn own_tool(prefix: &Path, tool: &str) -> PathBuf {
    let own = prefix.join("bin").join(tool);
    if own.is_file() { own } else { PathBuf::from(tool) }
}

pub async fn run(context: &Context, args: UpgradeArgs) -> Result<()> {
    let binary = std::env::current_exe()
        .and_then(std::fs::canonicalize)
        .context("could not find the file of the running gatana")?;
    let install = detect(&binary);
    output::info(&format!("gatana {CURRENT} at {}, {}", output::tilde(&binary), install.describe()));
    if let Install::Unmanaged(advice) = install {
        bail!(advice);
    }

    let latest = latest_version().await?;
    if !newer(&latest, CURRENT) {
        if newer(CURRENT, &latest) {
            output::info(&format!("This version is newer than the latest release, {latest}. Nothing to upgrade."));
        } else {
            output::success(&format!("gatana {CURRENT} is the latest release."));
        }
        return Ok(());
    }
    output::info(&format!("The latest release is {latest}."));

    if install == Install::Download {
        return replace_binary(context, &binary, &latest, args.dry_run).await;
    }
    for (program, program_args) in install.commands() {
        let line = format!("{} {}", program.display(), program_args.join(" "));
        if args.dry_run {
            output::info(&format!("Would run: {line}"));
            continue;
        }
        output::info(&format!("Running: {line}"));
        let status = Command::new(&program)
            .args(&program_args)
            .stdin(Stdio::inherit())
            .status()
            .await
            .with_context(|| format!("could not start {}", program.display()))?;
        if !status.success() {
            bail!("{line} failed ({status})");
        }
    }
    if !args.dry_run {
        output::success(&format!("Upgraded gatana to {latest}."));
    }
    Ok(())
}

/// The channel, from the real path of the binary (symlinks resolved).
fn detect(binary: &Path) -> Install {
    let text = binary.to_string_lossy();
    let before = |marker: &str| text.find(marker).map(|at| PathBuf::from(&text[..at]));
    let has_dir = |name: &str| binary.iter().any(|part| part == name);

    if let Some(prefix) = before("/Cellar/gatana/") {
        return Install::Homebrew { prefix };
    }
    if has_dir("node_modules") {
        if text.contains("/.bun/install/global/") {
            return Install::Bun;
        }
        if has_dir(".pnpm") && has_dir("global") {
            return Install::Pnpm;
        }
        // npm installs a global package with its dependencies nested: <prefix>/lib/node_modules/gatana/node_modules/@gatana/cli-…
        if let Some(prefix) = before("/lib/node_modules/gatana/") {
            return Install::Npm { prefix };
        }
        if text.contains("/_npx/") {
            return Install::Unmanaged(
                "This gatana runs from the npx cache. Run npx gatana@latest instead.".to_string(),
            );
        }
        let project = before("/node_modules/").unwrap_or_default();
        return Install::Unmanaged(format!(
            "This gatana is a dependency of the project in {}. Upgrade it there, for example with npm install gatana@latest.",
            output::tilde(&project)
        ));
    }

    let parent = binary.parent().unwrap_or(Path::new(""));
    let build = parent.file_name().is_some_and(|name| name == "release" || name == "debug")
        && parent.ancestors().skip(1).take(2).any(|dir| dir.file_name().is_some_and(|name| name == "target"));
    if build {
        return Install::Unmanaged(format!(
            "This gatana is a build from source in {}. Pull the source and build it again.",
            output::tilde(parent)
        ));
    }
    let cargo_home = std::env::var_os("CARGO_HOME")
        .filter(|dir| !dir.is_empty())
        .map(PathBuf::from)
        .unwrap_or_else(|| std::env::home_dir().unwrap_or_default().join(".cargo"));
    if parent == cargo_home.join("bin") {
        return Install::Unmanaged(
            "This gatana was installed with cargo install. Run cargo install again.".to_string(),
        );
    }
    Install::Download
}

/// The version of the latest GitHub release: GitHub answers /releases/latest with a redirect to
/// its tag, gatana@<version>. Other packages in the repository release with --latest=false.
async fn latest_version() -> Result<String> {
    let url = format!("{REPO}/releases/latest");
    // Not the shared client: that one follows the redirect.
    let client = reqwest::Client::builder()
        .user_agent(concat!("gatana-cli/", env!("CARGO_PKG_VERSION")))
        .redirect(reqwest::redirect::Policy::none())
        .build()
        .context("could not set up the HTTP client")?;
    let response = client.get(&url).send().await.with_context(|| format!("could not reach {url}"))?;
    let location = response.headers().get(reqwest::header::LOCATION).and_then(|value| value.to_str().ok());
    location
        .and_then(version_from_tag_url)
        .ok_or_else(|| anyhow!("{url} did not point to a gatana release ({})", response.status()))
}

fn version_from_tag_url(location: &str) -> Option<String> {
    let tag = location.rsplit_once("/tag/")?.1.replace("%40", "@");
    tag.strip_prefix("gatana@").filter(|version| !version.is_empty()).map(str::to_string)
}

/// True when `version` is a later release than `than`. A pre-release (4.2.0-alpha.0) comes before
/// its release (4.2.0).
fn newer(version: &str, than: &str) -> bool {
    fn parse(version: &str) -> (Vec<u64>, Option<&str>) {
        let (core, pre) = match version.split_once('-') {
            Some((core, pre)) => (core, Some(pre)),
            None => (version, None),
        };
        (core.split('.').map(|part| part.parse().unwrap_or(0)).collect(), pre)
    }
    let (core, pre) = parse(version);
    let (than_core, than_pre) = parse(than);
    match core.cmp(&than_core) {
        Ordering::Equal => match (pre, than_pre) {
            (None, Some(_)) => true,
            (Some(pre), Some(than_pre)) => pre > than_pre,
            _ => false,
        },
        order => order == Ordering::Greater,
    }
}

/// What install.sh does: download the archive for this machine, check it against its .sha256
/// file, and rename the new binary over the old one. A gatana that is running keeps its file.
async fn replace_binary(context: &Context, binary: &Path, version: &str, dry_run: bool) -> Result<()> {
    let file = format!("gatana-{}.tar.gz", release_target()?);
    let url = format!("{REPO}/releases/download/gatana%40{version}/{file}");
    if dry_run {
        output::info(&format!("Would download {url} and replace {}", output::tilde(binary)));
        return Ok(());
    }

    output::info(&format!("Downloading {url}"));
    let archive = download(context, &url).await?;
    let checksum = download(context, &format!("{url}.sha256")).await?;
    let expected = String::from_utf8_lossy(&checksum).split_whitespace().next().unwrap_or_default().to_lowercase();
    let actual: String = Sha256::digest(&archive).iter().map(|byte| format!("{byte:02x}")).collect();
    if expected != actual {
        bail!("the checksum of {file} does not match (expected {expected}, got {actual})");
    }

    let dir = binary.parent().ok_or_else(|| anyhow!("{} has no folder", binary.display()))?;
    let staged = dir.join(".gatana.new");
    write_executable(&staged, &unpack(&archive)?).map_err(|error| {
        if error.kind() == std::io::ErrorKind::PermissionDenied {
            anyhow!("cannot write to {}: permission denied. Run sudo gatana upgrade", dir.display())
        } else {
            anyhow!(error).context(format!("could not write {}", staged.display()))
        }
    })?;

    // The old binary stays until the new one has shown that it starts and is the right version.
    let reported = Command::new(&staged).arg("--version").output().await;
    let reported = reported.map(|out| String::from_utf8_lossy(&out.stdout).trim().to_string()).unwrap_or_default();
    if reported != format!("gatana {version}") {
        let _ = std::fs::remove_file(&staged);
        bail!("the downloaded binary did not report gatana {version} (it said '{reported}'); nothing was changed");
    }
    std::fs::rename(&staged, binary).with_context(|| format!("could not replace {}", binary.display()))?;
    output::success(&format!("Upgraded gatana {CURRENT} to {version} at {}", output::tilde(binary)));
    Ok(())
}

/// The release target for this machine, as scripts/dist.sh names it.
fn release_target() -> Result<&'static str> {
    Ok(match (std::env::consts::OS, std::env::consts::ARCH) {
        ("macos", "aarch64") => "aarch64-apple-darwin",
        ("macos", "x86_64") => "x86_64-apple-darwin",
        ("linux", "aarch64") => "aarch64-unknown-linux-musl",
        ("linux", "x86_64") => "x86_64-unknown-linux-musl",
        (os, arch) => bail!("there is no gatana release binary for {os} on {arch}"),
    })
}

async fn download(context: &Context, url: &str) -> Result<Vec<u8>> {
    let response = context.http().get(url).send().await.with_context(|| format!("could not download {url}"))?;
    let response = response.error_for_status().with_context(|| format!("could not download {url}"))?;
    Ok(response.bytes().await.with_context(|| format!("could not download {url}"))?.to_vec())
}

/// The `gatana` file from a release archive.
fn unpack(archive: &[u8]) -> Result<Vec<u8>> {
    let mut tar = tar::Archive::new(flate2::read::GzDecoder::new(archive));
    for entry in tar.entries().context("could not read the release archive")? {
        let mut entry = entry.context("could not read the release archive")?;
        if entry.path()?.as_os_str() == "gatana" {
            let mut bytes = Vec::new();
            entry.read_to_end(&mut bytes).context("could not read the release archive")?;
            return Ok(bytes);
        }
    }
    bail!("the release archive holds no gatana binary")
}

fn write_executable(path: &Path, bytes: &[u8]) -> std::io::Result<()> {
    std::fs::write(path, bytes)?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        std::fs::set_permissions(path, std::fs::Permissions::from_mode(0o755))?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_path_of_the_binary_tells_how_it_was_installed() {
        assert_eq!(detect(Path::new("/Users/me/.local/bin/gatana")), Install::Download);
        assert_eq!(detect(Path::new("/usr/local/bin/gatana")), Install::Download);
        assert_eq!(
            detect(Path::new("/opt/homebrew/Cellar/gatana/4.1.1/bin/gatana")),
            Install::Homebrew { prefix: PathBuf::from("/opt/homebrew") }
        );
        assert_eq!(
            detect(Path::new("/home/linuxbrew/.linuxbrew/Cellar/gatana/4.1.1/bin/gatana")),
            Install::Homebrew { prefix: PathBuf::from("/home/linuxbrew/.linuxbrew") }
        );
        assert_eq!(
            detect(Path::new(
                "/Users/me/.local/share/fnm/node-versions/v26.12.0/installation/lib/node_modules/gatana/node_modules/@gatana/cli-darwin-arm64/bin/gatana"
            )),
            Install::Npm { prefix: PathBuf::from("/Users/me/.local/share/fnm/node-versions/v26.12.0/installation") }
        );
        assert_eq!(
            detect(Path::new(
                "/Users/me/Library/pnpm/global/5/.pnpm/@gatana+cli-darwin-arm64@4.1.1/node_modules/@gatana/cli-darwin-arm64/bin/gatana"
            )),
            Install::Pnpm
        );
        assert_eq!(
            detect(Path::new("/Users/me/.bun/install/global/node_modules/@gatana/cli-darwin-arm64/bin/gatana")),
            Install::Bun
        );
        for unmanaged in [
            "/Users/me/.npm/_npx/0a1b2c/node_modules/@gatana/cli-darwin-arm64/bin/gatana",
            "/Users/me/project/node_modules/@gatana/cli-darwin-arm64/bin/gatana",
            "/Users/me/dev/gatana-js/packages/gatana-cli/target/release/gatana",
            "/Users/me/dev/gatana-js/packages/gatana-cli/target/aarch64-apple-darwin/release/gatana",
        ] {
            assert!(matches!(detect(Path::new(unmanaged)), Install::Unmanaged(_)), "{unmanaged}");
        }
    }

    #[test]
    fn the_latest_version_comes_from_the_tag_in_the_redirect() {
        let tag = "https://github.com/gatana-ai/gatana/releases/tag/gatana@4.1.1";
        assert_eq!(version_from_tag_url(tag).as_deref(), Some("4.1.1"));
        let encoded = "https://github.com/gatana-ai/gatana/releases/tag/gatana%404.2.0-alpha.0";
        assert_eq!(version_from_tag_url(encoded).as_deref(), Some("4.2.0-alpha.0"));
        assert_eq!(version_from_tag_url("https://github.com/gatana-ai/gatana/releases/tag/gatana-sdk@3.1.4"), None);
        assert_eq!(version_from_tag_url("https://github.com/gatana-ai/gatana/releases"), None);
    }

    #[test]
    fn versions_compare_by_number_and_a_pre_release_comes_first() {
        assert!(newer("4.1.1", "4.1.0"));
        assert!(newer("4.10.0", "4.9.3"));
        assert!(newer("5.0.0", "4.99.99"));
        assert!(!newer("4.1.0", "4.1.0"));
        assert!(!newer("4.1.0", "4.1.1"));
        assert!(newer("4.2.0", "4.2.0-alpha.0"));
        assert!(!newer("4.1.1", "4.2.0-alpha.0"));
        assert!(newer("4.2.0-beta.0", "4.2.0-alpha.0"));
    }
}
