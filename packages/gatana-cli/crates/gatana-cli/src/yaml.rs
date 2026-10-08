//! YAML out and in.
//!
//! The emitter follows js-yaml's `dump`, which the TypeScript CLI used, so `-o yaml` and the
//! SKILL.md frontmatter keep their exact text: the same scalars are plain, quoted or block-styled.
//! The one difference is that long lines are never folded (js-yaml folds at 80 columns by default).
//! The loader reads with the YAML 1.2 core schema, like js-yaml's `CORE_SCHEMA`.

use crate::util::js_number;
use regex_lite::Regex;
use serde_json::{Map, Number, Value};
use std::sync::OnceLock;

#[derive(Clone, Copy)]
struct Style {
    /// Quote every string value (not keys), as js-yaml's `forceQuotes`.
    force_quotes: bool,
    /// Double quotes instead of single ones where quoting is needed.
    double: bool,
}

const INDENT: usize = 2;

/// js-yaml `dump(value)` with its defaults (but no folding).
pub fn dump(value: &Value) -> String {
    emit(value, Style { force_quotes: false, double: false })
}

/// js-yaml `dump(value, { lineWidth: -1, quotingType: '"', forceQuotes: true })`: the frontmatter
/// style, every string on one line in double quotes.
pub fn dump_quoted(value: &Value) -> String {
    emit(value, Style { force_quotes: true, double: true })
}

fn emit(value: &Value, style: Style) -> String {
    let text = node(value, 0, true, false, style);
    if text.is_empty() { text } else { text + "\n" }
}

fn next_line(level: usize) -> String {
    format!("\n{}", " ".repeat(INDENT * level))
}

fn node(value: &Value, level: usize, compact: bool, is_key: bool, style: Style) -> String {
    match value {
        Value::Null => "null".to_string(),
        Value::Bool(flag) => flag.to_string(),
        Value::Number(number) => number_text(number),
        Value::String(text) => scalar(text, level, is_key, style),
        Value::Array(items) if items.is_empty() => "[]".to_string(),
        Value::Object(map) if map.is_empty() => "{}".to_string(),
        Value::Array(items) => {
            let mut out = String::new();
            for item in items {
                let dumped = node(item, level + 1, true, false, style);
                if !compact || !out.is_empty() {
                    out.push_str(&next_line(level));
                }
                out.push_str(if dumped.starts_with('\n') { "-" } else { "- " });
                out.push_str(&dumped);
            }
            out
        }
        Value::Object(map) => {
            let mut out = String::new();
            for (key, child) in map {
                if !compact || !out.is_empty() {
                    out.push_str(&next_line(level));
                }
                out.push_str(&scalar(key, level + 1, true, style));
                let dumped = node(child, level + 1, false, false, style);
                out.push_str(if dumped.starts_with('\n') { ":" } else { ": " });
                out.push_str(&dumped);
            }
            out
        }
    }
}

fn number_text(number: &Number) -> String {
    match number.as_f64() {
        Some(value) if value.is_nan() => ".nan".to_string(),
        Some(value) if value.is_infinite() => if value > 0.0 { ".inf" } else { "-.inf" }.to_string(),
        _ => js_number(number),
    }
}

enum ScalarStyle {
    Plain,
    Single,
    Double,
    Literal,
}

fn scalar(text: &str, level: usize, is_key: bool, style: Style) -> String {
    if text.is_empty() {
        return if style.double { "\"\"" } else { "''" }.to_string();
    }
    // YAML 1.1 booleans and sexagesimal numbers: quoted for old parsers, without escaping.
    if DEPRECATED_BOOLEANS.contains(&text) || base60().is_match(text) {
        return if style.double { format!("\"{text}\"") } else { format!("'{text}'") };
    }
    let indent = INDENT * level.max(1);
    match choose_style(text, is_key, style.force_quotes && !is_key, style.double) {
        ScalarStyle::Plain => text.to_string(),
        ScalarStyle::Single => format!("'{}'", text.replace('\'', "''")),
        ScalarStyle::Double => format!("\"{}\"", escape(text)),
        ScalarStyle::Literal => {
            let mut out = String::from("|");
            out.push_str(&block_header(text));
            let indented = indent_lines(text, indent);
            out.push_str(indented.strip_suffix('\n').unwrap_or(&indented));
            out
        }
    }
}

const DEPRECATED_BOOLEANS: &[&str] =
    &["y", "Y", "yes", "Yes", "YES", "on", "On", "ON", "n", "N", "no", "No", "NO", "off", "Off", "OFF"];

fn base60() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"^[-+]?[0-9_]+(?::[0-9_]+)+(?:\.[0-9_]*)?$").expect("valid regex"))
}

fn choose_style(text: &str, single_line_only: bool, force_quotes: bool, double: bool) -> ScalarStyle {
    let chars: Vec<char> = text.chars().collect();
    let mut plain = plain_safe_first(chars[0]) && plain_safe_last(chars[chars.len() - 1]);
    let mut has_line_break = false;
    let mut previous: Option<char> = None;
    for &ch in &chars {
        if ch == '\n' && !(single_line_only || force_quotes) {
            has_line_break = true;
        } else if !printable(ch) {
            return ScalarStyle::Double;
        }
        plain = plain && plain_safe(ch, previous);
        previous = Some(ch);
    }
    let quoted = if double { ScalarStyle::Double } else { ScalarStyle::Single };
    if !has_line_break {
        if plain && !force_quotes && !ambiguous(text) {
            return ScalarStyle::Plain;
        }
        return quoted;
    }
    if !force_quotes { ScalarStyle::Literal } else { quoted }
}

fn printable(ch: char) -> bool {
    let code = ch as u32;
    (0x20..=0x7E).contains(&code)
        || ((0xA1..=0xD7FF).contains(&code) && code != 0x2028 && code != 0x2029)
        || ((0xE000..=0xFFFD).contains(&code) && code != 0xFEFF)
        || (0x10000..=0x10FFFF).contains(&code)
}

fn whitespace(ch: char) -> bool {
    ch == ' ' || ch == '\t'
}

fn ns_char_or_whitespace(ch: char) -> bool {
    printable(ch) && ch != '\u{FEFF}' && ch != '\r' && ch != '\n'
}

/// js-yaml's isPlainSafe for block context, kept in its shape so it can be compared line by line.
#[allow(clippy::nonminimal_bool)]
fn plain_safe(ch: char, previous: Option<char>) -> bool {
    let ch_ns_or_ws = ns_char_or_whitespace(ch);
    let ch_ns = ch_ns_or_ws && !whitespace(ch);
    let previous_is_colon = previous == Some(':');
    (ch_ns_or_ws && ch != '#' && !(previous_is_colon && !ch_ns))
        || (previous.is_some_and(|prev| ns_char_or_whitespace(prev) && !whitespace(prev)) && ch == '#')
        || (previous_is_colon && ch_ns)
}

fn plain_safe_first(ch: char) -> bool {
    printable(ch)
        && ch != '\u{FEFF}'
        && !whitespace(ch)
        && !matches!(
            ch,
            '-' | '?'
                | ':'
                | ','
                | '['
                | ']'
                | '{'
                | '}'
                | '#'
                | '&'
                | '*'
                | '!'
                | '|'
                | '='
                | '>'
                | '\''
                | '"'
                | '%'
                | '@'
                | '`'
        )
}

fn plain_safe_last(ch: char) -> bool {
    !whitespace(ch) && ch != ':'
}

struct Resolvers {
    float: Regex,
    date: Regex,
    timestamp: Regex,
}

fn resolvers() -> &'static Resolvers {
    static RESOLVERS: OnceLock<Resolvers> = OnceLock::new();
    RESOLVERS.get_or_init(|| Resolvers {
        float: Regex::new(
            r"^(?:[-+]?(?:[0-9][0-9_]*)(?:\.[0-9_]*)?(?:[eE][-+]?[0-9]+)?|\.[0-9_]+(?:[eE][-+]?[0-9]+)?|[-+]?\.(?:inf|Inf|INF)|\.(?:nan|NaN|NAN))$",
        )
        .expect("valid regex"),
        date: Regex::new(r"^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$").expect("valid regex"),
        timestamp: Regex::new(
            r"^[0-9][0-9][0-9][0-9]-[0-9][0-9]?-[0-9][0-9]?(?:[Tt]|[ \t]+)[0-9][0-9]?:[0-9][0-9]:[0-9][0-9](?:\.[0-9]*)?(?:[ \t]*(?:Z|[-+][0-9][0-9]?(?::[0-9][0-9])?))?$",
        )
        .expect("valid regex"),
    })
}

/// True when a plain scalar would read back as something other than this string under js-yaml's
/// default schema: null, a boolean, a number, a timestamp or a merge key.
fn ambiguous(text: &str) -> bool {
    let resolvers = resolvers();
    matches!(text, "~" | "null" | "Null" | "NULL" | "true" | "True" | "TRUE" | "false" | "False" | "FALSE" | "<<")
        || yaml_integer(text)
        || (resolvers.float.is_match(text) && !text.ends_with('_'))
        || resolvers.date.is_match(text)
        || resolvers.timestamp.is_match(text)
}

/// js-yaml's resolveYamlInteger.
fn yaml_integer(text: &str) -> bool {
    let bytes = text.as_bytes();
    let mut index = 0;
    let mut has_digits = false;
    if bytes.is_empty() {
        return false;
    }
    let mut ch = bytes[0];
    if ch == b'-' || ch == b'+' {
        index += 1;
        ch = *bytes.get(index).unwrap_or(&0);
    }
    if ch == b'0' {
        if index + 1 == bytes.len() {
            return true;
        }
        index += 1;
        ch = bytes[index];
        let radix: Option<fn(u8) -> bool> = match ch {
            b'b' => Some(|c| c == b'0' || c == b'1'),
            b'x' => Some(|c: u8| c.is_ascii_hexdigit()),
            b'o' => Some(|c| (b'0'..=b'7').contains(&c)),
            _ => None,
        };
        if let Some(valid) = radix {
            let mut last = ch;
            for &c in &bytes[index + 1..] {
                last = c;
                if c == b'_' {
                    continue;
                }
                if !valid(c) {
                    return false;
                }
                has_digits = true;
            }
            return has_digits && last != b'_';
        }
    }
    if ch == b'_' {
        return false;
    }
    let mut last = ch;
    for &c in &bytes[index..] {
        last = c;
        if c == b'_' {
            continue;
        }
        if !c.is_ascii_digit() {
            return false;
        }
        has_digits = true;
    }
    has_digits && last != b'_'
}

fn escape(text: &str) -> String {
    let mut out = String::new();
    for ch in text.chars() {
        let sequence = match ch {
            '\0' => Some("\\0"),
            '\u{07}' => Some("\\a"),
            '\u{08}' => Some("\\b"),
            '\t' => Some("\\t"),
            '\n' => Some("\\n"),
            '\u{0B}' => Some("\\v"),
            '\u{0C}' => Some("\\f"),
            '\r' => Some("\\r"),
            '\u{1B}' => Some("\\e"),
            '"' => Some("\\\""),
            '\\' => Some("\\\\"),
            '\u{85}' => Some("\\N"),
            '\u{A0}' => Some("\\_"),
            '\u{2028}' => Some("\\L"),
            '\u{2029}' => Some("\\P"),
            _ => None,
        };
        match sequence {
            Some(sequence) => out.push_str(sequence),
            None if printable(ch) => out.push(ch),
            None => {
                let code = ch as u32;
                if code <= 0xFF {
                    out.push_str(&format!("\\x{code:02X}"));
                } else if code <= 0xFFFF {
                    out.push_str(&format!("\\u{code:04X}"));
                } else {
                    out.push_str(&format!("\\U{code:08X}"));
                }
            }
        }
    }
    out
}

fn block_header(text: &str) -> String {
    let indicator = if text.trim_start_matches('\n').starts_with(' ') { INDENT.to_string() } else { String::new() };
    let clip = text.ends_with('\n');
    let keep = clip && (text.ends_with("\n\n") || text == "\n");
    let chomp = if keep {
        "+"
    } else if clip {
        ""
    } else {
        "-"
    };
    format!("{indicator}{chomp}\n")
}

fn indent_lines(text: &str, spaces: usize) -> String {
    let pad = " ".repeat(spaces);
    let mut out = String::new();
    for line in text.split_inclusive('\n') {
        if !line.is_empty() && line != "\n" {
            out.push_str(&pad);
        }
        out.push_str(line);
    }
    out
}

/// Parses the first YAML document into JSON. An empty document is null.
pub fn load(text: &str) -> Result<Value, String> {
    let documents = yaml_rust2::YamlLoader::load_from_str(text).map_err(|error| error.to_string())?;
    Ok(documents.first().map(to_json).unwrap_or(Value::Null))
}

fn to_json(yaml: &yaml_rust2::Yaml) -> Value {
    use yaml_rust2::Yaml;
    match yaml {
        Yaml::Null | Yaml::BadValue | Yaml::Alias(_) => Value::Null,
        Yaml::Boolean(flag) => Value::Bool(*flag),
        Yaml::Integer(value) => Value::from(*value),
        Yaml::Real(text) => real(text),
        Yaml::String(text) => Value::String(text.clone()),
        Yaml::Array(items) => Value::Array(items.iter().map(to_json).collect()),
        Yaml::Hash(map) => {
            let mut out = Map::new();
            for (key, value) in map {
                let key = match to_json(key) {
                    Value::String(text) => text,
                    other => crate::util::js_string(&other),
                };
                out.insert(key, to_json(value));
            }
            Value::Object(out)
        }
    }
}

fn real(text: &str) -> Value {
    let parsed = match text.trim_start_matches('+') {
        ".inf" | ".Inf" | ".INF" => f64::INFINITY,
        "-.inf" | "-.Inf" | "-.INF" => f64::NEG_INFINITY,
        ".nan" | ".NaN" | ".NAN" => f64::NAN,
        other => other.replace('_', "").parse().unwrap_or(f64::NAN),
    };
    match Number::from_f64(parsed) {
        Some(_) if parsed.fract() == 0.0 && parsed.abs() < 9_007_199_254_740_992.0 => Value::from(parsed as i64),
        Some(number) => Value::Number(number),
        // JSON cannot hold infinities and NaN; JavaScript would print them as these words.
        None => Value::String(
            if parsed.is_nan() {
                "NaN"
            } else if parsed > 0.0 {
                "Infinity"
            } else {
                "-Infinity"
            }
            .into(),
        ),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn scalars_are_plain_or_quoted_like_js_yaml() {
        let value = json!({
            "plain": "hello world",
            "date": "2026-09-10T08:00:00.000Z",
            "number": "123",
            "bool": "true",
            "yes": "yes",
            "colon": "a: b",
            "hash": "a #b",
            "dash": "- x",
            "quote": "It's",
            "empty": "",
            "url": "https://x.example/a?b=c",
            "tab": "a\tb",
        });
        assert_eq!(
            dump(&value),
            "plain: hello world\ndate: '2026-09-10T08:00:00.000Z'\nnumber: '123'\nbool: 'true'\n'yes': 'yes'\n\
             colon: 'a: b'\nhash: 'a #b'\ndash: '- x'\nquote: It's\nempty: ''\nurl: https://x.example/a?b=c\ntab: \"a\\tb\"\n"
        );
    }

    #[test]
    fn nesting_follows_js_yaml_layout() {
        let value = json!({
            "server": {"slug": "x", "tags": ["a", "b"], "empty": [], "none": {}},
            "items": [{"a": 1, "b": null}, "two", [1, 2]],
            "text": "line one\nline two\n",
            "trimmed": "line one\nline two",
        });
        assert_eq!(
            dump(&value),
            "server:\n  slug: x\n  tags:\n    - a\n    - b\n  empty: []\n  none: {}\nitems:\n  - a: 1\n    b: null\n  - two\n  - - 1\n    - 2\n\
             text: |\n  line one\n  line two\ntrimmed: |-\n  line one\n  line two\n"
        );
        assert_eq!(dump(&json!(["a", {"b": 1}])), "- a\n- b: 1\n");
        assert_eq!(dump(&json!("eyJhbGciOi.x_y-z")), "eyJhbGciOi.x_y-z\n");
    }

    #[test]
    fn forced_quotes_use_double_quotes_on_one_line() {
        let value = json!({"description": "Say \"hi\"\nnow", "license": "MIT", "metadata": {"gatana-id": "skill_1", "count": 1, "n": "x"}});
        assert_eq!(
            dump_quoted(&value),
            "description: \"Say \\\"hi\\\"\\nnow\"\nlicense: \"MIT\"\nmetadata:\n  gatana-id: \"skill_1\"\n  count: 1\n  \"n\": \"x\"\n"
        );
    }

    #[test]
    fn integers_follow_js_yaml_rules() {
        for text in ["0", "12", "-3", "+4", "0x1F", "0o17", "0b101", "012", "1_000"] {
            assert!(yaml_integer(text), "{text}");
        }
        for text in ["", "-", "1_", "_1", "0x", "abc", "1.5", "0b2"] {
            assert!(!yaml_integer(text), "{text}");
        }
    }

    #[test]
    fn load_reads_the_core_schema() {
        let value = load("name: a\nversion: 1.0\nstable: true\nyes: yes\nwhen: 2026-01-01\nlist: [1, two]\n").unwrap();
        assert_eq!(
            value,
            json!({"name": "a", "version": 1, "stable": true, "yes": "yes", "when": "2026-01-01", "list": [1, "two"]})
        );
        assert_eq!(load("").unwrap(), Value::Null);
        assert!(load("a: [unclosed").is_err());
    }
}
