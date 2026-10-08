mod common;

use common::{Change, FakeSkillsApi};
use gatana_cli::skills::api::SkillsApi;
use gatana_cli::skills::frontmatter::parse_skill_md;
use gatana_cli::skills::manifest::read_manifest;
use gatana_cli::skills::push::{PushAction, PushOptions, PushResult, push_skills};
use gatana_cli::skills::sync::{SkillsIdentity, SyncOptions, sync_directory};
use gatana_cli::util::iso_millis;
use serde_json::json;
use std::path::{Path, PathBuf};

fn identity() -> SkillsIdentity {
    SkillsIdentity { org_id: "acme".into(), base_url: "https://acme.example".into() }
}

fn sync_defaults() -> SyncOptions {
    SyncOptions { dry_run: false, prune: true, force: false, ..SyncOptions::default() }
}

fn push_defaults() -> PushOptions {
    PushOptions::default()
}

fn write_skill(dir: &Path, name: &str, body: &str, front: Option<&str>) -> PathBuf {
    let front =
        front.map(str::to_string).unwrap_or_else(|| format!("name: {name}\ndescription: Use for {name}\nlicense: MIT"));
    std::fs::create_dir_all(dir.join(name)).unwrap();
    let file = dir.join(name).join("SKILL.md");
    std::fs::write(&file, format!("---\n{front}\n---\n\n{body}")).unwrap();
    file
}

fn brief(results: &[PushResult]) -> Vec<String> {
    results
        .iter()
        .map(|result| format!("{}:{}", result.name, serde_json::to_value(result.action).unwrap().as_str().unwrap()))
        .collect()
}

fn stamped(file: &Path) -> gatana_cli::skills::frontmatter::SkillFrontmatter {
    parse_skill_md(&std::fs::read_to_string(file).unwrap()).unwrap().0
}

#[tokio::test]
async fn a_new_hand_written_skill_is_created_and_stamped_and_pushing_again_is_unchanged() {
    let api = FakeSkillsApi::new();
    let dir = tempfile::tempdir().unwrap();
    let file = write_skill(dir.path(), "fresh", "Do the thing.\n", None);

    let created = push_skills(&api, &identity(), std::slice::from_ref(&file), &push_defaults()).await.unwrap();
    assert_eq!(created[0].action, PushAction::Created);
    let (frontmatter, body) = parse_skill_md(&std::fs::read_to_string(&file).unwrap()).unwrap();
    assert_eq!(frontmatter.meta("gatana-org"), Some("acme"));
    assert!(frontmatter.meta("gatana-id").is_some());
    assert_eq!(serde_json::Value::Object(frontmatter.extra), json!({ "license": "MIT" }));
    assert_eq!(body, "Do the thing.\n");

    let again = push_skills(&api, &identity(), std::slice::from_ref(&file), &push_defaults()).await.unwrap();
    assert_eq!(again[0].action, PushAction::Unchanged);
    assert!(!api.calls().iter().any(|call| call.starts_with("update")));
}

#[tokio::test]
async fn a_synced_file_that_was_edited_updates_its_skill_and_the_manifest_so_the_next_sync_is_clean() {
    let api = FakeSkillsApi::new();
    let a = api.seed("alpha", "v1\n");
    let dir = tempfile::tempdir().unwrap();
    sync_directory(&api, &identity(), dir.path(), &sync_defaults()).await.unwrap();
    let file = dir.path().join("alpha/SKILL.md");
    let text = std::fs::read_to_string(&file).unwrap();
    std::fs::write(&file, text.replace("v1", "v2")).unwrap();

    let updated = push_skills(&api, &identity(), &[dir.path().join("alpha")], &push_defaults()).await.unwrap();
    assert_eq!(updated[0].action, PushAction::Updated);
    assert_eq!(api.content_of(&a.id).as_deref(), Some("v2\n"));
    let manifest = read_manifest(dir.path()).unwrap().unwrap();
    let current = api.get(&a.id).await.unwrap();
    assert_eq!(Some(manifest.skills[&a.id].updated_at.clone()), iso_millis(&current.skill.updated_at));

    let summary = sync_directory(&api, &identity(), dir.path(), &sync_defaults()).await.unwrap();
    assert_eq!(summary.written, 0);
    assert!(summary.warnings.is_empty());
}

#[tokio::test]
async fn a_server_side_change_after_the_local_copy_is_a_conflict_unless_forced() {
    let api = FakeSkillsApi::new();
    let a = api.seed("alpha", "v1\n");
    let dir = tempfile::tempdir().unwrap();
    sync_directory(&api, &identity(), dir.path(), &sync_defaults()).await.unwrap();
    let file = dir.path().join("alpha/SKILL.md");
    std::fs::write(&file, std::fs::read_to_string(&file).unwrap().replace("v1", "mine")).unwrap();
    api.change(&a.id, Change { content: Some("theirs\n".into()), ..Change::default() }).unwrap();

    let conflict = push_skills(&api, &identity(), std::slice::from_ref(&file), &push_defaults()).await.unwrap();
    assert_eq!(conflict[0].action, PushAction::Conflict);
    assert_eq!(api.content_of(&a.id).as_deref(), Some("theirs\n"));

    let forced =
        push_skills(&api, &identity(), std::slice::from_ref(&file), &PushOptions { force: true, ..push_defaults() })
            .await
            .unwrap();
    assert_eq!(forced[0].action, PushAction::Updated);
    assert_eq!(api.content_of(&a.id).as_deref(), Some("mine\n"));
}

#[tokio::test]
async fn a_new_file_whose_name_exists_on_the_server_needs_a_baseline() {
    let api = FakeSkillsApi::new();
    api.seed("taken", "server\n");
    let dir = tempfile::tempdir().unwrap();
    let file = write_skill(dir.path(), "taken", "local\n", None);
    let conflict = push_skills(&api, &identity(), std::slice::from_ref(&file), &push_defaults()).await.unwrap();
    assert_eq!(conflict[0].action, PushAction::Conflict);
    assert!(conflict[0].detail.contains("no install baseline"));
    let forced =
        push_skills(&api, &identity(), std::slice::from_ref(&file), &PushOptions { force: true, ..push_defaults() })
            .await
            .unwrap();
    assert_eq!(forced[0].action, PushAction::Updated);
}

#[tokio::test]
async fn a_directory_of_skill_folders_pushes_each_and_bad_files_do_not_stop_the_rest() {
    let api = FakeSkillsApi::new();
    let dir = tempfile::tempdir().unwrap();
    write_skill(dir.path(), "good-one", "A\n", None);
    write_skill(dir.path(), "bad-one", "B\n", Some("name: Bad Name\ndescription: x"));
    write_skill(dir.path(), "good-two", "C\n", None);
    let results = push_skills(&api, &identity(), &[dir.path().to_path_buf()], &push_defaults()).await.unwrap();
    assert_eq!(brief(&results), vec!["bad-one:error", "good-one:created", "good-two:created"]);
}

#[tokio::test]
async fn a_file_from_another_organization_is_refused_without_force() {
    let api = FakeSkillsApi::new();
    let dir = tempfile::tempdir().unwrap();
    let file = write_skill(
        dir.path(),
        "foreign",
        "X\n",
        Some("name: foreign\ndescription: x\nmetadata:\n  gatana-id: skill_9\n  gatana-org: other"),
    );
    let refused = push_skills(&api, &identity(), std::slice::from_ref(&file), &push_defaults()).await.unwrap();
    assert_eq!(refused[0].action, PushAction::Error);
    assert!(refused[0].detail.contains("organization other"));
    let created =
        push_skills(&api, &identity(), std::slice::from_ref(&file), &PushOptions { force: true, ..push_defaults() })
            .await
            .unwrap();
    assert_eq!(created[0].action, PushAction::Created);
}

#[tokio::test]
async fn dry_run_reports_without_writing() {
    let api = FakeSkillsApi::new();
    let dir = tempfile::tempdir().unwrap();
    let file = write_skill(dir.path(), "fresh", "A\n", None);
    let result =
        push_skills(&api, &identity(), std::slice::from_ref(&file), &PushOptions { dry_run: true, ..push_defaults() })
            .await
            .unwrap();
    assert_eq!(result[0].action, PushAction::Created);
    assert!(api.list(None, None).await.unwrap().is_empty());
    assert_eq!(stamped(&file).meta("gatana-id"), None);
}

#[tokio::test]
async fn collection_places_a_new_skill_a_synced_file_keeps_its_collection_and_the_option_moves_it() {
    let api = FakeSkillsApi::new();
    let release = api.seed_collection("release");
    let other = api.seed_collection("other");
    let dir = tempfile::tempdir().unwrap();
    let file = write_skill(dir.path(), "fresh", "Do the thing.\n", None);
    let into = |name: &str| PushOptions { collection: Some(name.to_string()), ..push_defaults() };

    let created = push_skills(&api, &identity(), std::slice::from_ref(&file), &into("release")).await.unwrap();
    assert_eq!(created[0].action, PushAction::Created);
    assert_eq!(api.find("fresh").unwrap().collection_id, Some(release.id.clone()));
    assert_eq!(stamped(&file).meta("gatana-collection"), Some("release"));

    // Pushing the stamped file again without the option leaves it in its collection.
    let again = push_skills(&api, &identity(), std::slice::from_ref(&file), &push_defaults()).await.unwrap();
    assert_eq!(again[0].action, PushAction::Unchanged);

    // The option moves it.
    let moved = push_skills(&api, &identity(), std::slice::from_ref(&file), &into("other")).await.unwrap();
    assert_eq!(moved[0].action, PushAction::Updated);
    assert_eq!(api.find("fresh").unwrap().collection_id, Some(other.id.clone()));
    assert_eq!(stamped(&file).meta("gatana-collection"), Some("other"));

    let missing = push_skills(&api, &identity(), std::slice::from_ref(&file), &into("missing")).await.unwrap_err();
    assert!(missing.to_string().contains("No collection named \"missing\""));
}

#[tokio::test]
async fn the_default_targets_are_pushed_together_and_missing_folders_and_aliases_are_handled() {
    let api = FakeSkillsApi::new();
    let claude = tempfile::tempdir().unwrap();
    let agents = tempfile::tempdir().unwrap();
    let missing = claude.path().join("never-created");
    write_skill(claude.path(), "alpha", "A\n", None);
    write_skill(agents.path(), "beta", "B\n", None);
    let skip_empty = PushOptions { skip_empty: true, ..push_defaults() };
    let first = push_skills(
        &api,
        &identity(),
        &[claude.path().to_path_buf(), agents.path().to_path_buf(), missing.clone()],
        &skip_empty,
    )
    .await
    .unwrap();
    assert_eq!(brief(&first), vec!["alpha:created", "beta:created"]);

    // The same folder under two paths is one folder.
    let twice = push_skills(&api, &identity(), &[claude.path().to_path_buf(), claude.path().join(".")], &skip_empty)
        .await
        .unwrap();
    assert_eq!(brief(&twice), vec!["alpha:unchanged"]);

    // Without skip_empty an empty path is still refused, as a typed path should be.
    assert!(push_skills(&api, &identity(), &[missing], &push_defaults()).await.is_err());
}
