mod common;

use common::{Change, FakeSkillsApi, OLD_GUIDE, cli_5_2_folder};
use gatana_cli::skills::api::SkillsApi;
use gatana_cli::skills::frontmatter::parse_skill_md;
use gatana_cli::skills::manifest::read_manifest;
use gatana_cli::skills::push::{PushAction, PushOptions, PushResult, push_skills};
use gatana_cli::skills::sync::{SkillsIdentity, SyncOptions, sync_directory};
use gatana_cli::util::iso_millis;
use std::collections::BTreeMap;
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
async fn a_new_hand_written_skill_is_stored_byte_for_byte_and_pushing_again_is_unchanged() {
    let api = FakeSkillsApi::new();
    let dir = tempfile::tempdir().unwrap();
    let file = write_skill(
        dir.path(),
        "fresh",
        "Do the thing.\n",
        Some("# kept\nname:   fresh\ndescription: x\nlicense: MIT"),
    );
    let text = std::fs::read_to_string(&file).unwrap();

    let created = push_skills(&api, &identity(), std::slice::from_ref(&file), &push_defaults()).await.unwrap();
    assert_eq!(created[0].action, PushAction::Created);
    // The push no longer writes into the file, and the server holds the same bytes.
    assert_eq!(std::fs::read_to_string(&file).unwrap(), text);
    let id = api.find("fresh").unwrap().id;
    assert_eq!(api.markdown_of(&id), Some(text));

    api.clear_calls();
    let again = push_skills(&api, &identity(), std::slice::from_ref(&file), &push_defaults()).await.unwrap();
    assert_eq!(again[0].action, PushAction::Unchanged);
    assert!(!api.calls().iter().any(|call| call.starts_with("update") || call.starts_with("replaceFiles")));

    // Outside a synced directory nothing records which version the folder has, so an edit needs --force.
    std::fs::write(&file, std::fs::read_to_string(&file).unwrap().replace("the thing", "it")).unwrap();
    let edited = push_skills(&api, &identity(), std::slice::from_ref(&file), &push_defaults()).await.unwrap();
    assert_eq!(edited[0].action, PushAction::Conflict);
    assert!(edited[0].detail.contains("this machine has no record of a push of this folder"));
}

#[tokio::test]
async fn a_file_stamped_by_an_older_cli_is_still_sent_as_fields_and_its_other_files_go_through_the_file_route() {
    let api = FakeSkillsApi::new();
    let a = api.seed("alpha", "v1\n");
    let dir = tempfile::tempdir().unwrap();
    let front = format!(
        "name: alpha\ndescription: \"Use for alpha\"\nmetadata:\n  gatana-id: \"{}\"\n  gatana-org: \"acme\"\n  gatana-updated-at: \"{}\"",
        a.id,
        iso_millis(&a.updated_at).unwrap()
    );
    let file = write_skill(dir.path(), "alpha", "v1\n", Some(&front));

    // The rendered file differs from the stored document in its bytes, and is still unchanged.
    let same = push_skills(&api, &identity(), std::slice::from_ref(&file), &push_defaults()).await.unwrap();
    assert_eq!(same[0].action, PushAction::Unchanged);

    std::fs::write(&file, std::fs::read_to_string(&file).unwrap().replace("v1", "v2")).unwrap();
    std::fs::write(dir.path().join("alpha/notes.md"), "notes\n").unwrap();
    api.clear_calls();
    let updated = push_skills(&api, &identity(), std::slice::from_ref(&file), &push_defaults()).await.unwrap();
    assert_eq!(updated[0].action, PushAction::Updated);
    assert_eq!(api.calls().iter().filter(|call| call.starts_with("update") || call.starts_with("replace")).count(), 2);
    // The stamps did not reach the stored document.
    assert!(!api.markdown_of(&a.id).unwrap().contains("gatana-id"));
    assert_eq!(api.content_of(&a.id).as_deref(), Some("v2\n"));
    assert_eq!(api.files_of(&a.id)["notes.md"], b"notes\n");
    // The stamp is the saved version of such a file, so the next push has one to compare.
    let current = api.get(&a.id).await.unwrap();
    assert_eq!(stamped(&file).meta("gatana-updated-at").map(str::to_string), iso_millis(&current.skill.updated_at));
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
    assert!(conflict[0].detail.contains("this machine has no record of a push of this folder"));
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

    // Pushing the file again without the option leaves it in its collection.
    let again = push_skills(&api, &identity(), std::slice::from_ref(&file), &push_defaults()).await.unwrap();
    assert_eq!(again[0].action, PushAction::Unchanged);

    // The option moves it.
    let moved = push_skills(&api, &identity(), std::slice::from_ref(&file), &into("other")).await.unwrap();
    assert_eq!(moved[0].action, PushAction::Updated);
    assert_eq!(api.find("fresh").unwrap().collection_id, Some(other.id.clone()));
    // A move alone keeps the stored document.
    assert_eq!(api.markdown_of(&api.find("fresh").unwrap().id), Some(std::fs::read_to_string(&file).unwrap()));

    let missing = push_skills(&api, &identity(), std::slice::from_ref(&file), &into("missing")).await.unwrap_err();
    assert!(missing.to_string().contains("No accessible collection named \"missing\""));
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

/// Every file below a directory, by its path with `/`.
fn tree(dir: &Path) -> BTreeMap<String, Vec<u8>> {
    walkdir::WalkDir::new(dir)
        .into_iter()
        .map(Result::unwrap)
        .filter(|entry| entry.file_type().is_file())
        .map(|entry| {
            let path = entry.path().strip_prefix(dir).unwrap().to_str().unwrap().replace('\\', "/");
            (path, std::fs::read(entry.path()).unwrap())
        })
        .collect()
}

/// A skill folder with a subfolder, a binary file and a text file with a BOM and CRLF.
fn write_folder_skill(dir: &Path, name: &str) -> PathBuf {
    let file = write_skill(
        dir,
        name,
        "See references/guide.md.\n",
        Some(&format!("# a comment\nname: {name}\ndescription: >\n  Use for folders\nlicense: MIT")),
    );
    let folder = dir.join(name);
    std::fs::create_dir_all(folder.join("references/deep")).unwrap();
    std::fs::create_dir_all(folder.join("assets")).unwrap();
    std::fs::write(folder.join("references/guide.md"), "# Guide\n").unwrap();
    std::fs::write(folder.join("references/deep/win.txt"), "\u{feff}one\r\ntwo\r\n").unwrap();
    std::fs::write(folder.join("assets/all-bytes.bin"), (0..=255).collect::<Vec<u8>>()).unwrap();
    std::fs::write(folder.join("empty"), "").unwrap();
    file
}

#[tokio::test]
async fn a_folder_with_a_subfolder_and_a_binary_file_makes_a_round_trip_byte_for_byte() {
    let api = FakeSkillsApi::new();
    let source = tempfile::tempdir().unwrap();
    let target = tempfile::tempdir().unwrap();
    write_folder_skill(source.path(), "folder-skill");
    // What a push leaves alone: the Finder's file and a version control folder.
    std::fs::write(source.path().join("folder-skill/.DS_Store"), "x").unwrap();
    std::fs::create_dir(source.path().join("folder-skill/.git")).unwrap();
    std::fs::write(source.path().join("folder-skill/.git/HEAD"), "ref").unwrap();

    let pushed = push_skills(&api, &identity(), &[source.path().join("folder-skill")], &push_defaults()).await.unwrap();
    assert_eq!(brief(&pushed), vec!["folder-skill:created"]);
    assert_eq!(pushed[0].detail, "");
    let id = api.find("folder-skill").unwrap().id;
    assert_eq!(
        api.files_of(&id).keys().collect::<Vec<_>>(),
        ["assets/all-bytes.bin", "empty", "references/deep/win.txt", "references/guide.md"]
    );

    let summary = sync_directory(&api, &identity(), target.path(), &sync_defaults()).await.unwrap();
    assert_eq!((summary.written, summary.warnings.len()), (1, 0));
    let mut expected = tree(&source.path().join("folder-skill"));
    expected.retain(|path, _| path != ".DS_Store" && !path.starts_with(".git/"));
    assert_eq!(tree(&target.path().join("folder-skill")), expected);
    assert_eq!(expected.len(), 5);

    // The copy pushes back as unchanged, and a changed and a deleted file travel the other way.
    let copy = target.path().join("folder-skill");
    let unchanged = push_skills(&api, &identity(), std::slice::from_ref(&copy), &push_defaults()).await.unwrap();
    assert_eq!(brief(&unchanged), vec!["folder-skill:unchanged"]);
    std::fs::write(copy.join("references/guide.md"), "# Guide, edited\n").unwrap();
    std::fs::remove_file(copy.join("assets/all-bytes.bin")).unwrap();
    std::fs::write(copy.join("new.txt"), "new\n").unwrap();
    let updated = push_skills(&api, &identity(), std::slice::from_ref(&copy), &push_defaults()).await.unwrap();
    assert_eq!(brief(&updated), vec!["folder-skill:updated"]);
    assert_eq!(
        api.files_of(&id).keys().collect::<Vec<_>>(),
        ["empty", "new.txt", "references/deep/win.txt", "references/guide.md"]
    );
    assert_eq!(api.files_of(&id)["references/guide.md"], b"# Guide, edited\n");

    // The push recorded the folder in the manifest, so the next sync has nothing to do.
    api.clear_calls();
    let clean = sync_directory(&api, &identity(), target.path(), &sync_defaults()).await.unwrap();
    assert_eq!((clean.written, clean.warnings.len()), (0, 0));
    assert_eq!(api.calls(), vec!["list", "listServerSkills"]);
}

#[tokio::test]
async fn a_changed_supporting_file_is_a_conflict_when_the_server_copy_is_newer_unless_forced() {
    let api = FakeSkillsApi::new();
    let source = tempfile::tempdir().unwrap();
    let dir = tempfile::tempdir().unwrap();
    write_folder_skill(source.path(), "folder-skill");
    push_skills(&api, &identity(), &[source.path().to_path_buf()], &push_defaults()).await.unwrap();
    sync_directory(&api, &identity(), dir.path(), &sync_defaults()).await.unwrap();
    let id = api.find("folder-skill").unwrap().id;

    std::fs::write(dir.path().join("folder-skill/references/guide.md"), "mine\n").unwrap();
    api.put_files(&id, &[("references/guide.md", b"theirs\n")]);
    let conflict = push_skills(&api, &identity(), &[dir.path().to_path_buf()], &push_defaults()).await.unwrap();
    assert_eq!(conflict[0].action, PushAction::Conflict);
    assert_eq!(api.files_of(&id)["references/guide.md"], b"theirs\n");

    let forced =
        push_skills(&api, &identity(), &[dir.path().to_path_buf()], &PushOptions { force: true, ..push_defaults() })
            .await
            .unwrap();
    assert_eq!(forced[0].action, PushAction::Updated);
    assert_eq!(api.files_of(&id)["references/guide.md"], b"mine\n");
    assert_eq!(api.files_of(&id).len(), 4);
}

#[cfg(unix)]
#[tokio::test]
async fn symlinks_in_a_pushed_folder_and_symlinked_skill_folders_are_skipped_and_reported() {
    let api = FakeSkillsApi::new();
    let dir = tempfile::tempdir().unwrap();
    let outside = tempfile::tempdir().unwrap();
    std::fs::write(outside.path().join("secret.txt"), "secret").unwrap();
    write_skill(dir.path(), "real", "A\n", None);
    std::fs::write(dir.path().join("real/kept.txt"), "kept").unwrap();
    std::os::unix::fs::symlink(outside.path().join("secret.txt"), dir.path().join("real/link.txt")).unwrap();
    std::os::unix::fs::symlink(outside.path(), dir.path().join("real/linked-dir")).unwrap();
    // A whole skill folder that is a symlink.
    write_skill(outside.path(), "elsewhere", "B\n", None);
    std::os::unix::fs::symlink(outside.path().join("elsewhere"), dir.path().join("elsewhere")).unwrap();

    let results = push_skills(&api, &identity(), &[dir.path().to_path_buf()], &push_defaults()).await.unwrap();
    assert_eq!(brief(&results), vec!["elsewhere:skipped", "real:created"]);
    assert!(results[0].detail.contains("symlink"));
    assert!(results[1].detail.contains("symlink link.txt not pushed"));
    assert!(results[1].detail.contains("symlink linked-dir not pushed"));
    assert_eq!(api.files_of(&api.find("real").unwrap().id).keys().collect::<Vec<_>>(), ["kept.txt"]);
    assert!(api.find("elsewhere").is_none());
}

#[tokio::test]
async fn a_folder_over_the_limits_or_with_a_file_that_a_sync_cannot_write_is_refused_before_any_request() {
    let api = FakeSkillsApi::new();
    let dir = tempfile::tempdir().unwrap();
    write_skill(dir.path(), "many", "A\n", None);
    for index in 0..512 {
        std::fs::write(dir.path().join(format!("many/{index}.txt")), "x").unwrap();
    }
    write_skill(dir.path(), "large", "A\n", None);
    std::fs::write(dir.path().join("large/big.bin"), vec![0u8; 4 * 1024 * 1024]).unwrap();
    write_skill(dir.path(), "reserved", "A\n", None);
    std::fs::write(dir.path().join("reserved/aux.txt"), "x").unwrap();
    std::fs::write(dir.path().join("reserved/fine.txt"), "x").unwrap();
    write_skill(dir.path(), "nested", "A\n", None);
    std::fs::create_dir(dir.path().join("nested/sub")).unwrap();
    std::fs::write(dir.path().join("nested/sub/SKILL.md"), "x").unwrap();
    write_skill(dir.path(), "good", "A\n", None);

    let results = push_skills(&api, &identity(), &[dir.path().to_path_buf()], &push_defaults()).await.unwrap();
    assert_eq!(brief(&results), vec!["good:created", "large:error", "many:error", "nested:error", "reserved:error"]);
    assert!(results[1].detail.contains("2 files and 41943") && results[1].detail.contains("4194304 bytes"));
    assert!(results[2].detail.contains("513 files") && results[2].detail.contains("at most 512 files"));
    // The backend refuses a second SKILL.md, so the push does too.
    assert!(results[3].detail.contains("\"sub/SKILL.md\": it is a SKILL.md in a subfolder"));
    assert!(results[4].detail.contains("\"aux.txt\": Windows reserves the name"));
    let created: Vec<String> = api.calls().into_iter().filter(|call| call.starts_with("create")).collect();
    assert_eq!(created, ["create good"]);
}

#[tokio::test]
async fn a_rename_in_a_synced_folder_renames_the_skill_and_the_next_sync_moves_the_folder() {
    let api = FakeSkillsApi::new();
    let a = api.seed("alpha", "A\n");
    let dir = tempfile::tempdir().unwrap();
    sync_directory(&api, &identity(), dir.path(), &sync_defaults()).await.unwrap();
    let file = dir.path().join("alpha/SKILL.md");
    std::fs::write(&file, std::fs::read_to_string(&file).unwrap().replace("name: alpha", "name: beta")).unwrap();

    let renamed = push_skills(&api, &identity(), &[dir.path().to_path_buf()], &push_defaults()).await.unwrap();
    assert_eq!(brief(&renamed), vec!["beta:updated"]);
    assert_eq!(api.find("beta").unwrap().id, a.id);
    let summary = sync_directory(&api, &identity(), dir.path(), &sync_defaults()).await.unwrap();
    assert!(summary.warnings.is_empty());
    assert!(!dir.path().join("alpha").exists());
    assert!(dir.path().join("beta/SKILL.md").exists());
}

#[tokio::test]
async fn a_backend_without_file_routes_still_takes_the_skill_md_and_the_push_says_what_it_left_out() {
    let api = FakeSkillsApi::new();
    api.file_routes.set(false);
    let dir = tempfile::tempdir().unwrap();
    let synced = tempfile::tempdir().unwrap();
    let file = write_folder_skill(dir.path(), "folder-skill");

    let created = push_skills(&api, &identity(), std::slice::from_ref(&file), &push_defaults()).await.unwrap();
    assert_eq!(created[0].action, PushAction::Created);
    assert!(created[0].detail.contains("the server stores only the SKILL.md: 4 other files not pushed"));
    let id = api.find("folder-skill").unwrap().id;
    assert!(api.files_of(&id).is_empty());

    // The sync writes the one document, and an edit of it goes back as name, description and body.
    api.clear_calls();
    let first = sync_directory(&api, &identity(), synced.path(), &sync_defaults()).await.unwrap();
    assert_eq!((first.written, first.warnings.len()), (1, 0));
    assert_eq!(
        api.calls(),
        vec!["list".to_string(), "listServerSkills".to_string(), format!("listFiles {id}"), format!("get {id}")]
    );
    assert_eq!(tree(synced.path()).keys().collect::<Vec<_>>(), [".gatana-skills.json", "folder-skill/SKILL.md"]);
    api.clear_calls();
    sync_directory(&api, &identity(), synced.path(), &sync_defaults()).await.unwrap();
    assert_eq!(api.calls(), vec!["list", "listServerSkills"]);

    let copy = synced.path().join("folder-skill/SKILL.md");
    std::fs::write(&copy, std::fs::read_to_string(&copy).unwrap().replace("See references", "Read references"))
        .unwrap();
    api.clear_calls();
    let updated = push_skills(&api, &identity(), std::slice::from_ref(&copy), &push_defaults()).await.unwrap();
    assert_eq!(updated[0].action, PushAction::Updated);
    assert_eq!(api.calls(), vec![format!("get {id}"), format!("listFiles {id}"), format!("update {id}")]);
    assert_eq!(api.content_of(&id).as_deref(), Some("Read references/guide.md.\n"));
    api.clear_calls();
    let clean = sync_directory(&api, &identity(), synced.path(), &sync_defaults()).await.unwrap();
    assert_eq!((clean.written, clean.warnings.len()), (0, 0));
    assert_eq!(api.calls(), vec!["list", "listServerSkills"]);
}

#[tokio::test]
async fn a_file_of_another_name_is_pushed_alone_and_keeps_the_files_of_the_skill() {
    let api = FakeSkillsApi::new();
    let a = api.seed("alpha", "v1\n");
    api.put_files(&a.id, &[("docs/guide.md", b"guide\n")]);
    let dir = tempfile::tempdir().unwrap();
    let file = dir.path().join("draft.md");
    std::fs::write(&file, "---\nname: alpha\ndescription: Use for alpha\n---\n\nv2\n").unwrap();
    std::fs::write(dir.path().join("unrelated.txt"), "not a part of the skill").unwrap();

    let forced = PushOptions { force: true, ..push_defaults() };
    let updated = push_skills(&api, &identity(), std::slice::from_ref(&file), &forced).await.unwrap();
    assert_eq!(updated[0].action, PushAction::Updated);
    assert_eq!(api.content_of(&a.id).as_deref(), Some("v2\n"));
    assert_eq!(api.files_of(&a.id).keys().collect::<Vec<_>>(), ["docs/guide.md"]);
}

#[tokio::test]
async fn a_push_takes_the_new_updated_at_from_the_answer_of_the_file_route_and_sends_no_read_after_it() {
    let api = FakeSkillsApi::new();
    let source = tempfile::tempdir().unwrap();
    let target = tempfile::tempdir().unwrap();
    let file = write_folder_skill(source.path(), "folder-skill");

    // A new folder: the skill, then its files. No read follows the write of the files.
    push_skills(&api, &identity(), std::slice::from_ref(&file), &push_defaults()).await.unwrap();
    let id = api.find("folder-skill").unwrap().id;
    assert_eq!(api.calls(), vec!["list".to_string(), "create folder-skill".to_string(), format!("replaceFiles {id}")]);

    // A changed folder: the last request is the write, and the manifest holds the time that it set.
    sync_directory(&api, &identity(), target.path(), &sync_defaults()).await.unwrap();
    let copy = target.path().join("folder-skill");
    std::fs::write(copy.join("references/guide.md"), "# Guide, edited\n").unwrap();
    api.clear_calls();
    let updated = push_skills(&api, &identity(), std::slice::from_ref(&copy), &push_defaults()).await.unwrap();
    assert_eq!(brief(&updated), vec!["folder-skill:updated"]);
    assert_eq!(api.calls(), vec![format!("get {id}"), format!("listFiles {id}"), format!("replaceFiles {id}")]);
    let manifest = read_manifest(target.path()).unwrap().unwrap();
    assert_eq!(
        Some(manifest.skills[&id].updated_at.clone()),
        iso_millis(&api.find("folder-skill").unwrap().updated_at)
    );
}

#[tokio::test]
async fn the_folder_of_a_server_skill_is_not_pushed() {
    let api = FakeSkillsApi::new();
    api.seed("alpha", "A\n");
    let doc = "---\nname: review\ndescription: Use for review\n---\n\n# Review\n";
    api.serve("github", "review", &[("SKILL.md", doc.as_bytes())]);
    // The folder is not read, so a server skill over the limits of a push is skipped too.
    let big = "---\nname: big\ndescription: Use for big\n---\n\n# Big\n";
    api.serve("github", "big", &[("SKILL.md", big.as_bytes()), ("data.bin", &vec![0u8; 4 * 1024 * 1024])]);
    let dir = tempfile::tempdir().unwrap();
    sync_directory(&api, &identity(), dir.path(), &sync_defaults()).await.unwrap();
    assert!(dir.path().join("review/SKILL.md").exists() && dir.path().join("big/data.bin").exists());

    // A push of the whole directory, as the default paths give it, creates no organization skill
    // from the server skill.
    api.clear_calls();
    let results = push_skills(&api, &identity(), &[dir.path().to_path_buf()], &push_defaults()).await.unwrap();
    assert_eq!(brief(&results), vec!["alpha:unchanged", "big:skipped", "review:skipped"]);
    assert!(results[2].detail.contains("skill of the MCP server \"github\""));
    assert!(api.find("review").is_none());
    assert!(!api.calls().iter().any(|call| call.starts_with("create")));
}

#[tokio::test]
async fn a_folder_synced_from_another_organization_is_refused_without_force_and_its_server_skills_never_go() {
    let acme = FakeSkillsApi::new();
    acme.seed("alpha", "A\n");
    let doc = "---\nname: review\ndescription: Use for review\n---\n\n# Review\n";
    acme.serve("github", "review", &[("SKILL.md", doc.as_bytes())]);
    let dir = tempfile::tempdir().unwrap();
    sync_directory(&acme, &identity(), dir.path(), &sync_defaults()).await.unwrap();
    let before = read_manifest(dir.path()).unwrap();

    // Another organization, and the same organization ID on another host.
    let other = FakeSkillsApi::new();
    let elsewhere = SkillsIdentity { org_id: "other".into(), base_url: "https://other.example".into() };
    let staging = SkillsIdentity { base_url: "https://acme.staging.example".into(), ..identity() };
    for target in [&elsewhere, &staging] {
        let refused = push_skills(&other, target, &[dir.path().to_path_buf()], &push_defaults()).await.unwrap();
        assert_eq!(brief(&refused), ["alpha:error", "review:skipped"]);
        assert!(refused[0].detail.contains("synced from organization acme (https://acme.example)"));
    }
    assert!(other.calls().is_empty());

    // --force creates a copy of the organization skill, never of the server skill, and the
    // manifest of acme stays as it was.
    let force = PushOptions { force: true, ..push_defaults() };
    let forced = push_skills(&other, &elsewhere, &[dir.path().to_path_buf()], &force).await.unwrap();
    assert_eq!(brief(&forced), ["alpha:created", "review:skipped"]);
    assert!(other.find("review").is_none());
    assert_eq!(read_manifest(dir.path()).unwrap(), before);
}

#[tokio::test]
async fn a_push_keeps_a_server_file_that_the_folder_never_got_and_deletes_one_that_the_user_removed() {
    let api = FakeSkillsApi::new();
    let dir = tempfile::tempdir().unwrap();
    let id = cli_5_2_folder(&api, dir.path(), "# Old\n");
    std::fs::write(dir.path().join("beta/notes.md"), "notes\n").unwrap();

    // Before the first sync after the upgrade from CLI 5.2, the folder lacks a file of the server.
    // A dry run reports the refusal too.
    for options in [push_defaults(), PushOptions { dry_run: true, ..push_defaults() }] {
        let refused = push_skills(&api, &identity(), &[dir.path().to_path_buf()], &options).await.unwrap();
        assert_eq!(refused[0].action, PushAction::Error);
        assert!(
            refused[0]
                .detail
                .contains(&format!("the server holds the file \"{OLD_GUIDE}\", which this folder never got"))
        );
    }
    assert_eq!(api.files_of(&id).keys().collect::<Vec<_>>(), [OLD_GUIDE]);

    // The sync gets the file. The push then sends the new file and keeps the other.
    sync_directory(&api, &identity(), dir.path(), &sync_defaults()).await.unwrap();
    let pushed = push_skills(&api, &identity(), &[dir.path().to_path_buf()], &push_defaults()).await.unwrap();
    assert_eq!(pushed[0].action, PushAction::Updated);
    assert_eq!(api.files_of(&id).keys().collect::<Vec<_>>(), ["notes.md", OLD_GUIDE]);

    // A file that the folder had and that the user removed is removed on the server.
    std::fs::remove_file(dir.path().join("beta").join(OLD_GUIDE)).unwrap();
    let removed = push_skills(&api, &identity(), &[dir.path().to_path_buf()], &push_defaults()).await.unwrap();
    assert_eq!(removed[0].action, PushAction::Updated);
    assert_eq!(api.files_of(&id).keys().collect::<Vec<_>>(), ["notes.md"]);
}

#[tokio::test]
async fn a_file_whose_name_starts_with_a_dot_goes_only_when_the_skill_on_the_server_has_it() {
    let api = FakeSkillsApi::new();
    let dir = tempfile::tempdir().unwrap();
    // A new skill at the root of a repository: none of its dotfiles goes, and `.git` gets no note.
    write_skill(dir.path(), "tool", "A\n", None);
    let folder = dir.path().join("tool");
    std::fs::write(folder.join(".env"), "API_KEY=secret\n").unwrap();
    std::fs::create_dir_all(folder.join(".git")).unwrap();
    std::fs::write(folder.join(".git/config"), "x").unwrap();
    std::fs::create_dir_all(folder.join("docs/.cache")).unwrap();
    std::fs::write(folder.join("docs/.cache/state.json"), "{}").unwrap();
    std::fs::write(folder.join("docs/guide.md"), "# Guide\n").unwrap();
    let created = push_skills(&api, &identity(), std::slice::from_ref(&folder), &push_defaults()).await.unwrap();
    assert_eq!(created[0].action, PushAction::Created);
    assert!(created[0].detail.starts_with(".env, docs/.cache not pushed"));
    let id = api.find("tool").unwrap().id;
    assert_eq!(api.files_of(&id).keys().collect::<Vec<_>>(), ["docs/guide.md"]);

    // A dotfile that the skill has on the server comes with a sync and goes back with a push.
    api.put_files(&id, &[("docs/guide.md", b"# Guide\n"), (".gitignore", b".env\n")]);
    let synced = tempfile::tempdir().unwrap();
    sync_directory(&api, &identity(), synced.path(), &sync_defaults()).await.unwrap();
    let copy = synced.path().join("tool");
    std::fs::write(copy.join(".gitignore"), ".env\n*.log\n").unwrap();
    std::fs::write(copy.join(".env"), "API_KEY=secret\n").unwrap();
    let pushed = push_skills(&api, &identity(), &[copy], &push_defaults()).await.unwrap();
    assert_eq!(pushed[0].action, PushAction::Updated);
    assert!(pushed[0].detail.starts_with(".env not pushed"));
    assert_eq!(api.files_of(&id).keys().collect::<Vec<_>>(), [".gitignore", "docs/guide.md"]);
    assert_eq!(api.files_of(&id)[".gitignore"], b".env\n*.log\n");
}

#[tokio::test]
async fn a_push_that_stops_after_the_server_saved_the_skill_records_it_so_the_next_push_needs_no_force() {
    let api = FakeSkillsApi::new();
    let home = tempfile::tempdir().unwrap();
    let options = remembering(home.path());
    let dir = tempfile::tempdir().unwrap();
    let file = write_folder_skill(dir.path(), "partial");
    let refuse = |message: Option<&str>| *api.refuse_files.borrow_mut() = message.map(str::to_string);

    // The skill is created, and the server refuses its other files.
    refuse(Some("The skill is too large"));
    let first = push_skills(&api, &identity(), std::slice::from_ref(&file), &options).await.unwrap();
    assert_eq!(first[0].action, PushAction::Error);
    assert_eq!(first[0].detail, "created, but the server refused its other files: The skill is too large");
    let id = api.find("partial").unwrap().id;
    assert!(api.files_of(&id).is_empty());
    let key = std::fs::canonicalize(dir.path().join("partial")).unwrap().to_str().unwrap().to_string();
    assert_eq!(push_record(home.path())["folders"]["acme"][&key]["skillId"], id);
    refuse(None);
    let second = push_skills(&api, &identity(), std::slice::from_ref(&file), &options).await.unwrap();
    assert_eq!(second[0].action, PushAction::Updated);
    assert_eq!(api.files_of(&id).len(), 4);

    // A SKILL.md with the stamps of CLI 5.2 goes as fields before the files. The stamp gets the
    // version that the server saved, also when it then refuses the files.
    let alpha = api.seed("alpha", "v1\n");
    let front = format!(
        "name: alpha\ndescription: \"Use for alpha\"\nmetadata:\n  gatana-id: \"{}\"\n  gatana-org: \"acme\"\n  gatana-updated-at: \"{}\"",
        alpha.id,
        iso_millis(&alpha.updated_at).unwrap()
    );
    let stamped_file = write_skill(dir.path(), "alpha", "v2\n", Some(&front));
    std::fs::write(dir.path().join("alpha/notes.md"), "notes\n").unwrap();
    refuse(Some("The skill is too large"));
    let partly = push_skills(&api, &identity(), std::slice::from_ref(&stamped_file), &options).await.unwrap();
    assert_eq!(partly[0].action, PushAction::Error);
    assert!(partly[0].detail.starts_with("updated in part, because the server refused the next request"));
    assert_eq!(api.content_of(&alpha.id).as_deref(), Some("v2\n"));
    refuse(None);
    let rest = push_skills(&api, &identity(), std::slice::from_ref(&stamped_file), &options).await.unwrap();
    assert_eq!(rest[0].action, PushAction::Updated);
    assert_eq!(api.files_of(&alpha.id)["notes.md"], b"notes\n");
}

/// Options with a push record in a scratch directory, never in the home directory.
fn remembering(home: &Path) -> PushOptions {
    PushOptions { memory_file: Some(home.join(".gatana.skill-pushes.json")), ..push_defaults() }
}

fn push_record(home: &Path) -> serde_json::Value {
    serde_json::from_str(&std::fs::read_to_string(home.join(".gatana.skill-pushes.json")).unwrap()).unwrap()
}

#[tokio::test]
async fn a_folder_outside_a_synced_directory_is_remembered_so_a_second_push_needs_no_force() {
    let api = FakeSkillsApi::new();
    let home = tempfile::tempdir().unwrap();
    let dir = tempfile::tempdir().unwrap();
    let file = write_folder_skill(dir.path(), "folder-skill");
    let options = remembering(home.path());
    let folder = std::fs::canonicalize(dir.path().join("folder-skill")).unwrap();
    let edit = |text: &str| std::fs::write(dir.path().join("folder-skill/references/guide.md"), text).unwrap();

    // The first push creates the skill and records it: the ID and the time, by organization and folder.
    let created = push_skills(&api, &identity(), std::slice::from_ref(&file), &options).await.unwrap();
    assert_eq!(created[0].action, PushAction::Created);
    let id = api.find("folder-skill").unwrap().id;
    let updated_at = |api: &FakeSkillsApi| iso_millis(&api.find("folder-skill").unwrap().updated_at).unwrap();
    assert_eq!(
        push_record(home.path()),
        serde_json::json!({
            "version": 1,
            "folders": { "acme": { folder.to_str().unwrap(): { "skillId": id, "updatedAt": updated_at(&api) } } }
        })
    );
    // The folder holds no manifest and the SKILL.md no stamp.
    assert!(!dir.path().join(".gatana-skills.json").exists());

    // A changed folder goes up with no --force, and the record moves on.
    edit("# Guide, v2\n");
    let second = push_skills(&api, &identity(), std::slice::from_ref(&file), &options).await.unwrap();
    assert_eq!(second[0].action, PushAction::Updated);
    assert_eq!(push_record(home.path())["folders"]["acme"][folder.to_str().unwrap()]["updatedAt"], updated_at(&api));
    edit("# Guide, v3\n");
    let third = push_skills(&api, &identity(), std::slice::from_ref(&file), &options).await.unwrap();
    assert_eq!(third[0].action, PushAction::Updated);

    // Someone else changes the skill: the next push of a change is a conflict.
    api.change(&id, Change { description: Some("Changed elsewhere".into()), ..Change::default() }).unwrap();
    edit("# Guide, v4\n");
    let conflict = push_skills(&api, &identity(), std::slice::from_ref(&file), &options).await.unwrap();
    assert_eq!(conflict[0].action, PushAction::Conflict);
    assert!(conflict[0].detail.contains("changed on the server at"));

    // --force overwrites and records, so the push after it needs no --force.
    let forced =
        push_skills(&api, &identity(), std::slice::from_ref(&file), &PushOptions { force: true, ..options.clone() })
            .await
            .unwrap();
    assert_eq!(forced[0].action, PushAction::Updated);
    edit("# Guide, v5\n");
    let after = push_skills(&api, &identity(), std::slice::from_ref(&file), &options).await.unwrap();
    assert_eq!(after[0].action, PushAction::Updated);
    assert_eq!(api.files_of(&id)["references/guide.md"], b"# Guide, v5\n");
}

#[tokio::test]
async fn a_machine_with_no_record_and_a_record_of_another_skill_give_no_baseline() {
    let api = FakeSkillsApi::new();
    let home = tempfile::tempdir().unwrap();
    let dir = tempfile::tempdir().unwrap();
    let file = write_skill(dir.path(), "taken", "local\n", None);
    let options = remembering(home.path());

    // A new machine or a CI runner: the skill exists and nothing records a push of this folder.
    let first = api.seed("taken", "server\n");
    let conflict = push_skills(&api, &identity(), std::slice::from_ref(&file), &options).await.unwrap();
    assert_eq!(conflict[0].action, PushAction::Conflict);
    assert!(conflict[0].detail.contains("this machine has no record of a push of this folder"));
    assert!(!conflict[0].detail.contains("gatana skills install"));
    // A conflict and a dry run record nothing.
    assert!(!home.path().join(".gatana.skill-pushes.json").exists());
    let dry = PushOptions { force: true, dry_run: true, ..options.clone() };
    push_skills(&api, &identity(), std::slice::from_ref(&file), &dry).await.unwrap();
    assert!(!home.path().join(".gatana.skill-pushes.json").exists());

    // One --force, then the record holds this skill. An unchanged push records too.
    let force = PushOptions { force: true, ..options.clone() };
    push_skills(&api, &identity(), std::slice::from_ref(&file), &force).await.unwrap();
    let key = std::fs::canonicalize(dir.path().join("taken")).unwrap().to_str().unwrap().to_string();
    assert_eq!(push_record(home.path())["folders"]["acme"][&key]["skillId"], first.id);
    std::fs::remove_file(home.path().join(".gatana.skill-pushes.json")).unwrap();
    let unchanged = push_skills(&api, &identity(), std::slice::from_ref(&file), &options).await.unwrap();
    assert_eq!(unchanged[0].action, PushAction::Unchanged);
    assert_eq!(push_record(home.path())["folders"]["acme"][&key]["skillId"], first.id);

    // The skill is deleted and created again under the name: the record is of another skill, so
    // the folder has no baseline. The record does not choose the skill either: the name does.
    api.remove(&first.id);
    let second = api.seed("taken", "a new skill\n");
    std::fs::write(&file, std::fs::read_to_string(&file).unwrap().replace("local", "local, edited")).unwrap();
    let other = push_skills(&api, &identity(), std::slice::from_ref(&file), &options).await.unwrap();
    assert_eq!(other[0].action, PushAction::Conflict);
    assert!(other[0].detail.contains("no record of a push"));
    assert_eq!(api.content_of(&second.id).as_deref(), Some("a new skill\n"));
}

#[tokio::test]
async fn a_folder_in_a_synced_directory_keeps_the_manifest_as_its_only_record_and_gone_folders_are_dropped() {
    let api = FakeSkillsApi::new();
    let home = tempfile::tempdir().unwrap();
    let options = remembering(home.path());
    api.seed("alpha", "A\n");
    let synced = tempfile::tempdir().unwrap();
    sync_directory(&api, &identity(), synced.path(), &sync_defaults()).await.unwrap();
    let copy = synced.path().join("alpha/SKILL.md");
    std::fs::write(&copy, std::fs::read_to_string(&copy).unwrap().replace("A\n", "A2\n")).unwrap();
    let updated = push_skills(&api, &identity(), std::slice::from_ref(&copy), &options).await.unwrap();
    assert_eq!(updated[0].action, PushAction::Updated);
    assert!(!home.path().join(".gatana.skill-pushes.json").exists());

    // Two folders with no manifest are recorded. When one is gone, the next write drops its entry.
    let dir = tempfile::tempdir().unwrap();
    let one = write_skill(dir.path(), "one", "1\n", None);
    let two = write_skill(dir.path(), "two", "2\n", None);
    push_skills(&api, &identity(), &[one.clone(), two.clone()], &options).await.unwrap();
    assert_eq!(push_record(home.path())["folders"]["acme"].as_object().unwrap().len(), 2);
    std::fs::remove_dir_all(dir.path().join("one")).unwrap();
    push_skills(&api, &identity(), std::slice::from_ref(&two), &options).await.unwrap();
    let folders = push_record(home.path())["folders"]["acme"].as_object().unwrap().clone();
    assert_eq!(folders.len(), 1);
    assert!(folders.keys().next().unwrap().ends_with("/two"));
    // No temporary file stays next to the record.
    assert_eq!(std::fs::read_dir(home.path()).unwrap().count(), 1);
}
