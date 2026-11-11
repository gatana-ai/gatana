//! Alerts: the rules, the notification channels they send to, and the history of what was sent.
//! A rule is an audit log filter with a threshold. A channel is a destination of one kind, such as
//! email or webhook. The kinds and their settings come from the API, so a kind that the backend
//! adds needs no change here. Only organization owners reach these routes.

use super::{MASK, Silent, array_at, resolve, text_at};
use crate::cli::{AlertCommand, ChannelCommand, CreateAlertArgs, CreateChannelArgs};
use crate::context::Context;
use crate::output::{self, Column, Options};
use crate::util::{format_age, read_piped_stdin};
use anyhow::{Result, anyhow, bail};
use gatana_api::v1::query;
use serde_json::{Map, Value, json};

const ALERT_COLUMNS: [Column; 7] = [
    Column::path("Name", "name"),
    Column::path("Enabled", "isEnabled"),
    Column::computed("Notify When", |row| {
        json!(format!("{} in {}m", number_at(row, "threshold"), number_at(row, "windowMinutes")))
    }),
    Column::computed("Cooldown", |row| json!(format!("{}m", number_at(row, "cooldownMinutes")))),
    Column::computed("Channels", |row| {
        if row.get("allChannels") == Some(&Value::Bool(true)) {
            return json!("<all>");
        }
        let channels = row_channels(row);
        let names: Vec<&str> = channels.iter().filter_map(|channel| text_at(channel, "/name")).collect();
        if names.is_empty() { Value::Null } else { json!(names.join(", ")) }
    }),
    Column::path("Matches 7d", "matchesLastSevenDays"),
    Column::computed("Last Alert", |row| age_or(row.get("lastNotifiedAt"), "<never>")),
];

const CHANNEL_COLUMNS: [Column; 6] = [
    Column::path("Name", "name"),
    Column::path("Kind", "kindLabel"),
    Column::path("Enabled", "isEnabled"),
    Column::computed("Status", |row| {
        let failures = row.get("consecutiveFailures").and_then(Value::as_u64).unwrap_or(0);
        if row.get("isKindAvailable") == Some(&Value::Bool(false)) {
            json!("kind not available")
        } else if failures > 0 {
            json!(format!("failing ({failures})"))
        } else if row.get("lastSuccessAt").is_none_or(Value::is_null) {
            json!("not used")
        } else {
            json!("ok")
        }
    }),
    Column::computed("Last Success", |row| age_or(row.get("lastSuccessAt"), "<never>")),
    Column::computed("Age", |row| json!(format_age(row.get("createdAt")))),
];

const HISTORY_COLUMNS: [Column; 4] = [
    Column::computed("Sent", |row| json!(format_age(row.get("createdAt")))),
    Column::path("Type", "typeLabel"),
    Column::path("Title", "message.title"),
    Column::computed("Deliveries", |row| {
        let deliveries: Vec<String> = array_at(row, "deliveries")
            .iter()
            .map(|delivery| {
                format!(
                    "{}: {}",
                    text_at(delivery, "/channelName").unwrap_or_default(),
                    text_at(delivery, "/status").unwrap_or_default()
                )
            })
            .collect();
        if deliveries.is_empty() { Value::Null } else { json!(deliveries.join(", ")) }
    }),
];

const PREVIEW_COLUMNS: [Column; 2] = [Column::path("Last Days", "days"), Column::path("Matches", "matches")];

fn name_of(row: &Value) -> &str {
    text_at(row, "/name").unwrap_or_default()
}

fn number_at(row: &Value, key: &str) -> String {
    row.get(key).filter(|value| !value.is_null()).map(Value::to_string).unwrap_or_else(|| "?".into())
}

fn age_or(value: Option<&Value>, none: &str) -> Value {
    match value {
        Some(value) if !value.is_null() => json!(format_age(Some(value))),
        _ => json!(none),
    }
}

fn row_channels(rule: &Value) -> Vec<Value> {
    array_at(rule, "channels")
}

/// `field:operator:value`, the form of a filter in the address of the Audit Logs page. The value
/// keeps its colons. The backend knows the fields and the operators, and checks them.
pub(crate) fn parse_condition(text: &str) -> Result<Value> {
    let mut parts = text.splitn(3, ':');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(field), Some(operator), Some(value))
            if !field.is_empty() && !operator.is_empty() && !value.is_empty() =>
        {
            Ok(json!({ "field": field, "operator": operator, "value": value }))
        }
        _ => bail!("Invalid condition \"{text}\". Expected field:operator:value, for example outcome:eq:denied"),
    }
}

fn parse_conditions(texts: &[String]) -> Result<Vec<Value>> {
    texts.iter().map(|text| parse_condition(text)).collect()
}

/// A condition as `--where` takes it.
fn condition_text(condition: &Value) -> Value {
    let part = |key: &str| condition.get(key).and_then(Value::as_str).unwrap_or_default();
    json!(format!("{}:{}:{}", part("field"), part("operator"), part("value")))
}

/// The rule list with its 7-day match counts, which can take seconds on a large audit log.
async fn list_rules(api: &gatana_api::Client) -> Result<Value> {
    Ok(api.v1().list_alert_rules(&query::ListAlertRules::default()).value().await?)
}

fn find_rule(list: &Value, name: &str) -> Result<Value> {
    resolve::find_one(&array_at(list, "rules"), name, "alert", "\"gatana get alerts\"")
}

pub async fn get(context: &Context, name: Option<&str>) -> Result<()> {
    let list = list_rules(context.api().await?).await?;
    if let Some(name) = name {
        output::output(&find_rule(&list, name)?, Options::yaml());
        return Ok(());
    }
    output::output(&json!({ "alerts": array_at(&list, "rules") }), Options::columns(&ALERT_COLUMNS));
    if list.pointer("/dailyLimit/isReached") == Some(&Value::Bool(true)) && !output::machine_readable() {
        output::println(&output::yellow(&format!(
            "The organization reached its limit of {} alerts a day. Alerts are paused until midnight UTC.",
            number_at(&list["dailyLimit"], "limit")
        )));
    }
    Ok(())
}

/// The rule with its conditions as `--where` takes them, and the daily limit that all rules share.
pub async fn describe(context: &Context, name: &str) -> Result<()> {
    let list = list_rules(context.api().await?).await?;
    let mut rule = find_rule(&list, name)?;
    let conditions: Vec<Value> = array_at(&rule, "conditions").iter().map(condition_text).collect();
    let channels: Vec<Value> = row_channels(&rule)
        .iter()
        .map(|channel| {
            json!({ "name": channel.get("name"), "kind": channel.get("kindLabel"), "enabled": channel.get("isEnabled") })
        })
        .collect();
    rule["conditions"] = Value::Array(conditions);
    rule["channels"] = Value::Array(channels);
    output::output(&json!({ "alert": rule, "dailyLimit": list.get("dailyLimit") }), Options::yaml());
    Ok(())
}

pub async fn create(context: &Context, args: CreateAlertArgs) -> Result<()> {
    let api = context.api().await?;
    let conditions = parse_conditions(&args.conditions.conditions)?;
    // Found before the rule exists, so that a wrong name leaves nothing half made
    let channel_ids = channel_ids(api, &args.channels).await?;
    let mut body = json!({
        "name": args.name,
        "conditions": conditions,
        "isEnabled": !args.disabled,
        "allChannels": args.all_channels,
        "channelIds": channel_ids,
    });
    // The keys left out take the defaults of the backend
    for (key, value) in
        [("threshold", args.threshold), ("windowMinutes", args.window), ("cooldownMinutes", args.cooldown)]
    {
        if let Some(value) = value {
            body[key] = json!(value);
        }
    }
    let created = api.v1().create_alert_rule_raw(body).value().await?;
    if output::machine_readable() {
        output::print(&created);
        return Ok(());
    }
    let condition = format!(
        "notifies when {} within {} minutes",
        match number_at(&created, "threshold").as_str() {
            "1" => "1 event matches".to_string(),
            count => format!("{count} events match"),
        },
        number_at(&created, "windowMinutes")
    );
    if args.disabled {
        output::success(&format!("Created alert '{}', disabled. When enabled, it {condition}.", args.name));
        output::println(&format!("Enable it: gatana alert enable '{}'", args.name));
    } else {
        output::success(&format!("Created alert '{}': {condition}.", args.name));
    }
    if !args.all_channels && args.channels.is_empty() {
        output::println(&format!(
            "The rule has no channel, so it sends nothing. Add one: gatana alert add-channel '{}' <channel>",
            args.name
        ));
    }
    Ok(())
}

/// The IDs of channels given by name or ID, from one read of the list.
async fn channel_ids(api: &gatana_api::Client, names: &[String]) -> Result<Vec<String>> {
    if names.is_empty() {
        return Ok(Vec::new());
    }
    let rows = array_at(&api.v1().list_notification_channels().value().await?, "channels");
    let mut ids = Vec::new();
    for name in names {
        let id = resolve::id(&resolve::find_one(&rows, name, "channel", "\"gatana get channels\"")?).to_string();
        if !ids.contains(&id) {
            ids.push(id);
        }
    }
    Ok(ids)
}

pub async fn patch(context: &Context, name: &str, body: Value) -> Result<()> {
    let api = context.api().await?;
    let rule = resolve::alert(api, name).await?;
    if !body.is_object() {
        bail!("The patch must be a JSON object.");
    }
    // Every field of the update is optional, so the keys left out keep their values
    api.v1().update_alert_rule_raw(resolve::id(&rule), body).send().await?;
    output::success(&format!("Updated alert '{}'.", name_of(&rule)));
    Ok(())
}

pub async fn delete(context: &Context, name: &str) -> Result<()> {
    let api = context.api().await?;
    let rule = resolve::alert(api, name).await?;
    api.v1().delete_alert_rule(resolve::id(&rule)).send().await?;
    output::success(&format!("Deleted alert '{}'.", name_of(&rule)));
    Ok(())
}

pub async fn run(context: &Context, command: AlertCommand) -> Result<()> {
    let api = context.api().await?;
    match command {
        AlertCommand::Enable { alert } => set_rule_enabled(api, &alert, true).await?,
        AlertCommand::Disable { alert } => set_rule_enabled(api, &alert, false).await?,
        AlertCommand::Preview { conditions } => {
            let body = json!({ "conditions": parse_conditions(&conditions.conditions)? });
            let preview = api.v1().preview_alert_rule_raw(body).value().await?;
            output::output(&json!({ "periods": array_at(&preview, "periods") }), Options::columns(&PREVIEW_COLUMNS));
        }
        AlertCommand::AddChannel { alert, channels } => {
            let rule = resolve::alert(api, &alert).await?;
            if rule.get("allChannels") == Some(&Value::Bool(true)) {
                bail!("Alert '{}' already sends to every channel.", name_of(&rule));
            }
            let mut ids: Vec<String> = row_channels(&rule).iter().map(|row| resolve::id(row).to_string()).collect();
            let had_channels = !ids.is_empty();
            for id in channel_ids(api, &channels).await? {
                if !ids.contains(&id) {
                    ids.push(id);
                }
            }
            api.v1().update_alert_rule_raw(resolve::id(&rule), json!({ "channelIds": ids })).send().await?;
            let also = if had_channels { "also " } else { "" };
            output::success(&format!("Alert '{}' now {also}sends to {}.", name_of(&rule), channels.join(", ")));
        }
        AlertCommand::RemoveChannel { alert, channels } => {
            let rule = resolve::alert(api, &alert).await?;
            if rule.get("allChannels") == Some(&Value::Bool(true)) {
                bail!(
                    "Alert '{0}' sends to every channel. To choose the channels, run: gatana patch alert '{0}' -p allChannels=false",
                    name_of(&rule)
                );
            }
            let current: Vec<String> = row_channels(&rule).iter().map(|row| resolve::id(row).to_string()).collect();
            let removed = channel_ids(api, &channels).await?;
            if let Some(position) = removed.iter().position(|id| !current.contains(id)) {
                bail!("Alert '{}' does not send to channel '{}'.", name_of(&rule), channels[position]);
            }
            let ids: Vec<&String> = current.iter().filter(|id| !removed.contains(id)).collect();
            api.v1().update_alert_rule_raw(resolve::id(&rule), json!({ "channelIds": ids })).send().await?;
            output::success(&format!("Alert '{}' no longer sends to {}.", name_of(&rule), channels.join(", ")));
            if ids.is_empty() {
                output::info("The rule has no channel now, so it sends nothing.");
            }
        }
    }
    Ok(())
}

/// A rule that is enabled again starts at the newest audit log event, so a rule that already has
/// the state is left alone.
async fn set_rule_enabled(api: &gatana_api::Client, name: &str, enabled: bool) -> Result<()> {
    let rule = resolve::alert(api, name).await?;
    let state = if enabled { "enabled" } else { "disabled" };
    if rule.get("isEnabled") == Some(&Value::Bool(enabled)) {
        output::success(&format!("Alert '{}' is already {state}.", name_of(&rule)));
        return Ok(());
    }
    api.v1().update_alert_rule_raw(resolve::id(&rule), json!({ "isEnabled": enabled })).send().await?;
    output::success(&format!("Alert '{}' is now {state}.", name_of(&rule)));
    Ok(())
}

/// The fields of a channel kind: key, type, label and whether a value is required.
async fn kind_fields(api: &gatana_api::Client, kind: &str) -> Result<Vec<Value>> {
    let kinds = array_at(&api.v1().list_notification_channel_kinds().value().await?, "kinds");
    let Some(found) = kinds.iter().find(|row| text_at(row, "/kind") == Some(kind)) else {
        let names: Vec<&str> = kinds.iter().filter_map(|row| text_at(row, "/kind")).collect();
        bail!("No channel kind \"{kind}\". The kinds are: {}.", names.join(", "));
    };
    Ok(array_at(found, "fields"))
}

fn field_of<'a>(fields: &'a [Value], kind: &str, key: &str) -> Result<&'a Value> {
    fields.iter().find(|field| text_at(field, "/key") == Some(key)).ok_or_else(|| {
        let keys: Vec<&str> = fields.iter().filter_map(|field| text_at(field, "/key")).collect();
        anyhow!("The channel kind \"{kind}\" has no field \"{key}\". Its fields are: {}.", keys.join(", "))
    })
}

fn field_type(field: &Value) -> &str {
    text_at(field, "/type").unwrap_or_default()
}

/// A value as its field takes it. The API takes a list of addresses for an email list, which the
/// command line gives with commas. Text stays text: a secret such as "007" must not become a number.
fn shaped(field: &Value, key: &str, value: Value) -> Result<Value> {
    match value {
        Value::Null => Ok(Value::Null),
        Value::String(text) if field_type(field) == "email-list" => {
            Ok(json!(text.split(',').map(str::trim).filter(|part| !part.is_empty()).collect::<Vec<_>>()))
        }
        Value::Array(_) if field_type(field) == "email-list" => Ok(value),
        Value::String(_) => Ok(value),
        _ => bail!(
            "values.{key} must be text. For a value that looks like a number or a boolean, give the patch as JSON: -p '{{\"values\": {{\"{key}\": \"123\"}}}}'"
        ),
    }
}

fn split_setting(pair: &str) -> Result<(&str, &str)> {
    pair.split_once('=')
        .filter(|(key, _)| !key.is_empty())
        .ok_or_else(|| anyhow!("Invalid setting \"{pair}\". Expected format: field=value"))
}

/// The value of `--secret field=...`: the text itself, the content of `@<file>`, or stdin for `-`.
/// One newline at the end of a file or of stdin is not part of the secret.
fn secret_value(key: &str, value: &str) -> Result<String> {
    let chomp =
        |text: String| text.strip_suffix('\n').map(|rest| rest.trim_end_matches('\r').to_string()).unwrap_or(text);
    if value == "-" {
        let Some(text) = read_piped_stdin()? else {
            bail!("--secret {key}=- reads the secret from stdin, but nothing is piped in.");
        };
        return Ok(chomp(text));
    }
    match value.strip_prefix('@') {
        Some(path) => Ok(chomp(std::fs::read_to_string(path).map_err(|error| anyhow!("{path}: {error}"))?)),
        None => Ok(value.to_string()),
    }
}

/// The `values` of a new channel from `-s` and `--secret`.
fn new_channel_values(fields: &[Value], args: &CreateChannelArgs) -> Result<Map<String, Value>> {
    let generated = |key: &str| {
        anyhow!(
            "Gatana creates the value of \"{key}\". The new channel prints it, and \"gatana channel rotate-secret\" replaces it."
        )
    };
    let mut values = Map::new();
    for pair in &args.settings {
        let (key, value) = split_setting(pair)?;
        let field = field_of(fields, &args.kind, key)?;
        if field_type(field) == "generated-secret" {
            return Err(generated(key));
        }
        values.insert(key.to_string(), shaped(field, key, json!(value))?);
    }
    for pair in &args.secrets {
        let (key, value) = split_setting(pair)?;
        match field_type(field_of(fields, &args.kind, key)?) {
            "secret" => values.insert(key.to_string(), json!(secret_value(key, value)?)),
            "generated-secret" => return Err(generated(key)),
            _ => bail!("\"{key}\" is not a secret field. Give it with -s {key}=<value>"),
        };
    }
    Ok(values)
}

/// A channel as it is shown: the secrets that Gatana generated are hidden unless asked for. The
/// API never returns the secrets that an owner typed.
fn shown_channel(mut channel: Value, show_secrets: bool) -> Value {
    if !show_secrets && let Some(secrets) = channel.get_mut("secrets").and_then(Value::as_object_mut) {
        for secret in secrets.values_mut() {
            if let Some(value) = secret.get_mut("value") {
                *value = json!(MASK);
            }
        }
    }
    channel
}

pub async fn get_channel(context: &Context, name: Option<&str>, show_secrets: bool) -> Result<()> {
    let api = context.api().await?;
    if let Some(name) = name {
        output::output(&shown_channel(resolve::channel(api, name).await?, show_secrets), Options::yaml());
        return Ok(());
    }
    let channels: Vec<Value> = array_at(&api.v1().list_notification_channels().value().await?, "channels")
        .into_iter()
        .map(|channel| shown_channel(channel, show_secrets))
        .collect();
    output::output(&json!({ "channels": channels }), Options::columns(&CHANNEL_COLUMNS));
    Ok(())
}

/// The channel with the alert rules that send to it.
pub async fn describe_channel(context: &Context, name: &str, show_secrets: bool) -> Result<()> {
    let api = context.api().await?;
    let channel = resolve::channel(api, name).await?;
    let id = resolve::id(&channel).to_string();
    let query = query::ListAlertRules { match_counts: Some("false".into()) };
    let rules = array_at(&api.v1().list_alert_rules(&query).value().await?, "rules");
    let alerts: Vec<Value> = rules
        .iter()
        .filter(|rule| {
            rule.get("allChannels") == Some(&Value::Bool(true))
                || row_channels(rule).iter().any(|row| resolve::id(row) == id)
        })
        .map(|rule| json!({ "name": rule.get("name"), "enabled": rule.get("isEnabled") }))
        .collect();
    output::output(&json!({ "channel": shown_channel(channel, show_secrets), "alerts": alerts }), Options::yaml());
    Ok(())
}

pub async fn create_channel(context: &Context, args: CreateChannelArgs) -> Result<()> {
    let api = context.api().await?;
    let fields = kind_fields(api, &args.kind).await?;
    let values = new_channel_values(&fields, &args)?;
    let body = json!({ "name": args.name, "kind": args.kind, "values": values });
    let created = api.v1().create_notification_channel_raw(body).value().await?;
    if output::machine_readable() {
        output::print(&created);
        return Ok(());
    }
    output::success(&format!("Created {} channel '{}'.", args.kind, args.name));
    if let Some(secrets) = created.get("generatedSecrets").and_then(Value::as_object) {
        for (key, value) in secrets {
            output::println(&format!("{key}: {}", value.as_str().unwrap_or_default()));
        }
    }
    output::println(&format!("Send a test message: gatana channel test '{}'", args.name));
    Ok(())
}

/// What the update is sent. The backend replaces the plain settings whole when it gets `values`,
/// so the stored settings fill in the fields that the patch leaves out. A secret that is left out
/// keeps its value in the backend.
fn merged_channel_patch(channel: &Value, fields: &[Value], patch: Map<String, Value>) -> Result<Map<String, Value>> {
    if patch.contains_key("settings") || patch.contains_key("secrets") {
        bail!(
            "The settings and the secrets of a channel are patched under \"values\", for example -p values.url=https://…"
        );
    }
    let mut body = patch;
    let Some(given) = body.remove("values") else {
        return Ok(body);
    };
    let Value::Object(given) = given else { bail!("\"values\" must be an object of field values.") };
    let kind = text_at(channel, "/kind").unwrap_or_default();
    let mut values = channel.get("settings").and_then(Value::as_object).cloned().unwrap_or_default();
    for (key, value) in given {
        let field = field_of(fields, kind, &key)?;
        let value = shaped(field, &key, value)?;
        values.insert(key, value);
    }
    body.insert("values".into(), Value::Object(values));
    Ok(body)
}

pub async fn patch_channel(context: &Context, name: &str, body: Value) -> Result<()> {
    let api = context.api().await?;
    let channel = resolve::channel(api, name).await?;
    let Value::Object(patch) = body else { bail!("The patch must be a JSON object.") };
    let fields = match patch.contains_key("values") {
        true => kind_fields(api, text_at(&channel, "/kind").unwrap_or_default()).await?,
        false => Vec::new(),
    };
    let body = merged_channel_patch(&channel, &fields, patch)?;
    api.v1().update_notification_channel_raw(resolve::id(&channel), Value::Object(body)).send().await?;
    output::success(&format!("Updated channel '{}'.", name_of(&channel)));
    Ok(())
}

pub async fn delete_channel(context: &Context, name: &str) -> Result<()> {
    let api = context.api().await?;
    let channel = resolve::channel(api, name).await?;
    api.v1().delete_notification_channel(resolve::id(&channel)).send().await?;
    output::success(&format!("Deleted channel '{}'.", name_of(&channel)));
    Ok(())
}

pub async fn run_channel(context: &Context, command: ChannelCommand) -> Result<()> {
    let api = context.api().await?;
    match command {
        ChannelCommand::Kinds => {
            let kinds = api.v1().list_notification_channel_kinds().value().await?;
            output::output(&json!({ "kinds": array_at(&kinds, "kinds") }), Options::yaml());
        }
        ChannelCommand::Test { channel } => {
            let channel = resolve::channel(api, &channel).await?;
            let result = api.v1().test_notification_channel(resolve::id(&channel)).value().await?;
            let sent = result.get("success") == Some(&Value::Bool(true));
            if output::machine_readable() {
                output::print(&result);
            } else if sent {
                output::success(&format!(
                    "Sent a test message through channel '{}' in {} ms.",
                    name_of(&channel),
                    number_at(&result, "durationMs")
                ));
            } else {
                output::error(&format!(
                    "The test message through channel '{}' failed: {}",
                    name_of(&channel),
                    text_at(&result, "/error").unwrap_or("no error was given")
                ));
            }
            if !sent {
                return Err(Silent.into());
            }
        }
        ChannelCommand::RotateSecret { channel, field } => {
            let channel = resolve::channel(api, &channel).await?;
            let field = match field {
                Some(field) => field,
                None => only_generated_secret(api, &channel).await?,
            };
            let rotated = api
                .v1()
                .rotate_notification_channel_secret_raw(resolve::id(&channel), json!({ "field": field }))
                .value()
                .await?;
            if output::machine_readable() {
                output::print(&rotated);
                return Ok(());
            }
            output::success(&format!(
                "Replaced {field} of channel '{}'. The old value no longer works.",
                name_of(&channel)
            ));
            output::println(&format!("{field}: {}", text_at(&rotated, "/value").unwrap_or_default()));
        }
        ChannelCommand::Enable { channel } => set_channel_enabled(api, &channel, true).await?,
        ChannelCommand::Disable { channel } => set_channel_enabled(api, &channel, false).await?,
    }
    Ok(())
}

/// The one secret that Gatana generates for channels of this kind.
async fn only_generated_secret(api: &gatana_api::Client, channel: &Value) -> Result<String> {
    let kind = text_at(channel, "/kind").unwrap_or_default();
    let fields = kind_fields(api, kind).await?;
    let generated: Vec<&str> = fields
        .iter()
        .filter(|field| field_type(field) == "generated-secret")
        .filter_map(|field| text_at(field, "/key"))
        .collect();
    match generated.as_slice() {
        [field] => Ok(field.to_string()),
        [] => bail!("The channel kind \"{kind}\" has no secret that Gatana generates."),
        fields => bail!("The channel kind \"{kind}\" has several generated secrets. Name one: {}.", fields.join(", ")),
    }
}

async fn set_channel_enabled(api: &gatana_api::Client, name: &str, enabled: bool) -> Result<()> {
    let channel = resolve::channel(api, name).await?;
    api.v1().update_notification_channel_raw(resolve::id(&channel), json!({ "isEnabled": enabled })).send().await?;
    let state = if enabled { "enabled" } else { "disabled" };
    output::success(&format!("Channel '{}' is now {state}.", name_of(&channel)));
    Ok(())
}

/// What Gatana sent, newest first, with the delivery to each channel.
pub async fn history(context: &Context, limit: u32, page: u32) -> Result<()> {
    let api = context.api().await?;
    let query = query::ListNotifications { page: Some(page.to_string()), limit: Some(limit.to_string()) };
    let list = api.v1().list_notifications(&query).value().await?;
    let shown = json!({ "notifications": array_at(&list, "data"), "pagination": list.get("pagination") });
    output::output(&shown, Options::columns(&HISTORY_COLUMNS));
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn webhook_fields() -> Vec<Value> {
        vec![
            json!({ "key": "url", "type": "url" }),
            json!({ "key": "authHeaderName", "type": "text" }),
            json!({ "key": "authHeaderValue", "type": "secret" }),
            json!({ "key": "signingSecret", "type": "generated-secret" }),
        ]
    }

    fn channel_args(kind: &str, settings: &[&str], secrets: &[&str]) -> CreateChannelArgs {
        CreateChannelArgs {
            name: "x".into(),
            kind: kind.into(),
            settings: settings.iter().map(|text| text.to_string()).collect(),
            secrets: secrets.iter().map(|text| text.to_string()).collect(),
        }
    }

    #[test]
    fn a_condition_is_field_operator_value_and_the_value_keeps_its_colons() {
        assert_eq!(
            parse_condition("outcome:eq:denied").unwrap(),
            json!({ "field": "outcome", "operator": "eq", "value": "denied" })
        );
        let condition = parse_condition("toolName:contains:a:b").unwrap();
        assert_eq!(condition["value"], json!("a:b"));
        assert_eq!(condition_text(&condition), json!("toolName:contains:a:b"));
        assert!(parse_condition("outcome=denied").is_err());
        assert!(parse_condition("outcome:eq:").is_err());
    }

    #[test]
    fn new_channel_values_follow_the_fields_of_the_kind() {
        let fields = webhook_fields();
        let dir = tempfile::tempdir().unwrap();
        let file = dir.path().join("key.txt");
        std::fs::write(&file, "007\n").unwrap();
        let secret = format!("authHeaderValue=@{}", file.display());
        let args = channel_args("webhook", &["url=https://x.example/?a=b", "authHeaderName=X-Key"], &[&secret]);
        assert_eq!(
            Value::Object(new_channel_values(&fields, &args).unwrap()),
            json!({ "url": "https://x.example/?a=b", "authHeaderName": "X-Key", "authHeaderValue": "007" })
        );

        let error = |settings: &[&str], secrets: &[&str]| {
            new_channel_values(&fields, &channel_args("webhook", settings, secrets)).unwrap_err().to_string()
        };
        assert!(
            error(&["uri=https://x"], &[])
                .starts_with("The channel kind \"webhook\" has no field \"uri\". Its fields are: url,")
        );
        assert!(error(&[], &["url=https://x"]).contains("is not a secret field"));
        assert!(error(&["signingSecret=abc"], &[]).starts_with("Gatana creates the value"));
        assert!(error(&["url"], &[]).starts_with("Invalid setting"));

        let email = vec![json!({ "key": "recipients", "type": "email-list" })];
        let args = channel_args("email", &["recipients=ada@example.com, bob@example.com,"], &[]);
        assert_eq!(
            new_channel_values(&email, &args).unwrap()["recipients"],
            json!(["ada@example.com", "bob@example.com"])
        );
    }

    #[test]
    fn a_channel_patch_keeps_the_settings_it_leaves_out() {
        let channel = json!({
            "kind": "webhook",
            "settings": { "url": "https://old.example", "authHeaderName": "X-Key" },
            "secrets": { "authHeaderValue": { "hasValue": true } },
        });
        let patch =
            |value: Value| merged_channel_patch(&channel, &webhook_fields(), value.as_object().unwrap().clone());
        // Without values, the backend keeps every setting, so nothing is added
        assert_eq!(Value::Object(patch(json!({ "name": "new" })).unwrap()), json!({ "name": "new" }));
        assert_eq!(
            Value::Object(
                patch(json!({ "values": { "url": "https://new.example", "authHeaderValue": null } })).unwrap()
            ),
            json!({ "values": { "url": "https://new.example", "authHeaderName": "X-Key", "authHeaderValue": null } })
        );
        // -p values.authHeaderValue=007 arrives as the number 7, which is not what was typed
        assert!(patch(json!({ "values": { "authHeaderValue": 7 } })).unwrap_err().to_string().contains("must be text"));
        assert!(
            patch(json!({ "settings": { "url": "https://x" } })).unwrap_err().to_string().contains("under \"values\"")
        );
        assert!(patch(json!({ "values": { "uri": "x" } })).is_err());
    }

    #[test]
    fn generated_secrets_are_hidden_unless_asked_for() {
        let channel = json!({ "secrets": { "authHeaderValue": { "hasValue": true }, "signingSecret": { "hasValue": true, "value": "whsec_1" } } });
        let hidden = shown_channel(channel.clone(), false);
        assert_eq!(hidden["secrets"]["signingSecret"]["value"], json!(MASK));
        assert_eq!(hidden["secrets"]["authHeaderValue"], json!({ "hasValue": true }));
        assert_eq!(shown_channel(channel.clone(), true), channel);
    }
}
