//! FaaS servers: JavaScript source code that Gatana runs as an MCP server.

pub mod deployment;
pub mod runner;

use crate::output::{self, Options};
use crate::util::set_path;
use anyhow::{Context, Result, anyhow, bail};
use regex_lite::Regex;
use serde_json::{Map, Value, json};
use std::io::Write;
use std::path::{Path, PathBuf};

pub struct IndexCheck {
    pub exists: bool,
    pub has_schema: bool,
}

/// The static check: an index.js that exports a schema.
pub fn check_index_js(dir: &Path) -> Result<IndexCheck> {
    let path = dir.join("index.js");
    if !path.is_file() {
        return Ok(IndexCheck { exists: false, has_schema: false });
    }
    let content = std::fs::read_to_string(&path).with_context(|| format!("Failed to read {}", path.display()))?;
    let es_module = Regex::new(r"(?i)export\s+const\s+schema\s*=").expect("valid regex");
    let common_js = Regex::new(r"(?i)module\.exports\.schema\s*=").expect("valid regex");
    Ok(IndexCheck { exists: true, has_schema: es_module.is_match(&content) || common_js.is_match(&content) })
}

/// Checks the source code: index.js exists and exports a schema, and, when Node.js is at hand,
/// each tool in the schema has a description and an exported function and every exported function
/// a schema entry. Errors when the code cannot be checked at all.
pub async fn verify(source: &Path) -> Result<Value> {
    let path = std::path::absolute(source)?;
    let check = check_index_js(&path)?;
    if !check.exists {
        bail!("index.js not found in {}", path.display());
    }
    if !check.has_schema {
        bail!(
            "index.js does not contain a schema export. Make sure your file exports a schema:\n  \u{2022} ES modules: export const schema = {{ ... }}\n  \u{2022} CommonJS: module.exports.schema = {{ ... }}"
        );
    }
    let outcome = runner::run(&path, runner::Mode::Verify).await?;
    if !outcome.ok {
        bail!("Failed to import module: {}", outcome.error.unwrap_or_default());
    }
    let mut result = Map::new();
    result.insert("path".into(), Value::String(path.display().to_string()));
    if let Value::Object(fields) = outcome.result {
        result.extend(fields);
    }
    if result.get("toolCount").and_then(Value::as_u64) == Some(0) {
        output::info("Warning: schema is empty \u{2014} no tools defined.");
    }
    Ok(Value::Object(result))
}

/// The input of `faas run`: `--input` JSON, else `--file`, then `-p key=value` on top.
pub fn tool_input(input: Option<&str>, file: Option<&Path>, params: &[String]) -> Result<Value> {
    let mut data = if let Some(input) = input {
        serde_json::from_str(input).map_err(|error| anyhow!("Failed to parse inline JSON: {error}"))?
    } else if let Some(file) = file {
        let text =
            std::fs::read_to_string(file).map_err(|error| anyhow!("Failed to read/parse input file: {error}"))?;
        serde_json::from_str(&text).map_err(|error| anyhow!("Failed to read/parse input file: {error}"))?
    } else {
        json!({})
    };
    if !params.is_empty() {
        if !data.is_object() {
            data = json!({});
        }
        for param in params {
            let Some((key, value)) = param.split_once('=') else {
                bail!("Invalid param format: \"{param}\". Expected key=value");
            };
            // Numbers, booleans, arrays and objects as JSON; anything else stays a string.
            let value = serde_json::from_str(value).unwrap_or_else(|_| Value::String(value.to_string()));
            set_path(&mut data, key, value);
        }
    }
    Ok(data)
}

/// Runs one tool of the local source code and prints what it returns.
pub async fn run_tool(source: &Path, tool: &str, input: &Value) -> Result<()> {
    let path = std::path::absolute(source)?;
    if !path.join("index.js").is_file() {
        bail!("Failed to import module: index.js not found in {}", path.display());
    }
    output::info(&format!("Running tool \"{tool}\"..."));
    let outcome = runner::run(&path, runner::Mode::Run { tool, input }).await?;
    if outcome.ok {
        output::print(&outcome.result);
        return Ok(());
    }
    let error = outcome.error.unwrap_or_default();
    match outcome.stage.as_deref() {
        Some("import") => bail!("Failed to import module: {error}"),
        Some("validation") => {
            let mut message = error;
            for (path, issue) in &outcome.issues {
                message.push_str(&format!("\n  - {path}: {issue}"));
            }
            output::error(&message);
            output::print(&json!({ "expected": outcome.expected.unwrap_or(Value::Null) }));
            bail!(crate::commands::Silent)
        }
        _ => bail!(error),
    }
}

const TEMPLATE: &str = r#"import z from 'zod';

export const schema = {
    whoami: {
        description: 'returns HTTP headers',
    },
    add: {
        description: 'adds two numbers',
        input: z.object({
            a: z.number(),
            b: z.number(),
        })
    },
};
export function whoami(args, credentials) {
    return JSON.stringify(credentials)
}
export function add({ a, b } = params) {
    return String(Number(a) + Number(b))
}
"#;

/// Writes the template index.js, after asking when the folder already holds files.
pub fn init(target: &Path) -> Result<()> {
    let path = std::path::absolute(target)?;
    if path.exists() {
        let has_files = std::fs::read_dir(&path)?.next().is_some();
        if has_files {
            let proceed = dialoguer::Confirm::new()
                .with_prompt(format!(
                    "The directory {} is not empty. Do you want to initialize the source code template here?",
                    path.display()
                ))
                .default(false)
                .interact()?;
            if !proceed {
                output::info("Initialization cancelled.");
                return Ok(());
            }
        }
    } else {
        std::fs::create_dir_all(&path)?;
    }
    std::fs::write(path.join("index.js"), TEMPLATE)?;
    output::info(&format!("Initialized FaaS server source code template at {}", path.display()));
    Ok(())
}

/// The files that make up the deployment: everything below the folder except dot files and dot
/// folders, zip files at the top, and Windows thumbnail caches.
fn deployment_files(source: &Path) -> Result<Vec<(PathBuf, String)>> {
    let mut files = Vec::new();
    let walker = walkdir::WalkDir::new(source).follow_links(false).sort_by_file_name().into_iter();
    for entry in
        walker.filter_entry(|entry| entry.depth() == 0 || !entry.file_name().to_string_lossy().starts_with('.'))
    {
        let entry = entry?;
        let is_file = entry.file_type().is_file() || (entry.file_type().is_symlink() && entry.path().is_file());
        if !is_file {
            continue;
        }
        let relative = entry.path().strip_prefix(source)?;
        let name = relative.components().map(|part| part.as_os_str().to_string_lossy()).collect::<Vec<_>>().join("/");
        let file_name = entry.file_name().to_string_lossy();
        if (entry.depth() == 1 && file_name.ends_with(".zip")) || file_name == "Thumbs.db" {
            continue;
        }
        files.push((entry.path().to_path_buf(), name));
    }
    Ok(files)
}

/// A file time as zip stores it: local time, two-second precision, 1980 to 2107.
fn zip_time(time: std::time::SystemTime) -> Option<zip::DateTime> {
    use chrono::{Datelike, Timelike};
    let local = chrono::DateTime::<chrono::Local>::from(time);
    zip::DateTime::from_date_and_time(
        u16::try_from(local.year()).ok()?,
        local.month() as u8,
        local.day() as u8,
        local.hour() as u8,
        local.minute() as u8,
        local.second() as u8,
    )
    .ok()
}

/// Zips the folder into a temporary file, removed when the handle drops.
pub fn create_zip(source: &Path) -> Result<tempfile::NamedTempFile> {
    let mut archive_file = tempfile::Builder::new().prefix("faas-function-").suffix(".zip").tempfile()?;
    {
        let mut zip = zip::ZipWriter::new(archive_file.as_file_mut());
        for (path, name) in deployment_files(source)? {
            let mut options = zip::write::SimpleFileOptions::default()
                .compression_method(zip::CompressionMethod::Deflated)
                .compression_level(Some(9));
            let metadata = std::fs::metadata(&path)?;
            if let Some(modified) = metadata.modified().ok().and_then(zip_time) {
                options = options.last_modified_time(modified);
            }
            #[cfg(unix)]
            {
                use std::os::unix::fs::PermissionsExt;
                options = options.unix_permissions(metadata.permissions().mode() & 0o777);
            }
            zip.start_file(name, options)?;
            zip.write_all(&std::fs::read(&path)?)?;
        }
        zip.finish()?;
    }
    Ok(archive_file)
}

fn source_code_url(api: &gatana_api::Client, slug: &str) -> Result<url::Url> {
    Ok(api.url(&format!("/api/v1/mcp-servers/{}/source-code", gatana_api::encode_path_segment(slug)))?)
}

async fn failure(response: reqwest::Response, what: &str) -> anyhow::Error {
    let status = response.status();
    let body = response.text().await.unwrap_or_else(|_| format!("HTTP {status}"));
    anyhow!("Failed to {what} ({}): {body}", status.as_u16())
}

pub async fn upload(api: &gatana_api::Client, slug: &str, zip_path: &Path) -> Result<()> {
    let url = source_code_url(api, slug)?;
    gatana_api::debug!("gatana:http", "→ PUT {url}");
    let part = reqwest::multipart::Part::bytes(std::fs::read(zip_path)?)
        .file_name("function.zip")
        .mime_str("application/octet-stream")?;
    let form = reqwest::multipart::Form::new().part("file", part);
    let response = api.request(reqwest::Method::PUT, url.clone()).multipart(form).send().await?;
    gatana_api::debug!("gatana:http", "← {} PUT {url}", response.status());
    if response.status() != reqwest::StatusCode::OK {
        return Err(failure(response, "upload ZIP file").await);
    }
    Ok(())
}

pub async fn download(api: &gatana_api::Client, slug: &str, out: Option<&Path>) -> Result<()> {
    let url = source_code_url(api, slug)?;
    gatana_api::debug!("gatana:http", "→ GET {url}");
    let response = api.request(reqwest::Method::GET, url.clone()).send().await?;
    gatana_api::debug!("gatana:http", "← {} GET {url}", response.status());
    if !response.status().is_success() {
        return Err(failure(response, "download source code").await);
    }
    let path = std::path::absolute(out.map(Path::to_path_buf).unwrap_or_else(|| PathBuf::from(format!("{slug}.zip"))))?;
    std::fs::write(&path, response.bytes().await?)?;
    output::info(&format!("Downloaded source code to {}", path.display()));
    Ok(())
}

/// Prints the verification of local source code; fails when a tool is not valid.
pub async fn print_verification(source: &Path) -> Result<()> {
    let result = verify(source).await?;
    let valid = result.get("valid").and_then(Value::as_bool).unwrap_or(false);
    output::output(&result, Options::default());
    if !valid {
        bail!(crate::commands::Silent);
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_zip_leaves_out_dot_files_top_level_zips_and_thumbnails() {
        let dir = tempfile::tempdir().unwrap();
        let root = dir.path();
        for file in
            ["index.js", "lib/util.js", ".env", ".git/config", "old.zip", "lib/nested.zip", "Thumbs.db", "lib/.hidden"]
        {
            let path = root.join(file);
            std::fs::create_dir_all(path.parent().unwrap()).unwrap();
            std::fs::write(path, "x").unwrap();
        }
        let names: Vec<String> = deployment_files(root).unwrap().into_iter().map(|(_, name)| name).collect();
        assert_eq!(names, vec!["index.js", "lib/nested.zip", "lib/util.js"]);
        let archive = create_zip(root).unwrap();
        let mut zip = zip::ZipArchive::new(std::fs::File::open(archive.path()).unwrap()).unwrap();
        assert_eq!(zip.len(), 3);
        assert_eq!(zip.by_index(0).unwrap().name(), "index.js");
    }

    #[test]
    fn tool_input_layers_params_over_json() {
        let input =
            tool_input(Some(r#"{"a": 1}"#), None, &["b.c=2".into(), "s=text".into(), "l=[1,2]".into()]).unwrap();
        assert_eq!(input, json!({"a": 1, "b": {"c": 2}, "s": "text", "l": [1, 2]}));
        assert!(tool_input(None, None, &["novalue".into()]).is_err());
    }

    #[test]
    fn the_static_check_finds_both_export_styles() {
        let dir = tempfile::tempdir().unwrap();
        assert!(!check_index_js(dir.path()).unwrap().exists);
        std::fs::write(dir.path().join("index.js"), "module.exports.schema = {}").unwrap();
        assert!(check_index_js(dir.path()).unwrap().has_schema);
        std::fs::write(dir.path().join("index.js"), "export function x() {}").unwrap();
        assert!(!check_index_js(dir.path()).unwrap().has_schema);
    }
}
