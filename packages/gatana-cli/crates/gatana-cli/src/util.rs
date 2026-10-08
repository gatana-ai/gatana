//! Small helpers that keep the TypeScript CLI's behavior: JavaScript number and date formatting,
//! lodash-style dotted paths, kubectl-style ages.

use chrono::{DateTime, SecondsFormat, Utc};
use serde_json::{Map, Number, Value};
use std::io::{IsTerminal, Read};

/// A number as JavaScript prints it: `1.0` is `1`.
pub fn js_number(number: &Number) -> String {
    if number.is_i64() || number.is_u64() {
        return number.to_string();
    }
    match number.as_f64() {
        Some(value) if value.fract() == 0.0 && value.abs() < 1e21 => format!("{value:.0}"),
        Some(value) => value.to_string(),
        None => number.to_string(),
    }
}

/// `String(value)` for a JSON value, with objects and arrays as compact JSON.
pub fn js_string(value: &Value) -> String {
    match value {
        Value::Null => "null".to_string(),
        Value::Bool(flag) => flag.to_string(),
        Value::Number(number) => js_number(number),
        Value::String(text) => text.clone(),
        other => other.to_string(),
    }
}

/// `new Date(text).toISOString()`: UTC with milliseconds. The manifest compares these strings, so
/// the format must not drift.
pub fn iso_millis(text: &str) -> Option<String> {
    parse_date(text).map(|date| date.to_rfc3339_opts(SecondsFormat::Millis, true))
}

pub fn parse_date(text: &str) -> Option<DateTime<Utc>> {
    if let Ok(date) = DateTime::parse_from_rfc3339(text) {
        return Some(date.with_timezone(&Utc));
    }
    // `2026-09-10 08:00:00Z` and friends.
    DateTime::parse_from_rfc3339(&text.replacen(' ', "T", 1)).ok().map(|date| date.with_timezone(&Utc))
}

pub fn now_iso() -> String {
    Utc::now().to_rfc3339_opts(SecondsFormat::Millis, true)
}

/// kubectl-style age: `3s`, `5m12s`, `2h30m`, `4d`.
pub fn format_age(value: Option<&Value>) -> String {
    let Some(date) = value.and_then(Value::as_str).filter(|text| !text.is_empty()).and_then(parse_date) else {
        return "<unknown>".to_string();
    };
    let diff = Utc::now().signed_duration_since(date).num_milliseconds();
    if diff < 0 {
        return "0s".to_string();
    }
    let seconds = diff / 1000;
    let minutes = seconds / 60;
    let hours = minutes / 60;
    let days = hours / 24;
    if days > 0 {
        format!("{days}d")
    } else if hours > 0 {
        format!("{hours}h{}m", minutes % 60)
    } else if minutes > 0 {
        format!("{minutes}m{}s", seconds % 60)
    } else {
        format!("{seconds}s")
    }
}

/// The inverse of `format_age`, in milliseconds: `3m10s` is 190000. None when nothing matches.
pub fn from_age(text: &str) -> Option<u64> {
    let mut total: u64 = 0;
    let mut matched = false;
    let mut digits = String::new();
    for ch in text.chars() {
        if ch.is_ascii_digit() {
            digits.push(ch);
            continue;
        }
        let unit = match ch {
            's' => 1_000,
            'm' => 60_000,
            'h' => 3_600_000,
            'd' => 86_400_000,
            _ => {
                digits.clear();
                continue;
            }
        };
        if let Ok(value) = digits.parse::<u64>() {
            total = total.saturating_add(value.saturating_mul(unit));
            matched = true;
        }
        digits.clear();
    }
    matched.then_some(total)
}

fn path_keys(path: &str) -> Vec<String> {
    let mut keys = Vec::new();
    for part in path.split('.') {
        let mut rest = part;
        while let Some(open) = rest.find('[') {
            if open > 0 {
                keys.push(rest[..open].to_string());
            }
            match rest[open..].find(']') {
                Some(close) => {
                    keys.push(rest[open + 1..open + close].trim_matches(|c| c == '"' || c == '\'').to_string());
                    rest = &rest[open + close + 1..];
                }
                None => {
                    keys.push(rest[open..].to_string());
                    rest = "";
                }
            }
        }
        if !rest.is_empty() || part.is_empty() {
            keys.push(rest.to_string());
        }
    }
    keys
}

fn is_index(key: &str) -> bool {
    !key.is_empty() && key.bytes().all(|byte| byte.is_ascii_digit()) && (key == "0" || !key.starts_with('0'))
}

/// lodash `_.get(value, 'a.b[0].c')`.
pub fn get_path<'a>(value: &'a Value, path: &str) -> Option<&'a Value> {
    let mut current = value;
    for key in path_keys(path) {
        current = match current {
            Value::Object(map) => map.get(&key)?,
            Value::Array(items) => items.get(key.parse::<usize>().ok()?)?,
            _ => return None,
        };
    }
    Some(current)
}

/// lodash `_.set(value, 'a.b[0].c', new)`: missing levels become objects, or arrays when the next
/// key is an index.
pub fn set_path(value: &mut Value, path: &str, new: Value) {
    let keys = path_keys(path);
    let mut current = value;
    for (position, key) in keys.iter().enumerate() {
        let last = position == keys.len() - 1;
        let next_is_index = keys.get(position + 1).is_some_and(|next| is_index(next));
        if let Value::Array(items) = current
            && !is_index(key)
        {
            // A named key on an array: lodash sets a property, which JSON cannot hold. The array
            // becomes an object keyed by index instead of losing the value.
            let map: Map<String, Value> =
                items.drain(..).enumerate().map(|(index, item)| (index.to_string(), item)).collect();
            *current = Value::Object(map);
        }
        if !current.is_object() && !current.is_array() {
            *current = Value::Object(Map::new());
        }
        let slot: &mut Value = match current {
            Value::Array(items) => {
                let index: usize = key.parse().unwrap_or(0);
                if items.len() <= index {
                    items.resize(index + 1, Value::Null);
                }
                &mut items[index]
            }
            Value::Object(map) => map.entry(key.clone()).or_insert(Value::Null),
            _ => unreachable!("made a container above"),
        };
        if last {
            *slot = new;
            return;
        }
        if !slot.is_object() && !slot.is_array() {
            *slot = if next_is_index { Value::Array(Vec::new()) } else { Value::Object(Map::new()) };
        }
        current = slot;
    }
}

/// What `-p key=value` and `-a key=value` make of a value: `true`, `false`, `null` and anything
/// `Number()` reads become JSON scalars; the rest stays a string.
pub fn coerce_scalar(text: &str) -> Value {
    match text {
        "true" => return Value::Bool(true),
        "false" => return Value::Bool(false),
        "null" => return Value::Null,
        "" => return Value::String(String::new()),
        _ => {}
    }
    match js_number_from(text) {
        Some(number) => number,
        None => Value::String(text.to_string()),
    }
}

fn js_number_from(text: &str) -> Option<Value> {
    let trimmed = text.trim();
    if trimmed.is_empty() {
        return Some(Value::from(0));
    }
    for (prefix, radix) in [("0x", 16), ("0X", 16), ("0o", 8), ("0O", 8), ("0b", 2), ("0B", 2)] {
        if let Some(digits) = trimmed.strip_prefix(prefix) {
            return i64::from_str_radix(digits, radix).ok().map(Value::from);
        }
    }
    // Rust also reads `inf` and `nan`; Number() does not, and JSON cannot hold them anyway.
    if trimmed.chars().any(|ch| ch.is_ascii_alphabetic() && ch != 'e' && ch != 'E') {
        return None;
    }
    let value: f64 = trimmed.parse().ok()?;
    if value.fract() == 0.0 && value.abs() < 9_007_199_254_740_992.0 {
        return Some(Value::from(value as i64));
    }
    Number::from_f64(value).map(Value::Number)
}

/// lodash `_.merge` for JSON: objects merge key by key, everything else is replaced.
pub fn deep_merge(target: &mut Value, source: &Value) {
    match (target, source) {
        (Value::Object(target), Value::Object(source)) => {
            for (key, value) in source {
                match target.get_mut(key) {
                    Some(existing) if existing.is_object() && value.is_object() => deep_merge(existing, value),
                    _ => {
                        target.insert(key.clone(), value.clone());
                    }
                }
            }
        }
        (target, source) => *target = source.clone(),
    }
}

/// Everything piped to stdin, or None when stdin is a terminal.
pub fn read_piped_stdin() -> std::io::Result<Option<String>> {
    let stdin = std::io::stdin();
    if stdin.is_terminal() {
        return Ok(None);
    }
    let mut text = String::new();
    stdin.lock().read_to_string(&mut text)?;
    Ok(Some(text))
}

/// `-a key=value` / `-p key=value` pairs, or one JSON object when the joined text starts with `{`.
pub fn parse_inline_object(pairs: &[String]) -> anyhow::Result<Value> {
    let joined = pairs.join(" ");
    if joined.trim_start().starts_with('{') {
        return serde_json::from_str(&joined).map_err(|error| anyhow::anyhow!("Failed to parse JSON input: {error}"));
    }
    let mut object = Value::Object(Map::new());
    for pair in pairs {
        let Some((key, value)) = pair.split_once('=') else {
            anyhow::bail!("Invalid key=value pair: \"{pair}\". Expected format: key.path=value");
        };
        set_path(&mut object, key, coerce_scalar(value));
    }
    Ok(object)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn numbers_print_like_javascript() {
        assert_eq!(js_string(&json!(1.0)), "1");
        assert_eq!(js_string(&json!(1.5)), "1.5");
        assert_eq!(js_string(&json!(42)), "42");
        assert_eq!(js_string(&json!(true)), "true");
    }

    #[test]
    fn ages_round_trip() {
        assert_eq!(from_age("3m10s"), Some(190_000));
        assert_eq!(from_age("10m"), Some(600_000));
        assert_eq!(from_age("2h30m"), Some(9_000_000));
        assert_eq!(from_age("45d"), Some(3_888_000_000));
        assert_eq!(from_age("soon"), None);
        assert_eq!(format_age(None), "<unknown>");
        let earlier = (Utc::now() - chrono::Duration::seconds(312)).to_rfc3339();
        assert_eq!(format_age(Some(&json!(earlier))), "5m12s");
        let days = (Utc::now() - chrono::Duration::days(4)).to_rfc3339();
        assert_eq!(format_age(Some(&json!(days))), "4d");
    }

    #[test]
    fn dates_normalize_to_javascript_iso_strings() {
        assert_eq!(iso_millis("2026-09-10T08:00:00Z").as_deref(), Some("2026-09-10T08:00:00.000Z"));
        assert_eq!(iso_millis("2026-09-10T10:00:00.5+02:00").as_deref(), Some("2026-09-10T08:00:00.500Z"));
        assert_eq!(iso_millis("not a date"), None);
    }

    #[test]
    fn paths_set_and_get_like_lodash() {
        let mut value = json!({});
        set_path(&mut value, "a.b", json!(1));
        set_path(&mut value, "list[1].name", json!("x"));
        set_path(&mut value, "n.0", json!("first"));
        assert_eq!(value, json!({"a": {"b": 1}, "list": [null, {"name": "x"}], "n": ["first"]}));
        assert_eq!(get_path(&value, "a.b"), Some(&json!(1)));
        assert_eq!(get_path(&value, "list[1].name"), Some(&json!("x")));
        assert_eq!(get_path(&value, "a.missing"), None);
    }

    #[test]
    fn inline_values_are_coerced_like_the_typescript_cli() {
        assert_eq!(coerce_scalar("true"), json!(true));
        assert_eq!(coerce_scalar("null"), Value::Null);
        assert_eq!(coerce_scalar("42"), json!(42));
        assert_eq!(coerce_scalar("1.5"), json!(1.5));
        assert_eq!(coerce_scalar("0x10"), json!(16));
        assert_eq!(coerce_scalar("hello"), json!("hello"));
        assert_eq!(coerce_scalar("NaN"), json!("NaN"));
        assert_eq!(coerce_scalar(""), json!(""));
        let object = parse_inline_object(&["isEnabled=false".into(), "a.b=x y".into()]).unwrap();
        assert_eq!(object, json!({"isEnabled": false, "a": {"b": "x y"}}));
        let json = parse_inline_object(&["{\"a\":".into(), "1}".into()]).unwrap();
        assert_eq!(json, json!({"a": 1}));
        assert!(parse_inline_object(&["novalue".into()]).is_err());
    }

    #[test]
    fn merge_is_deep_for_objects_only() {
        let mut target = json!({"orgs": {"acme": {"baseUrl": "x", "tokens": {"a": 1}}}});
        deep_merge(&mut target, &json!({"orgs": {"acme": {"pat": "p", "tokens": {"b": 2}}}}));
        assert_eq!(target, json!({"orgs": {"acme": {"baseUrl": "x", "tokens": {"a": 1, "b": 2}, "pat": "p"}}}));
    }
}
