//! Which file paths of a skill the CLI writes and pushes. The sync applies the rules to every path
//! from the server and the push to every local file, on every platform alike, so that each machine
//! holds the same files of a skill.

use std::collections::HashMap;
use unicode_normalization::UnicodeNormalization;

pub const SKILL_FILE: &str = "SKILL.md";

/// The longest path that the backend stores, in bytes.
const MAX_PATH_BYTES: usize = 255;

/// Why the backend refuses a path, or a path can leave the skill folder, or None. The backend
/// applies these rules at every write. The sync applies them again, because it does not trust an
/// MCP server, and the push applies them before its first request.
fn unsafe_reason(path: &str) -> Option<&'static str> {
    if path.len() > MAX_PATH_BYTES {
        return Some("it is longer than 255 bytes");
    }
    if path.contains('\\') {
        return Some("it contains a backslash");
    }
    if path.chars().any(char::is_control) {
        return Some("it contains a control character");
    }
    if path.starts_with('/') {
        return Some("it is an absolute path");
    }
    if path.split('/').any(|segment| segment.is_empty() || segment == "." || segment == "..") {
        return Some("it has an empty, \".\" or \"..\" segment");
    }
    // A host could find a second skill in the folder.
    if path.rsplit_once('/').is_some_and(|(_, name)| name.to_lowercase() == SKILL_FILE.to_lowercase()) {
        return Some("it is a SKILL.md in a subfolder. A skill has one SKILL.md, at its root");
    }
    None
}

/// Why Windows cannot hold a file or folder of this name, or None.
fn windows_reason(segment: &str) -> Option<&'static str> {
    const RESERVED: [&str; 6] = ["CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"];
    // Windows also reserves "CON .txt": spaces between the name and the extension do not count.
    let stem = segment.split('.').next().unwrap_or_default().trim_end().to_ascii_uppercase();
    let numbered = stem.strip_prefix("COM").or_else(|| stem.strip_prefix("LPT")).is_some_and(|digit| {
        let mut chars = digit.chars();
        matches!((chars.next(), chars.next()), (Some('0'..='9' | '¹' | '²' | '³'), None))
    });
    if RESERVED.contains(&stem.as_str()) || numbered {
        return Some("Windows reserves the name");
    }
    if segment.ends_with('.') || segment.ends_with(' ') {
        return Some("a name that ends with a dot or a space does not exist on Windows");
    }
    if segment.contains(['<', '>', ':', '"', '|', '?', '*']) {
        return Some("it contains a character that Windows does not allow");
    }
    None
}

/// Splits paths into the ones a skill folder gets on every machine, in byte order with `SKILL.md`
/// first, and the others, each with the reason. Of several paths that are one path on a file system
/// that ignores letter case or Unicode form, the first in byte order stays.
pub fn check_paths<'a>(paths: impl IntoIterator<Item = &'a str>) -> (Vec<&'a str>, Vec<(&'a str, String)>) {
    let mut sorted: Vec<&str> = paths.into_iter().collect();
    sorted.sort_by_key(|path| (*path != SKILL_FILE, path.as_bytes()));
    let mut kept = Vec::new();
    let mut skipped = Vec::new();
    // Every kept file and each of its folders, by the name as such a file system compares it.
    let mut taken: HashMap<String, (&str, bool)> = HashMap::new();
    for path in sorted {
        if let Some(reason) = unsafe_reason(path).or_else(|| path.split('/').find_map(windows_reason)) {
            skipped.push((path, reason.to_string()));
            continue;
        }
        let folded: String = path.nfc().collect::<String>().to_lowercase().nfc().collect();
        let prefixes: Vec<usize> =
            path.match_indices('/').map(|(index, _)| index).chain(std::iter::once(path.len())).collect();
        let folded_prefixes: Vec<usize> =
            folded.match_indices('/').map(|(index, _)| index).chain(std::iter::once(folded.len())).collect();
        let clash = prefixes.iter().zip(&folded_prefixes).find_map(|(end, folded_end)| {
            let is_file = *end == path.len();
            let (other, other_is_file) = taken.get(&folded[..*folded_end])?;
            // The same folder, spelled the same way, is no clash.
            (is_file || *other_is_file || *other != &path[..*end]).then_some(*other)
        });
        if let Some(other) = clash {
            let reason = format!("it is the same path as {other:?} where letter case or Unicode form does not count");
            skipped.push((path, reason));
            continue;
        }
        for (end, folded_end) in prefixes.iter().zip(&folded_prefixes) {
            taken.entry(folded[..*folded_end].to_string()).or_insert((&path[..*end], *end == path.len()));
        }
        kept.push(path);
    }
    (kept, skipped)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn skipped(paths: &[&str]) -> Vec<String> {
        check_paths(paths.iter().copied()).1.into_iter().map(|(path, _)| path.to_string()).collect()
    }

    #[test]
    fn paths_that_can_leave_the_folder_are_refused() {
        let bad = [
            "../x",
            "a/../../x",
            "/etc/passwd",
            "a//b",
            "a/./b",
            ".",
            "a/",
            "",
            "a\\..\\..\\x",
            "a\u{0}b",
            "a\nb",
            "a\u{7f}b",
        ];
        assert_eq!(skipped(&bad).len(), bad.len());
        assert_eq!(check_paths(["SKILL.md", "a/b.txt", "a b/c#d.md", ".hidden", "..."]).1.len(), 1);
    }

    #[test]
    fn a_nested_skill_md_and_a_path_over_255_bytes_are_refused_as_the_backend_refuses_them() {
        let long = format!("docs/{}", "é".repeat(126));
        assert_eq!(long.len(), 257);
        let bad = ["docs/SKILL.md", "a/b/skill.MD", long.as_str()];
        assert_eq!(skipped(&bad).len(), bad.len());
        assert!(skipped(&["SKILL.md", "docs/SKILL.md.bak", &"a".repeat(255)]).is_empty());
    }

    #[test]
    fn names_that_windows_cannot_hold_are_skipped() {
        let bad = [
            "CON",
            "docs/nul.txt",
            "com1",
            "COM0",
            "lpt0.md",
            "LPT9.md",
            "COM\u{b9}",
            "lpt\u{b3}.txt",
            "CONIN$",
            "conout$.log",
            "CON .txt",
            "a./b",
            "a /b",
            "trailing.",
            "a:b",
            "what?.md",
        ];
        assert_eq!(skipped(&bad), {
            let mut sorted = bad.to_vec();
            sorted.sort();
            sorted
        });
        assert!(skipped(&["console.md", "com10", "COM\u{b9}0", "lpt", "nul-terminated.md", "conin.md"]).is_empty());
    }

    #[test]
    fn of_paths_that_collide_the_first_in_byte_order_stays() {
        // Files that differ in letter case, and folders that do.
        let (kept, skipped) = check_paths(["docs/b.md", "Docs/a.md", "readme.md", "README.md", "docs/c.md"]);
        assert_eq!(kept, ["Docs/a.md", "README.md"]);
        assert_eq!(skipped.iter().map(|(path, _)| *path).collect::<Vec<_>>(), ["docs/b.md", "docs/c.md", "readme.md"]);
        assert!(skipped[0].1.contains("\"Docs\""));

        // One name in the two Unicode forms: "é" as one code point and as "e" with a combining accent.
        let (kept, skipped) = check_paths(["caf\u{e9}.md", "cafe\u{301}.md"]);
        assert_eq!(kept, ["cafe\u{301}.md"]);
        assert_eq!(skipped[0].0, "caf\u{e9}.md");

        // A file and a folder of one name, and the document of the skill in another letter case.
        let (kept, _) = check_paths(["tools/run.sh", "Tools", "SKILL.MD", "SKILL.md"]);
        assert_eq!(kept, ["SKILL.md", "Tools"]);

        // Folders that are spelled the same way do not collide.
        assert!(check_paths(["a/b/c.md", "a/b/d.md", "a/e.md"]).1.is_empty());
    }
}
