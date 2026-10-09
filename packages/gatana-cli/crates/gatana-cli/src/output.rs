//! How results reach the terminal: `-o json|yaml|table`, kubectl-style tables, and the success,
//! error and info lines.
//!
//! Results go to stdout. Errors go to stderr, and so do info lines when the format is JSON or
//! YAML, so a script that parses stdout gets only the result.

use crate::util::{get_path, js_string};
use serde_json::{Map, Value, json};
use std::io::Write;
use std::sync::atomic::{AtomicBool, AtomicU8, Ordering};

#[derive(Clone, Copy, Debug, PartialEq, Eq, clap::ValueEnum)]
pub enum Format {
    Json,
    Yaml,
    Table,
}

static FORMAT: AtomicU8 = AtomicU8::new(Format::Table as u8);
static EXPLICIT: AtomicBool = AtomicBool::new(false);

/// Set once from the global `-o` flag.
pub fn set_format(format: Option<Format>) {
    EXPLICIT.store(format.is_some(), Ordering::Relaxed);
    FORMAT.store(format.unwrap_or(Format::Table) as u8, Ordering::Relaxed);
}

pub fn format() -> Format {
    match FORMAT.load(Ordering::Relaxed) {
        value if value == Format::Json as u8 => Format::Json,
        value if value == Format::Yaml as u8 => Format::Yaml,
        _ => Format::Table,
    }
}

/// True when the user passed `-o`; commands then honor it over their own default.
pub fn format_explicit() -> bool {
    EXPLICIT.load(Ordering::Relaxed)
}

/// True when `-o json` or `-o yaml` was asked for.
pub fn machine_readable() -> bool {
    format_explicit() && format() != Format::Table
}

/// One table column: a title and how to get the cell from a row.
pub struct Column {
    pub title: &'static str,
    cell: Cell,
}

enum Cell {
    Path(&'static str),
    Computed(fn(&Value) -> Value),
}

impl Column {
    /// The value at a lodash-style path of the row (`transportConfig.type`).
    pub const fn path(title: &'static str, path: &'static str) -> Self {
        Self { title, cell: Cell::Path(path) }
    }

    /// A value computed from the whole row.
    pub const fn computed(title: &'static str, compute: fn(&Value) -> Value) -> Self {
        Self { title, cell: Cell::Computed(compute) }
    }

    fn render(&self, row: &Value) -> String {
        match &self.cell {
            Cell::Path(path) => cell_text(get_path(row, path)),
            Cell::Computed(compute) => cell_text(Some(&compute(row))),
        }
    }
}

#[derive(Default)]
pub struct Options<'a> {
    pub columns: Option<&'a [Column]>,
    pub no_headers: bool,
    /// The format when the user did not pass `-o`.
    pub default_format: Option<Format>,
}

impl<'a> Options<'a> {
    pub fn columns(columns: &'a [Column]) -> Self {
        Self { columns: Some(columns), ..Self::default() }
    }

    pub fn default_format(format: Format) -> Self {
        Self { default_format: Some(format), ..Self::default() }
    }

    pub fn yaml() -> Self {
        Self::default_format(Format::Yaml)
    }
}

/// Writes to stdout. A closed pipe (`gatana get servers | head -1`) ends the process quietly.
pub fn write_stdout(text: &str) {
    let mut stdout = std::io::stdout().lock();
    if let Err(error) = stdout.write_all(text.as_bytes()).and_then(|()| stdout.flush())
        && error.kind() == std::io::ErrorKind::BrokenPipe
    {
        std::process::exit(0);
    }
}

pub fn write_stderr(text: &str) {
    let _ = std::io::stderr().lock().write_all(text.as_bytes());
}

pub fn println(text: &str) {
    write_stdout(&format!("{text}\n"));
}

pub fn eprintln(text: &str) {
    write_stderr(&format!("{text}\n"));
}

// Emphasis for a terminal. `console` leaves the text plain when the stream is not a terminal, when
// NO_COLOR is set, or when TERM is dumb; stderr is checked on its own.

pub fn bold(text: &str) -> String {
    console::style(text).bold().to_string()
}

pub fn dim(text: &str) -> String {
    console::style(text).dim().to_string()
}

pub fn green(text: &str) -> String {
    console::style(text).green().to_string()
}

/// For warnings, which go to stderr.
pub fn yellow(text: &str) -> String {
    console::style(text).yellow().for_stderr().to_string()
}

/// For errors, which go to stderr.
pub fn red(text: &str) -> String {
    console::style(text).red().for_stderr().to_string()
}

/// A path with the home directory as `~`, for messages.
pub fn tilde(path: &std::path::Path) -> String {
    let home = std::env::home_dir().unwrap_or_default();
    match path.strip_prefix(&home) {
        Ok(rest) if !home.as_os_str().is_empty() => format!("~/{}", rest.display()),
        _ => path.display().to_string(),
    }
}

/// Prints a result in the chosen format.
pub fn output(data: &Value, options: Options) {
    let format = match options.default_format {
        Some(default) if !format_explicit() => default,
        _ => format(),
    };
    match format {
        Format::Json => println(&data.to_string()),
        Format::Yaml => write_stdout(&crate::yaml::dump(data)),
        Format::Table => {
            for line in table_lines(data, &options) {
                println(&line);
            }
        }
    }
}

/// `output` with no options.
pub fn print(data: &Value) {
    output(data, Options::default());
}

pub fn success(message: &str) {
    match format() {
        Format::Table => println(&green(message)),
        _ => print(&json!({ "success": true, "message": message })),
    }
}

pub fn error(message: &str) {
    match format() {
        Format::Table => eprintln(&red(message)),
        Format::Json => eprintln(&json!({ "success": false, "error": message }).to_string()),
        Format::Yaml => write_stderr(&crate::yaml::dump(&json!({ "success": false, "error": message }))),
    }
}

/// Progress and notes. Kept out of stdout when stdout carries JSON or YAML.
pub fn info(message: &str) {
    if machine_readable() { eprintln(message) } else { println(message) }
}

/// Moves the cursor up `count` lines and clears them.
pub fn clear_lines(count: usize) {
    write_stdout(&"\x1b[1A\x1b[2K".repeat(count));
}

fn cell_text(value: Option<&Value>) -> String {
    match value {
        None | Some(Value::Null) => "<none>".to_string(),
        Some(value @ (Value::Object(_) | Value::Array(_))) => value.to_string(),
        Some(value) => js_string(value),
    }
}

fn table_lines(data: &Value, options: &Options) -> Vec<String> {
    match data {
        Value::Array(rows) if !rows.is_empty() => render_table(rows, options.columns, options.no_headers),
        Value::Object(map) if options.columns.is_some() => {
            // A wrapped list such as `{ servers: [...] }`: the first array in it is the table.
            match map.values().find_map(Value::as_array) {
                Some(rows) if rows.is_empty() => {
                    vec![format!("No {} found.", map.keys().next().map(String::as_str).unwrap_or("items"))]
                }
                Some(rows) => render_table(rows, options.columns, options.no_headers),
                None => render_table(std::slice::from_ref(data), options.columns, options.no_headers),
            }
        }
        Value::Object(map) => key_value_sections(map),
        Value::Array(_) => Vec::new(),
        Value::String(text) => vec![text.clone()],
        other => vec![js_string(other)],
    }
}

/// kubectl-style: uppercase headers, no borders, columns three spaces apart.
pub fn render_table(rows: &[Value], columns: Option<&[Column]>, no_headers: bool) -> Vec<String> {
    let (headers, cells): (Vec<String>, Vec<Vec<String>>) = match columns {
        Some(columns) => (
            columns.iter().map(|column| column.title.to_uppercase()).collect(),
            rows.iter().map(|row| columns.iter().map(|column| column.render(row)).collect()).collect(),
        ),
        None => {
            let Some(first) = rows[0].as_object() else {
                return rows.iter().map(|row| cell_text(Some(row))).collect();
            };
            let keys: Vec<&String> = first.keys().collect();
            (
                keys.iter().map(|key| key.to_uppercase()).collect(),
                rows.iter().map(|row| keys.iter().map(|key| cell_text(row.get(key.as_str()))).collect()).collect(),
            )
        }
    };
    let width = |text: &str| text.chars().count();
    let widths: Vec<usize> = headers
        .iter()
        .enumerate()
        .map(|(index, header)| cells.iter().map(|row| width(&row[index])).chain([width(header)]).max().unwrap_or(0))
        .collect();
    let line = |cells: &[String]| {
        let padded: Vec<String> =
            cells.iter().zip(&widths).map(|(cell, width)| format!("{cell:<width$}", width = width)).collect();
        padded.join("   ").trim_end().to_string()
    };
    let mut lines = Vec::new();
    if !no_headers {
        lines.push(line(&headers));
    }
    lines.extend(cells.iter().map(|row| line(row)));
    lines
}

const PROPERTY_COLUMNS: [Column; 2] = [Column::path("Property", "property"), Column::path("Value", "value")];

/// An object without columns: its scalars as a property/value table, then each nested object or
/// list under its own heading.
fn key_value_sections(map: &Map<String, Value>) -> Vec<String> {
    let mut scalars = Vec::new();
    let mut nested = Vec::new();
    for (key, value) in map {
        match value {
            Value::Array(items) if items.is_empty() => scalars.push(json!({ "property": key, "value": "[]" })),
            Value::Object(fields) if fields.is_empty() => scalars.push(json!({ "property": key, "value": "{}" })),
            Value::Array(_) | Value::Object(_) => nested.push((key, value)),
            Value::Null => scalars.push(json!({ "property": key, "value": "<none>" })),
            other => scalars.push(json!({ "property": key, "value": other })),
        }
    }
    let mut lines = Vec::new();
    if !scalars.is_empty() {
        lines.extend(render_table(&scalars, Some(&PROPERTY_COLUMNS), false));
    }
    for (key, value) in nested {
        lines.push(format!("\n{key}:"));
        match value {
            Value::Array(items) => {
                let rows: Vec<Value> = items
                    .iter()
                    .map(|item| if item.is_object() { item.clone() } else { json!({ "value": item }) })
                    .collect();
                lines.extend(render_table(&rows, None, false));
            }
            Value::Object(fields) => {
                let rows: Vec<Value> = fields
                    .iter()
                    .map(|(name, field)| {
                        let text = match field {
                            Value::Null => "<none>".to_string(),
                            Value::Object(_) | Value::Array(_) => field.to_string(),
                            scalar => js_string(scalar),
                        };
                        json!({ "property": name, "value": text })
                    })
                    .collect();
                lines.extend(render_table(&rows, Some(&PROPERTY_COLUMNS), false));
            }
            _ => {}
        }
    }
    lines
}

#[cfg(test)]
mod tests {
    use super::*;

    const COLUMNS: [Column; 2] = [Column::path("Slug", "slug"), Column::path("Type", "transportConfig.type")];

    #[test]
    fn tables_are_padded_with_uppercase_headers() {
        let rows = json!([
            { "slug": "github", "transportConfig": { "type": "hosted" } },
            { "slug": "x", "transportConfig": null },
        ]);
        let lines = table_lines(&rows, &Options::columns(&COLUMNS));
        assert_eq!(lines, vec!["SLUG     TYPE", "github   hosted", "x        <none>"]);
    }

    #[test]
    fn a_wrapped_empty_list_says_so() {
        let lines = table_lines(&json!({ "servers": [] }), &Options::columns(&COLUMNS));
        assert_eq!(lines, vec!["No servers found."]);
    }

    #[test]
    fn objects_without_columns_become_property_tables_and_sections() {
        let lines = table_lines(
            &json!({ "id": "a", "enabled": true, "gone": null, "tags": [], "logs": [{ "event": "x" }], "meta": { "k": 1, "o": { "a": 1 } } }),
            &Options::default(),
        );
        assert_eq!(
            lines,
            vec![
                "PROPERTY   VALUE",
                "id         a",
                "enabled    true",
                "gone       <none>",
                "tags       []",
                "\nlogs:",
                "EVENT",
                "x",
                "\nmeta:",
                "PROPERTY   VALUE",
                "k          1",
                "o          {\"a\":1}",
            ]
        );
    }
}
