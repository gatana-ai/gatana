//! Debug logging switched on by the `DEBUG` environment variable, with the patterns of the npm
//! `debug` package the TypeScript CLI used: `DEBUG=gatana:*`, `DEBUG=gatana:http`,
//! `DEBUG=*,-gatana:http`. Lines go to stderr.

use std::sync::OnceLock;

struct Patterns {
    enabled: Vec<String>,
    skipped: Vec<String>,
}

fn patterns() -> &'static Patterns {
    static PATTERNS: OnceLock<Patterns> = OnceLock::new();
    PATTERNS.get_or_init(|| parse(&std::env::var("DEBUG").unwrap_or_default()))
}

fn parse(spec: &str) -> Patterns {
    let mut patterns = Patterns { enabled: Vec::new(), skipped: Vec::new() };
    for part in spec.split(|c: char| c == ',' || c.is_whitespace()).filter(|part| !part.is_empty()) {
        match part.strip_prefix('-') {
            Some(skipped) => patterns.skipped.push(skipped.to_string()),
            None => patterns.enabled.push(part.to_string()),
        }
    }
    patterns
}

/// `*` matches any run of characters, as in the npm package.
fn matches(pattern: &str, namespace: &str) -> bool {
    let mut parts = pattern.split('*');
    let first = parts.next().unwrap_or_default();
    let Some(mut rest) = namespace.strip_prefix(first) else {
        return false;
    };
    let parts: Vec<&str> = parts.collect();
    if parts.is_empty() {
        return rest.is_empty();
    }
    for (index, part) in parts.iter().enumerate() {
        if index == parts.len() - 1 {
            return rest.ends_with(part);
        }
        match rest.find(part) {
            Some(position) => rest = &rest[position + part.len()..],
            None => return false,
        }
    }
    true
}

fn is_enabled_in(patterns: &Patterns, namespace: &str) -> bool {
    !patterns.skipped.iter().any(|pattern| matches(pattern, namespace))
        && patterns.enabled.iter().any(|pattern| matches(pattern, namespace))
}

pub fn enabled(namespace: &str) -> bool {
    is_enabled_in(patterns(), namespace)
}

#[doc(hidden)]
pub fn log(namespace: &str, message: std::fmt::Arguments) {
    eprintln!("  {namespace} {message}");
}

/// `debug!("gatana:http", "→ {} {}", method, url)`: printed when `DEBUG` enables the namespace.
#[macro_export]
macro_rules! debug {
    ($namespace:expr, $($arg:tt)*) => {
        if $crate::debug::enabled($namespace) {
            $crate::debug::log($namespace, format_args!($($arg)*));
        }
    };
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn patterns_follow_the_npm_debug_package() {
        let all = parse("gatana:*");
        assert!(is_enabled_in(&all, "gatana:http"));
        assert!(!is_enabled_in(&all, "gatana"));
        let both = parse("gatana,gatana:*");
        assert!(is_enabled_in(&both, "gatana"));
        let skip = parse("*,-gatana:http");
        assert!(is_enabled_in(&skip, "gatana"));
        assert!(!is_enabled_in(&skip, "gatana:http"));
        assert!(!is_enabled_in(&parse(""), "gatana"));
        assert!(is_enabled_in(&parse("gat*ttp"), "gatana:http"));
    }
}
