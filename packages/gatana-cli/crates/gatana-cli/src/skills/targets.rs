//! Where skills are installed: preset agent folders or any directory.

use anyhow::Result;
use std::collections::HashSet;
use std::path::{Path, PathBuf};

pub struct Preset {
    pub name: &'static str,
    pub dir: &'static str,
    pub readers: &'static str,
}

/// Where the agent frameworks look for user-level skills.
pub const PRESETS: [Preset; 3] = [
    Preset { name: "claude", dir: "~/.claude/skills", readers: "Claude Code" },
    Preset { name: "agents", dir: "~/.agents/skills", readers: "Codex, Cursor, Gemini CLI, OpenCode, Copilot, Amp" },
    Preset { name: "hermes", dir: "~/.hermes/skills", readers: "Hermes Agent" },
];

pub const DEFAULT_TARGETS: [&str; 2] = ["claude", "agents"];

pub fn preset(name: &str) -> Option<&'static Preset> {
    PRESETS.iter().find(|preset| preset.name == name)
}

pub fn home() -> PathBuf {
    std::env::home_dir().unwrap_or_default()
}

pub fn expand_home(path: &str, home: &Path) -> PathBuf {
    if path == "~" {
        return home.to_path_buf();
    }
    if let Some(rest) = path.strip_prefix("~/") {
        return home.join(rest);
    }
    std::path::absolute(path).unwrap_or_else(|_| PathBuf::from(path))
}

/// Presets become their directory; anything else is a path. No arguments: the default targets.
pub fn resolve_targets(args: &[String], home: &Path) -> Vec<PathBuf> {
    let defaults: Vec<String> = DEFAULT_TARGETS.iter().map(|name| name.to_string()).collect();
    let names = if args.is_empty() { &defaults } else { args };
    names.iter().map(|name| expand_home(preset(name).map(|preset| preset.dir).unwrap_or(name), home)).collect()
}

/// Creates the directories and collapses aliases: `~/.agents/skills` is often a symlink to
/// `~/.claude/skills`, and syncing the same folder twice would make the second pass see the first
/// pass's folders as foreign.
pub fn prepare_targets(dirs: &[PathBuf]) -> Result<Vec<PathBuf>> {
    let mut seen = HashSet::new();
    let mut result = Vec::new();
    for dir in dirs {
        std::fs::create_dir_all(dir)?;
        let real = std::fs::canonicalize(dir)?;
        if seen.insert(real.clone()) {
            result.push(real);
        }
    }
    Ok(result)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn presets_and_paths_resolve() {
        let home = Path::new("/home/me");
        assert_eq!(
            resolve_targets(&[], home),
            vec![PathBuf::from("/home/me/.claude/skills"), PathBuf::from("/home/me/.agents/skills")]
        );
        assert_eq!(resolve_targets(&["hermes".into()], home), vec![PathBuf::from("/home/me/.hermes/skills")]);
        assert_eq!(resolve_targets(&["~/x".into()], home), vec![PathBuf::from("/home/me/x")]);
        assert_eq!(resolve_targets(&["/abs".into()], home), vec![PathBuf::from("/abs")]);
    }

    #[cfg(unix)]
    #[test]
    fn prepare_targets_creates_directories_and_collapses_symlinked_aliases() {
        let base = tempfile::tempdir().unwrap();
        let real = base.path().join("real");
        let alias = base.path().join("alias");
        std::fs::create_dir(&real).unwrap();
        std::os::unix::fs::symlink(&real, &alias).unwrap();
        let dirs = prepare_targets(&[alias, real, base.path().join("new")]).unwrap();
        assert_eq!(dirs.len(), 2);
        assert!(base.path().join("new").exists());
    }
}
