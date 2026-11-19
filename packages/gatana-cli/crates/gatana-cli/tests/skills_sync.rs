mod common;

use common::{Change, FakeSkillsApi, OLD_GUIDE, ServerListing, cli_5_2_folder};
use gatana_cli::skills::frontmatter::parse_skill_md;
use gatana_cli::skills::manifest::{MANIFEST_FILE, Subscription, SubscriptionKind, read_manifest, sha256};
use gatana_cli::skills::push::{PushOptions, push_skills};
use gatana_cli::skills::subscriptions::resolve_subscription;
use gatana_cli::skills::sync::{SkillsIdentity, SyncOptions, sync_directory, sync_targets};
use gatana_cli::skills::targets::prepare_targets;
use gatana_cli::util::iso_millis;
use std::collections::BTreeSet;
use std::path::Path;

fn identity() -> SkillsIdentity {
    SkillsIdentity { org_id: "acme".into(), base_url: "https://acme.example".into() }
}

fn defaults() -> SyncOptions {
    SyncOptions { dry_run: false, prune: true, force: false, ..SyncOptions::default() }
}

fn read(path: &Path) -> String {
    std::fs::read_to_string(path).unwrap()
}

fn body_of(path: &Path) -> String {
    parse_skill_md(&read(path)).unwrap().1
}

fn subscription(kind: SubscriptionKind, id: &str, name: &str) -> Subscription {
    Subscription { kind, id: id.into(), name: name.into() }
}

#[tokio::test]
async fn first_sync_writes_every_skill_and_the_manifest_and_the_second_fetches_nothing() {
    let api = FakeSkillsApi::new();
    let a = api.seed("alpha", "# Alpha\n");
    api.seed("beta", "# Beta\n");
    let dir = tempfile::tempdir().unwrap();

    let first = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!(first.written, 2);
    assert_eq!(first.total, 2);
    // The file is the document of the server, with nothing added.
    assert_eq!(Some(read(&dir.path().join("alpha/SKILL.md"))), api.markdown_of(&a.id));
    assert_eq!(body_of(&dir.path().join("alpha/SKILL.md")), "# Alpha\n");
    let manifest = read_manifest(dir.path()).unwrap().unwrap();
    assert_eq!((manifest.version, manifest.org_id.as_str()), (3, "acme"));
    assert_eq!(manifest.skills[&a.id].name, "alpha");
    assert_eq!(manifest.skills[&a.id].files.keys().collect::<Vec<_>>(), ["SKILL.md"]);

    api.clear_calls();
    let second = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!(second.written, 0);
    assert_eq!(api.calls(), vec!["list", "listServerSkills"]);
}

#[tokio::test]
async fn remote_rename_moves_the_folder_remote_delete_prunes_it_and_no_prune_keeps_it() {
    let api = FakeSkillsApi::new();
    let a = api.seed("alpha", "A\n");
    let b = api.seed("beta", "B\n");
    let dir = tempfile::tempdir().unwrap();
    sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();

    api.change(&a.id, Change { name: Some("alpha-two".into()), ..Change::default() }).unwrap();
    sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert!(!dir.path().join("alpha").exists());
    assert!(dir.path().join("alpha-two/SKILL.md").exists());

    api.remove(&b.id);
    let kept =
        sync_directory(&api, &identity(), dir.path(), &SyncOptions { prune: false, ..defaults() }).await.unwrap();
    assert_eq!(kept.removed, 0);
    assert!(dir.path().join("beta/SKILL.md").exists());
    assert!(read_manifest(dir.path()).unwrap().unwrap().skills.contains_key(&b.id));

    let pruned = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!(pruned.removed, 1);
    assert!(!dir.path().join("beta").exists());
    assert!(!read_manifest(dir.path()).unwrap().unwrap().skills.contains_key(&b.id));
}

#[tokio::test]
async fn a_foreign_folder_is_left_alone_and_reported_and_force_adopts_it() {
    let api = FakeSkillsApi::new();
    api.seed("mine", "remote\n");
    let dir = tempfile::tempdir().unwrap();
    std::fs::create_dir(dir.path().join("mine")).unwrap();
    std::fs::write(dir.path().join("mine/SKILL.md"), "hand written\n").unwrap();

    let summary = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!(summary.written, 0);
    assert_eq!(read(&dir.path().join("mine/SKILL.md")), "hand written\n");
    assert!(summary.warnings[0].contains("not tracked by Gatana"));

    sync_directory(&api, &identity(), dir.path(), &SyncOptions { force: true, ..defaults() }).await.unwrap();
    assert_eq!(body_of(&dir.path().join("mine/SKILL.md")), "remote\n");
}

#[tokio::test]
async fn local_edits_are_kept_until_force_and_a_managed_folder_with_extra_files_is_kept_on_prune() {
    let api = FakeSkillsApi::new();
    let a = api.seed("alpha", "v1\n");
    let dir = tempfile::tempdir().unwrap();
    sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    std::fs::write(dir.path().join("alpha/SKILL.md"), "edited locally\n").unwrap();
    api.change(&a.id, Change { content: Some("v2\n".into()), ..Change::default() }).unwrap();

    let skipped = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!(skipped.written, 0);
    assert!(skipped.warnings[0].contains("local edits"));
    assert_eq!(read(&dir.path().join("alpha/SKILL.md")), "edited locally\n");

    sync_directory(&api, &identity(), dir.path(), &SyncOptions { force: true, ..defaults() }).await.unwrap();
    assert_eq!(body_of(&dir.path().join("alpha/SKILL.md")), "v2\n");

    std::fs::write(dir.path().join("alpha/notes.txt"), "keep me").unwrap();
    api.remove(&a.id);
    let pruned = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert!(!dir.path().join("alpha/SKILL.md").exists());
    assert!(dir.path().join("alpha/notes.txt").exists());
    assert!(pruned.warnings[0].contains("kept"));
}

#[tokio::test]
async fn a_directory_synced_from_another_organization_is_refused_without_force() {
    let api = FakeSkillsApi::new();
    api.seed("alpha", "A\n");
    let dir = tempfile::tempdir().unwrap();
    sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    let other = SkillsIdentity { org_id: "other".into(), base_url: "https://other.example".into() };
    let refused = sync_directory(&api, &other, dir.path(), &defaults()).await.unwrap_err();
    assert!(refused.to_string().contains("syncs skills from acme"));
    let switched = sync_directory(&api, &other, dir.path(), &SyncOptions { force: true, ..defaults() }).await.unwrap();
    assert_eq!(read_manifest(dir.path()).unwrap().unwrap().org_id, "other");
    assert!(switched.warnings.iter().any(|warning| warning.contains("switched")));
}

#[tokio::test]
async fn dry_run_touches_nothing() {
    let api = FakeSkillsApi::new();
    api.seed("alpha", "A\n");
    let dir = tempfile::tempdir().unwrap();
    let summary =
        sync_directory(&api, &identity(), dir.path(), &SyncOptions { dry_run: true, ..defaults() }).await.unwrap();
    assert_eq!(summary.written, 1);
    assert_eq!(std::fs::read_dir(dir.path()).unwrap().count(), 0);
}

#[tokio::test]
async fn a_skill_that_disappears_between_list_and_get_is_skipped_with_a_warning() {
    let api = FakeSkillsApi::new();
    let a = api.seed("alpha", "A\n");
    let dir = tempfile::tempdir().unwrap();
    *api.remove_after_list.borrow_mut() = Some(a.id.clone());
    let summary = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert!(summary.warnings[0].contains("disappeared"));
    assert!(!dir.path().join("alpha").exists());
}

#[cfg(unix)]
#[tokio::test]
async fn prepare_targets_creates_directories_and_collapses_symlinked_aliases() {
    let base = tempfile::tempdir().unwrap();
    let real = base.path().join("real");
    let alias = base.path().join("alias");
    std::fs::create_dir(&real).unwrap();
    std::os::unix::fs::symlink(&real, &alias).unwrap();
    let dirs = prepare_targets(&[alias, real, base.path().join("new")]).unwrap();
    assert_eq!(dirs.len(), 2);
    assert!(base.path().join("new").exists());
}

#[tokio::test]
async fn installing_a_name_follows_it_a_rename_is_followed_and_what_leaves_it_is_pruned() {
    let api = FakeSkillsApi::new();
    let release = api.seed_collection("release");
    let other = api.seed_collection("other");
    let in_release = api.seed_in("deploy", "D\n", Some(&release.id));
    api.seed_in("review", "R\n", Some(&other.id));
    api.seed("root-skill", "S\n");
    let dir = tempfile::tempdir().unwrap();
    let follow_release = subscription(SubscriptionKind::Collection, &release.id, "release");

    let first = sync_directory(
        &api,
        &identity(),
        dir.path(),
        &SyncOptions { subscribe: Some(follow_release.clone()), ..defaults() },
    )
    .await
    .unwrap();
    assert_eq!(first.written, 1);
    assert_eq!(first.subscriptions, Some(vec![follow_release.clone()]));
    assert!(dir.path().join("deploy/SKILL.md").exists());
    assert!(!dir.path().join("review").exists());
    assert!(!dir.path().join("root-skill").exists());

    // Installing the same name again keeps one manifest entry.
    sync_directory(
        &api,
        &identity(),
        dir.path(),
        &SyncOptions { subscribe: Some(follow_release.clone()), ..defaults() },
    )
    .await
    .unwrap();
    assert_eq!(read_manifest(dir.path()).unwrap().unwrap().subscriptions, Some(vec![follow_release.clone()]));

    // A dry run with a name previews without writing the subscription.
    let preview = sync_directory(
        &api,
        &identity(),
        dir.path(),
        &SyncOptions {
            dry_run: true,
            subscribe: Some(subscription(SubscriptionKind::Collection, &other.id, "other")),
            ..defaults()
        },
    )
    .await
    .unwrap();
    assert_eq!(preview.subscriptions.unwrap().len(), 2);
    assert_eq!(read_manifest(dir.path()).unwrap().unwrap().subscriptions, Some(vec![follow_release.clone()]));

    api.rename_collection(&release.id, "release-train");
    let renamed = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert!(renamed.warnings.iter().any(|warning| warning.contains("now named \"release-train\"")));
    assert_eq!(
        read_manifest(dir.path()).unwrap().unwrap().subscriptions,
        Some(vec![subscription(SubscriptionKind::Collection, &release.id, "release-train")])
    );

    // A skill moved out of the collection is pruned like an unshared one.
    api.change(&in_release.id, Change { collection_id: Some(None), ..Change::default() }).unwrap();
    let moved = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!(moved.removed, 1);
    assert!(!dir.path().join("deploy").exists());

    // --reset forgets the subscriptions and takes every readable skill again.
    let reset =
        sync_directory(&api, &identity(), dir.path(), &SyncOptions { reset: true, ..defaults() }).await.unwrap();
    assert_eq!(reset.written, 3);
    assert_eq!(reset.subscriptions, None);
    assert_eq!(read_manifest(dir.path()).unwrap().unwrap().subscriptions, None);
}

#[tokio::test]
async fn a_followed_collection_that_disappears_is_reported_and_its_skills_are_pruned() {
    let api = FakeSkillsApi::new();
    let release = api.seed_collection("release");
    api.seed_in("deploy", "D\n", Some(&release.id));
    let dir = tempfile::tempdir().unwrap();
    let follow = subscription(SubscriptionKind::Collection, &release.id, "release");
    sync_directory(&api, &identity(), dir.path(), &SyncOptions { subscribe: Some(follow.clone()), ..defaults() })
        .await
        .unwrap();

    api.remove_collection(&release.id);
    let summary = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!(summary.removed, 1);
    assert!(summary.warnings.iter().any(|warning| warning.contains("gone or no longer shared")));
    // The entry stays and is reported until the directory is reset with --reset.
    assert_eq!(read_manifest(dir.path()).unwrap().unwrap().subscriptions, Some(vec![follow]));
}

#[tokio::test]
async fn a_single_skill_can_be_followed_next_to_a_collection_and_a_name_in_both_namespaces_is_refused() {
    let api = FakeSkillsApi::new();
    let release = api.seed_collection("release");
    api.seed_in("deploy", "D\n", Some(&release.id));
    let lone = api.seed("triage", "T\n");
    api.seed("other", "O\n");
    let dir = tempfile::tempdir().unwrap();

    let skill = resolve_subscription(&api, "triage", None).await.unwrap();
    assert_eq!(skill, subscription(SubscriptionKind::Skill, &lone.id, "triage"));
    assert_eq!(
        resolve_subscription(&api, "release", None).await.unwrap(),
        subscription(SubscriptionKind::Collection, &release.id, "release")
    );
    let missing = resolve_subscription(&api, "nothing-here", None).await.unwrap_err();
    assert!(missing.to_string().contains("No collection or skill named \"nothing-here\""));

    let first = sync_directory(&api, &identity(), dir.path(), &SyncOptions { subscribe: Some(skill), ..defaults() })
        .await
        .unwrap();
    assert_eq!(first.written, 1);
    assert!(dir.path().join("triage/SKILL.md").exists());
    assert!(!dir.path().join("other").exists());

    let release_subscription = resolve_subscription(&api, "release", None).await.unwrap();
    let both = sync_directory(
        &api,
        &identity(),
        dir.path(),
        &SyncOptions { subscribe: Some(release_subscription), ..defaults() },
    )
    .await
    .unwrap();
    assert_eq!(both.written, 1);
    assert!(dir.path().join("deploy/SKILL.md").exists());

    api.change(&lone.id, Change { name: Some("incident-triage".into()), ..Change::default() }).unwrap();
    let renamed = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert!(
        renamed.warnings.iter().any(|warning| warning.contains("skill \"triage\" is now named \"incident-triage\""))
    );
    assert!(dir.path().join("incident-triage/SKILL.md").exists());
    assert!(!dir.path().join("triage").exists());

    api.remove(&lone.id);
    let removed = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert!(removed.warnings.iter().any(|warning| warning.contains("skill \"incident-triage\" is gone")));
    assert!(!dir.path().join("incident-triage").exists());

    // A skill named like a collection needs the caller to say which.
    api.seed("release", "R\n");
    let both_kinds = resolve_subscription(&api, "release", None).await.unwrap_err();
    assert!(both_kinds.to_string().contains("both a collection and a skill"));
    assert_eq!(
        resolve_subscription(&api, "release", Some(SubscriptionKind::Collection)).await.unwrap().kind,
        SubscriptionKind::Collection
    );
    assert_eq!(
        resolve_subscription(&api, "release", Some(SubscriptionKind::Skill)).await.unwrap().kind,
        SubscriptionKind::Skill
    );
}

#[tokio::test]
async fn sync_sets_up_a_folder_that_was_never_installed_into_with_every_readable_skill() {
    let api = FakeSkillsApi::new();
    api.seed("deploy", "D\n");
    let installed = tempfile::tempdir().unwrap();
    let fresh = tempfile::tempdir().unwrap();
    let missing = fresh.path().join("never-made");
    sync_directory(&api, &identity(), installed.path(), &defaults()).await.unwrap();

    // The hook path: the same targets as install, nothing special for a first run.
    let dirs = prepare_targets(&[installed.path().to_path_buf(), fresh.path().to_path_buf(), missing.clone()]).unwrap();
    assert_eq!(dirs.len(), 3);
    let summaries = sync_targets(&api, &identity(), &dirs, &defaults()).await.unwrap();
    assert_eq!(summaries.len(), 3);
    assert_eq!(summaries[0].skipped, 1);
    assert_eq!(summaries[1].written, 1);
    assert_eq!(summaries[2].written, 1);
    assert_eq!(read_manifest(fresh.path()).unwrap().unwrap().subscriptions, None);
    assert!(fresh.path().join("deploy/SKILL.md").exists());
    assert!(missing.join("deploy/SKILL.md").exists());
}

const GUIDE: &str = "references/guide.md";
const TOOL: &str = "bin/tool.bin";

/// A skill with a text file in a subfolder and a binary file, synced into a new directory.
async fn synced_folder_skill(api: &FakeSkillsApi) -> (String, tempfile::TempDir) {
    let id = api.seed("alpha", "A\n").id;
    api.put_files(&id, &[(GUIDE, b"guide v1\n"), (TOOL, &[0, 159, 146, 150, 255])]);
    let dir = tempfile::tempdir().unwrap();
    let summary = sync_directory(api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((summary.written, summary.warnings.len()), (1, 0));
    api.clear_calls();
    (id, dir)
}

#[tokio::test]
async fn a_changed_file_is_the_only_file_fetched_and_a_file_that_is_gone_on_the_server_is_removed() {
    let api = FakeSkillsApi::new();
    let (id, dir) = synced_folder_skill(&api).await;
    let folder = dir.path().join("alpha");
    assert_eq!(std::fs::read(folder.join(TOOL)).unwrap(), [0, 159, 146, 150, 255]);

    // Nothing changed: one request, as before a skill had files.
    sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!(api.calls(), vec!["list", "listServerSkills"]);

    api.clear_calls();
    api.put_files(&id, &[(GUIDE, b"guide v2\n"), (TOOL, &[0, 159, 146, 150, 255])]);
    let changed = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((changed.written, changed.warnings.len()), (1, 0));
    assert_eq!(
        api.calls(),
        vec![
            "list".to_string(),
            "listServerSkills".to_string(),
            format!("listFiles {id}"),
            format!("getFile {id} {GUIDE}")
        ]
    );
    assert_eq!(read(&folder.join(GUIDE)), "guide v2\n");

    // The folder of the removed file goes too, because it is empty. A file of the user stays.
    std::fs::write(folder.join("my-notes.txt"), "mine").unwrap();
    api.clear_calls();
    api.put_files(&id, &[(TOOL, &[0, 159, 146, 150, 255])]);
    let removed = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert!(removed.warnings.is_empty());
    assert_eq!(api.calls(), vec!["list".to_string(), "listServerSkills".to_string(), format!("listFiles {id}")]);
    assert!(!folder.join("references").exists());
    assert!(folder.join(TOOL).exists());
    assert_eq!(read(&folder.join("my-notes.txt")), "mine");
    let manifest = read_manifest(dir.path()).unwrap().unwrap();
    assert_eq!(manifest.skills[&id].files.keys().collect::<Vec<_>>(), ["SKILL.md", TOOL]);
}

#[tokio::test]
async fn a_local_edit_or_removal_of_a_supporting_file_blocks_the_sync_until_force() {
    let api = FakeSkillsApi::new();
    let (id, dir) = synced_folder_skill(&api).await;
    let folder = dir.path().join("alpha");
    api.put_files(&id, &[(GUIDE, b"guide v2\n"), (TOOL, &[1])]);

    std::fs::write(folder.join(GUIDE), "edited locally\n").unwrap();
    let edited = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((edited.written, edited.skipped), (0, 1));
    assert!(edited.warnings[0].contains("local edits"));
    assert_eq!(read(&folder.join(GUIDE)), "edited locally\n");
    assert_eq!(std::fs::read(folder.join(TOOL)).unwrap(), [0, 159, 146, 150, 255]);

    std::fs::write(folder.join(GUIDE), "guide v1\n").unwrap();
    std::fs::remove_file(folder.join(TOOL)).unwrap();
    let removed = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert!(removed.warnings[0].contains("local edits"));
    assert!(!folder.join(TOOL).exists());

    let forced =
        sync_directory(&api, &identity(), dir.path(), &SyncOptions { force: true, ..defaults() }).await.unwrap();
    assert_eq!((forced.written, forced.warnings.len()), (1, 0));
    assert_eq!(read(&folder.join(GUIDE)), "guide v2\n");
    assert_eq!(std::fs::read(folder.join(TOOL)).unwrap(), [1]);
}

#[tokio::test]
async fn a_folder_without_its_skill_md_is_written_again_and_each_local_edit_that_it_replaced_is_reported() {
    let api = FakeSkillsApi::new();
    let (id, dir) = synced_folder_skill(&api).await;
    let folder = dir.path().join("alpha");
    api.put_files(&id, &[(GUIDE, b"guide v1\n")]);
    std::fs::write(folder.join(GUIDE), "edited locally\n").unwrap();
    std::fs::write(folder.join(TOOL), "edited locally\n").unwrap();
    std::fs::remove_file(folder.join("SKILL.md")).unwrap();

    let summary = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((summary.written, summary.warnings.len()), (1, 1));
    assert!(summary.warnings[0].ends_with(&format!(
        "alpha: the sync replaced the local edits in {GUIDE}, {TOOL}. The folder had no SKILL.md, so the sync wrote the skill again"
    )));
    assert_eq!(read(&folder.join(GUIDE)), "guide v1\n");
    assert!(!folder.join(TOOL).exists());
}

#[tokio::test]
async fn a_file_of_the_user_is_left_alone_and_is_never_overwritten_by_a_new_file_of_the_server_without_force() {
    let api = FakeSkillsApi::new();
    let (id, dir) = synced_folder_skill(&api).await;
    let folder = dir.path().join("alpha");
    std::fs::write(folder.join("notes.md"), "mine\n").unwrap();

    // An extra file is no local edit: the skill still follows the server.
    api.put_files(&id, &[(GUIDE, b"guide v2\n"), (TOOL, &[1])]);
    let synced = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((synced.written, synced.warnings.len()), (1, 0));
    assert_eq!(read(&folder.join("notes.md")), "mine\n");

    // The server now has a file at that path. Nothing of the skill is written, so the folder stays whole.
    api.put_files(&id, &[(GUIDE, b"guide v3\n"), ("notes.md", b"theirs\n")]);
    let blocked = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((blocked.written, blocked.skipped), (0, 1));
    assert!(blocked.warnings[0].contains("Gatana did not write it"));
    assert_eq!(read(&folder.join("notes.md")), "mine\n");
    assert_eq!(read(&folder.join(GUIDE)), "guide v2\n");
    assert!(folder.join(TOOL).exists());

    let forced =
        sync_directory(&api, &identity(), dir.path(), &SyncOptions { force: true, ..defaults() }).await.unwrap();
    assert!(forced.warnings.is_empty());
    assert_eq!(read(&folder.join("notes.md")), "theirs\n");
    assert_eq!(read(&folder.join(GUIDE)), "guide v3\n");
    assert!(!folder.join(TOOL).exists());
}

#[tokio::test]
async fn a_version_2_manifest_upgrades_without_a_rewrite_and_without_a_false_local_edit() {
    let api = FakeSkillsApi::new();
    let a = api.seed("alpha", "# Alpha\n");
    let b = api.seed("beta", "# Beta\n");
    // Someone pushed a file with a newer CLI before this machine synced with CLI 5.2.
    api.put_files(&b.id, &[(GUIDE, b"guide\n")]);
    let b = api.find("beta").unwrap();
    let dir = tempfile::tempdir().unwrap();
    // What CLI 5.2 wrote: a rendered SKILL.md with its stamps, and one hash per skill.
    let old_file = |skill: &gatana_cli::skills::api::Skill| {
        format!(
            "---\nname: {}\ndescription: \"Use for {}\"\nmetadata:\n  gatana-id: \"{}\"\n  gatana-org: \"acme\"\n---\n\n# Old\n",
            skill.name, skill.name, skill.id
        )
    };
    let mut skills = serde_json::Map::new();
    for skill in [&a, &b] {
        std::fs::create_dir(dir.path().join(&skill.name)).unwrap();
        std::fs::write(dir.path().join(&skill.name).join("SKILL.md"), old_file(skill)).unwrap();
        let entry = serde_json::json!({
            "name": skill.name,
            "updatedAt": iso_millis(&skill.updated_at).unwrap(),
            "hash": sha256(old_file(skill).as_bytes()),
        });
        skills.insert(skill.id.clone(), entry);
    }
    let manifest = serde_json::json!({
        "version": 2, "orgId": "acme", "baseUrl": "https://acme.example", "syncedAt": "x", "skills": skills, "subscriptions": null,
    });
    std::fs::write(dir.path().join(MANIFEST_FILE), manifest.to_string()).unwrap();

    let first = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((first.written, first.skipped, first.warnings.len()), (0, 2, 0));
    // The first sync asks for the file list of each skill once, and fetches only what is missing.
    assert_eq!(
        api.calls(),
        vec![
            "list".to_string(),
            "listServerSkills".to_string(),
            format!("listFiles {}", a.id),
            format!("listFiles {}", b.id),
            format!("getFile {} {GUIDE}", b.id)
        ]
    );
    assert_eq!(read(&dir.path().join("alpha/SKILL.md")), old_file(&a));
    assert_eq!(read(&dir.path().join("beta/SKILL.md")), old_file(&b));
    assert_eq!(read(&dir.path().join("beta").join(GUIDE)), "guide\n");
    assert!(read(&dir.path().join(MANIFEST_FILE)).contains("\"version\": 3"));
    assert!(!read(&dir.path().join(MANIFEST_FILE)).contains("filesUnchecked"));

    api.clear_calls();
    let second = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((second.written, second.warnings.len()), (0, 0));
    assert_eq!(api.calls(), vec!["list", "listServerSkills"]);

    // A change of another file keeps the old SKILL.md. A change of the document replaces it.
    api.put_files(&b.id, &[(GUIDE, b"guide v2\n")]);
    sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!(read(&dir.path().join("beta/SKILL.md")), old_file(&b));
    api.change(&a.id, Change { content: Some("# New\n".into()), ..Change::default() }).unwrap();
    sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!(Some(read(&dir.path().join("alpha/SKILL.md"))), api.markdown_of(&a.id));
}

#[tokio::test]
async fn a_file_check_that_failed_or_that_waits_for_local_edits_runs_at_a_later_sync() {
    let pending = |dir: &Path| read_manifest(dir).unwrap().unwrap().files_unchecked;

    // The check fails: the skill stays in the set, and the next sync checks it.
    let api = FakeSkillsApi::new();
    let dir = tempfile::tempdir().unwrap();
    let id = cli_5_2_folder(&api, dir.path(), "# Old\n");
    *api.fail_files_of.borrow_mut() = Some(id.clone());
    let failed = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!(failed.errors.len(), 1);
    assert_eq!(pending(dir.path()), BTreeSet::from([id.clone()]));
    *api.fail_files_of.borrow_mut() = None;
    sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!(read(&dir.path().join("beta").join(OLD_GUIDE)), "guide\n");
    assert!(!read(&dir.path().join(MANIFEST_FILE)).contains("filesUnchecked"));

    // A skill with local edits waits, and the push that the warning advises deletes no file that
    // the folder never got.
    let api = FakeSkillsApi::new();
    let dir = tempfile::tempdir().unwrap();
    let id = cli_5_2_folder(&api, dir.path(), "# Mine\n");
    let skipped = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert!(skipped.warnings[0].contains("has local edits"));
    assert_eq!(pending(dir.path()), BTreeSet::from([id.clone()]));
    let refused = push_skills(&api, &identity(), &[dir.path().to_path_buf()], &PushOptions::default()).await.unwrap();
    assert!(refused[0].detail.contains("which this folder never got"));
    assert_eq!(api.files_of(&id).len(), 1);
    // Without the edit, the next sync does the check.
    let skill_md = dir.path().join("beta/SKILL.md");
    std::fs::write(&skill_md, read(&skill_md).replace("# Mine\n", "# Old\n")).unwrap();
    sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!(read(&dir.path().join("beta").join(OLD_GUIDE)), "guide\n");
    assert!(pending(dir.path()).is_empty());
}

#[tokio::test]
async fn each_bad_path_from_the_server_is_refused_and_no_file_lands_outside_the_skill_folder() {
    let api = FakeSkillsApi::new();
    let id = api.seed("alpha", "A\n").id;
    let bad = [
        "../escape.txt",
        "../../escape.txt",
        "a/../../escape.txt",
        "/abs.txt",
        "a//b.txt",
        "./c.txt",
        "a/./c.txt",
        "..",
        "back\\slash.txt",
        "..\\..\\escape.txt",
        "ctl\u{1}.txt",
        "line\nbreak.txt",
        "",
    ];
    let mut files: Vec<(&str, &[u8])> = bad.iter().map(|path| (*path, b"bad".as_slice())).collect();
    files.push(("ok/fine.txt", b"fine"));
    api.put_files(&id, &files);
    let base = tempfile::tempdir().unwrap();
    let dir = base.path().join("deep/skills");

    let summary = sync_directory(&api, &identity(), &dir, &defaults()).await.unwrap();
    assert_eq!(summary.written, 1);
    assert_eq!(summary.warnings.len(), bad.len());
    assert!(summary.warnings.iter().all(|warning| warning.contains("skipped")));
    // The warning shows a control character escaped.
    assert!(summary.warnings.iter().any(|warning| warning.contains("ctl\\u{1}.txt")));
    let written: Vec<String> = walkdir::WalkDir::new(base.path())
        .into_iter()
        .map(Result::unwrap)
        .filter(|entry| entry.file_type().is_file())
        .map(|entry| entry.path().strip_prefix(base.path()).unwrap().to_string_lossy().replace('\\', "/"))
        .collect();
    let mut written = written;
    written.sort();
    assert_eq!(
        written,
        ["deep/skills/.gatana-skills.json", "deep/skills/alpha/SKILL.md", "deep/skills/alpha/ok/fine.txt"]
    );
    let manifest = read_manifest(&dir).unwrap().unwrap();
    assert_eq!(manifest.skills[&id].files.keys().collect::<Vec<_>>(), ["SKILL.md", "ok/fine.txt"]);

    // A skill name that is no folder name is skipped too.
    api.change(&id, Change { name: Some("../alpha".into()), ..Change::default() }).unwrap();
    let renamed = sync_directory(&api, &identity(), &dir, &SyncOptions { prune: false, ..defaults() }).await.unwrap();
    assert!(renamed.warnings[0].contains("the name cannot be a folder name"));
    assert!(!base.path().join("deep/alpha").exists());
}

#[tokio::test]
async fn paths_that_collide_or_that_windows_cannot_hold_are_skipped_and_reported_on_every_platform() {
    let api = FakeSkillsApi::new();
    let id = api.seed("alpha", "A\n").id;
    api.put_files(
        &id,
        &[
            ("Docs/a.md", b"a"),
            ("docs/b.md", b"b"),
            ("caf\u{e9}.md", b"nfc"),
            ("cafe\u{301}.md", b"nfd"),
            ("CON.txt", b"x"),
            ("trailing.", b"x"),
            ("plain.md", b"p"),
        ],
    );
    let dir = tempfile::tempdir().unwrap();
    let summary = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!(summary.written, 1);
    let skipped =
        |path: &str| summary.warnings.iter().filter(|warning| warning.contains(&format!("{path:?} skipped"))).count();
    assert_eq!(summary.warnings.len(), 4);
    assert_eq!((skipped("docs/b.md"), skipped("caf\u{e9}.md"), skipped("CON.txt"), skipped("trailing.")), (1, 1, 1, 1));
    let manifest = read_manifest(dir.path()).unwrap().unwrap();
    assert_eq!(
        manifest.skills[&id].files.keys().collect::<Vec<_>>(),
        ["Docs/a.md", "SKILL.md", "cafe\u{301}.md", "plain.md"]
    );
    assert_eq!(read(&dir.path().join("alpha/Docs/a.md")), "a");
    assert_eq!(read(&dir.path().join("alpha/cafe\u{301}.md")), "nfd");

    // The skipped files are not asked for again while the skill does not change.
    api.clear_calls();
    let second = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((api.calls(), second.warnings.len()), (vec!["list".to_string(), "listServerSkills".to_string()], 0));
}

#[cfg(unix)]
#[tokio::test]
async fn a_symlink_on_the_way_to_a_file_blocks_the_write() {
    let api = FakeSkillsApi::new();
    let (id, dir) = synced_folder_skill(&api).await;
    let folder = dir.path().join("alpha");
    let outside = tempfile::tempdir().unwrap();

    // A subfolder of the skill is replaced by a symlink to a folder with the same content.
    std::fs::rename(folder.join("references"), outside.path().join("references")).unwrap();
    std::os::unix::fs::symlink(outside.path().join("references"), folder.join("references")).unwrap();
    api.put_files(&id, &[(GUIDE, b"guide v2\n"), (TOOL, &[1])]);
    let blocked = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((blocked.written, blocked.skipped), (0, 1));
    assert!(blocked.warnings[0].contains("is a symlink"));
    assert_eq!(read(&outside.path().join("references/guide.md")), "guide v1\n");
    // Nothing of the skill was written, so the folder is still the old version as a whole.
    assert_eq!(std::fs::read(folder.join(TOOL)).unwrap(), [0, 159, 146, 150, 255]);

    // A file that is gone on the server is not removed through the symlink either.
    api.put_files(&id, &[(TOOL, &[1])]);
    let kept = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert!(kept.warnings.iter().any(|warning| warning.contains("left in place")));
    assert!(outside.path().join("references/guide.md").exists());

    // A skill folder that is a symlink: not written into, also with --force.
    api.seed("linked", "L\n");
    std::os::unix::fs::symlink(outside.path(), dir.path().join("linked")).unwrap();
    let forced =
        sync_directory(&api, &identity(), dir.path(), &SyncOptions { force: true, ..defaults() }).await.unwrap();
    assert!(forced.warnings.iter().any(|warning| warning.contains("linked is a symlink")));
    assert!(!outside.path().join("SKILL.md").exists());
}

/// A SKILL.md as a server writes it: a comment, extra spaces, a quoted value and CRLF in one line,
/// so that a rewrite of the name shows every byte that it touched.
fn server_doc(name: &str) -> String {
    format!(
        "---\n# kept\nname:   {name}  # the name\r\ndescription: \"Use for {name}\"\nlicense: MIT\n---\n\n# {name}\n\nname: {name}\n"
    )
}

fn server_file_calls(api: &FakeSkillsApi) -> Vec<String> {
    api.calls().into_iter().filter(|call| call.starts_with("getServerFile")).collect()
}

#[tokio::test]
async fn server_skills_are_written_next_to_the_organization_skills_and_only_a_changed_file_is_fetched() {
    let api = FakeSkillsApi::new();
    api.seed("alpha", "A\n");
    let doc = server_doc("git-workflow");
    api.serve("github", "git-workflow", &[("SKILL.md", doc.as_bytes()), ("references/my%20notes.md", b"v1\n")]);
    api.serve("github", "team/review", &[("SKILL.md", server_doc("review").as_bytes()), ("bin/tool.bin", &[0, 255])]);
    let dir = tempfile::tempdir().unwrap();

    let first = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((first.written, first.total, first.warnings.len(), first.errors.len()), (3, 3, 0, 0));
    // A skill keeps its name and its bytes. A path is written as the URI means it.
    assert_eq!(read(&dir.path().join("git-workflow/SKILL.md")), doc);
    assert_eq!(read(&dir.path().join("git-workflow/references/my notes.md")), "v1\n");
    assert_eq!(std::fs::read(dir.path().join("review/bin/tool.bin")).unwrap(), [0, 255]);
    assert_eq!(server_file_calls(&api).len(), 4);

    // The entry is found by the server ID and the URI, never by the name.
    let manifest = read_manifest(dir.path()).unwrap().unwrap();
    assert_eq!(manifest.version, 3);
    assert_eq!(manifest.skills.len(), 1);
    let entry = &manifest.server_skills["srvr_github skill://git-workflow/SKILL.md"];
    assert_eq!((entry.server_id.as_str(), entry.server_slug.as_str()), ("srvr_github", "github"));
    assert_eq!((entry.uri.as_str(), entry.name.as_str()), ("skill://git-workflow/SKILL.md", "git-workflow"));
    assert_eq!(entry.files.keys().collect::<Vec<_>>(), ["SKILL.md", "references/my notes.md"]);
    assert_eq!(entry.files["SKILL.md"].digest, Some(format!("sha256:{}", sha256(doc.as_bytes()))));
    assert_eq!(manifest.server_skills["srvr_github skill://team/review/SKILL.md"].name, "review");

    // Nothing changed: one more request than a sync without server skills, and no file.
    api.clear_calls();
    let second = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((second.written, second.warnings.len()), (0, 0));
    assert_eq!(api.calls(), vec!["list", "listServerSkills"]);

    // One file changed and one is gone: one read.
    api.serve("github", "git-workflow", &[("SKILL.md", doc.as_bytes()), ("references/my%20notes.md", b"v2\n")]);
    api.serve("github", "team/review", &[("SKILL.md", server_doc("review").as_bytes())]);
    api.clear_calls();
    let changed = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((changed.written, changed.warnings.len()), (2, 0));
    assert_eq!(server_file_calls(&api), ["getServerFile github skill://git-workflow/references/my%20notes.md"]);
    assert_eq!(read(&dir.path().join("git-workflow/references/my notes.md")), "v2\n");
    assert!(!dir.path().join("review/bin").exists());
}

#[tokio::test]
async fn a_server_skill_that_loses_its_folder_gets_the_slug_in_front_and_a_rewritten_name() {
    let api = FakeSkillsApi::new();
    let org = api.seed("deploy", "The organization way.\n");
    let doc = server_doc("deploy");
    api.serve("github", "deploy", &[("SKILL.md", doc.as_bytes()), ("steps.md", b"1\n")]);
    api.serve("zeta", "ops/deploy", &[("SKILL.md", doc.as_bytes())]);
    let dir = tempfile::tempdir().unwrap();

    let first = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((first.written, first.errors.len()), (3, 0));
    assert_eq!(body_of(&dir.path().join("deploy/SKILL.md")), "The organization way.\n");
    // Every byte is the byte of the server, except the name.
    let renamed = read(&dir.path().join("github-deploy/SKILL.md"));
    assert_eq!(renamed, doc.replacen("name:   deploy  # the name", "name:   github-deploy  # the name", 1));
    assert_eq!(renamed.matches("github-deploy").count(), 1);
    assert_eq!(read(&dir.path().join("github-deploy/steps.md")), "1\n");
    assert!(read(&dir.path().join("zeta-deploy/SKILL.md")).contains("name:   zeta-deploy  # the name"));
    // The run that gives a skill the prefix says who has the plain name.
    assert_eq!(first.warnings.len(), 2);
    assert!(first.warnings[0].contains(
        "skill \"deploy\" of server \"github\" is in the folder github-deploy: an organization skill has the folder deploy"
    ));

    // The manifest holds the digest of the server and the hash of the file as written.
    let manifest = read_manifest(dir.path()).unwrap().unwrap();
    let entry = &manifest.server_skills["srvr_github skill://deploy/SKILL.md"];
    assert_eq!(entry.name, "github-deploy");
    assert_eq!(entry.files["SKILL.md"].digest, Some(format!("sha256:{}", sha256(doc.as_bytes()))));
    assert_eq!(entry.files["SKILL.md"].hash, sha256(renamed.as_bytes()));
    assert_ne!(entry.files["SKILL.md"].hash, sha256(doc.as_bytes()));

    // The rewritten file is no local edit, and nothing is fetched again.
    api.clear_calls();
    let second = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((second.written, second.skipped, second.warnings.len()), (0, 3, 0));
    assert_eq!(api.calls(), vec!["list", "listServerSkills"]);

    // The organization skill is deleted: the lower slug takes the plain name, with the bytes of
    // the server. The other server keeps the prefix.
    api.remove(&org.id);
    let third = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert!(third.errors.is_empty());
    assert_eq!(read(&dir.path().join("deploy/SKILL.md")), doc);
    assert_eq!(read(&dir.path().join("deploy/steps.md")), "1\n");
    assert!(!dir.path().join("github-deploy").exists());
    assert!(dir.path().join("zeta-deploy/SKILL.md").exists());
    let manifest = read_manifest(dir.path()).unwrap().unwrap();
    assert!(manifest.skills.is_empty());
    assert_eq!(manifest.server_skills["srvr_github skill://deploy/SKILL.md"].name, "deploy");

    // The name comes back: the server skill moves to the folder with the prefix again.
    api.seed("deploy", "Back.\n");
    sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!(body_of(&dir.path().join("deploy/SKILL.md")), "Back.\n");
    assert!(read(&dir.path().join("github-deploy/SKILL.md")).contains("name:   github-deploy"));

    // The folder with the prefix is taken too: the skill is skipped, with the two owners.
    api.seed("github-deploy", "Taken.\n");
    let taken = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert!(taken.warnings.iter().any(|warning| warning.contains(
        "skill \"deploy\" of server \"github\" skipped: an organization skill has the folder deploy, and an organization skill has the folder github-deploy"
    )));
    assert_eq!(body_of(&dir.path().join("github-deploy/SKILL.md")), "Taken.\n");
    assert!(!dir.path().join("github-deploy/steps.md").exists());
}

#[tokio::test]
async fn a_server_without_credentials_is_skipped_and_reported_once_with_the_authorize_link() {
    let api = FakeSkillsApi::new();
    api.serve("open", "notes", &[("SKILL.md", server_doc("notes").as_bytes())]);
    api.serve("safe", "one", &[("SKILL.md", server_doc("one").as_bytes())]);
    api.serve("safe", "two", &[("SKILL.md", server_doc("two").as_bytes())]);
    api.servers.borrow_mut().get_mut("safe").unwrap().needs_credentials = true;
    let dir = tempfile::tempdir().unwrap();

    let summary = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((summary.written, summary.skipped, summary.errors.len()), (1, 2, 0));
    assert!(dir.path().join("notes/SKILL.md").exists());
    assert!(!dir.path().join("one").exists() && !dir.path().join("two").exists());
    // One message and one request for the server, not one per skill.
    assert_eq!(summary.warnings.len(), 1);
    assert!(summary.warnings[0].contains("https://acme.example/authorize/safe"));
    assert!(summary.warnings[0].contains("The skills of server \"safe\" were skipped"));
    assert_eq!(server_file_calls(&api).iter().filter(|call| call.contains(" safe ")).count(), 1);

    // After the user authorizes, the next sync writes them.
    api.servers.borrow_mut().get_mut("safe").unwrap().needs_credentials = false;
    let later = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((later.written, later.warnings.len()), (2, 0));
    assert!(dir.path().join("two/SKILL.md").exists());
}

#[tokio::test]
async fn a_directory_with_a_subscription_list_takes_server_skills_only_of_a_server_that_it_follows() {
    let api = FakeSkillsApi::new();
    let alpha = api.seed("alpha", "A\n");
    api.seed("beta", "B\n");
    api.serve("github", "git-workflow", &[("SKILL.md", server_doc("git-workflow").as_bytes())]);
    api.serve("github", "review", &[("SKILL.md", server_doc("review").as_bytes())]);
    api.serve("jira", "tickets", &[("SKILL.md", server_doc("tickets").as_bytes())]);
    let dir = tempfile::tempdir().unwrap();

    // A list without a server: no server skill.
    let follow = |subscription| SyncOptions { subscribe: Some(subscription), ..defaults() };
    let only_alpha = follow(subscription(SubscriptionKind::Skill, &alpha.id, "alpha"));
    let first = sync_directory(&api, &identity(), dir.path(), &only_alpha).await.unwrap();
    assert_eq!((first.written, first.total), (1, 1));
    assert!(!dir.path().join("git-workflow").exists());

    // `install github --server` follows every skill of that server. A server is found only with
    // the flag, and one skill of a server cannot be followed.
    let server = resolve_subscription(&api, "github", Some(SubscriptionKind::Server)).await.unwrap();
    assert_eq!(server, subscription(SubscriptionKind::Server, "srvr_github", "github"));
    assert!(resolve_subscription(&api, "github", None).await.is_err());
    assert!(resolve_subscription(&api, "git-workflow", None).await.is_err());
    let unknown = resolve_subscription(&api, "nope", Some(SubscriptionKind::Server)).await.unwrap_err();
    assert!(unknown.to_string().contains("Servers with skills: github, jira"));
    let second = sync_directory(&api, &identity(), dir.path(), &follow(server.clone())).await.unwrap();
    assert_eq!((second.written, second.total), (2, 3));
    assert!(dir.path().join("git-workflow/SKILL.md").exists() && dir.path().join("review/SKILL.md").exists());
    assert!(!dir.path().join("tickets").exists() && !dir.path().join("beta").exists());
    assert_eq!(second.subscriptions.as_ref().unwrap()[1], server);

    // The server is switched off, or the user can no longer use it: its skills are no longer
    // listed, and its folders go by the rule for a deleted organization skill.
    let github = api.servers.borrow_mut().remove("github").unwrap();
    let kept =
        sync_directory(&api, &identity(), dir.path(), &SyncOptions { prune: false, ..defaults() }).await.unwrap();
    assert_eq!(kept.removed, 0);
    assert!(dir.path().join("review/SKILL.md").exists());
    let pruned = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((pruned.removed, pruned.total), (2, 1));
    assert!(!dir.path().join("git-workflow").exists() && !dir.path().join("review").exists());
    assert!(dir.path().join("alpha/SKILL.md").exists());
    assert!(pruned.warnings.iter().any(|warning| warning.contains("server \"github\" publishes no skills for you")));
    // The directory still follows the server, so the skills return with it.
    api.servers.borrow_mut().insert("github".into(), github);
    let back = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((back.written, back.warnings.len()), (2, 0));

    // A directory without a list takes every server skill that the listing holds.
    let all = tempfile::tempdir().unwrap();
    let everything = sync_directory(&api, &identity(), all.path(), &defaults()).await.unwrap();
    assert_eq!(everything.total, 5);
    assert!(all.path().join("tickets/SKILL.md").exists());
}

#[tokio::test]
async fn a_listing_that_fails_removes_nothing_and_a_backend_without_the_route_has_no_server_skills() {
    let api = FakeSkillsApi::new();
    api.seed("alpha", "A\n");
    api.serve("github", "review", &[("SKILL.md", server_doc("review").as_bytes())]);
    let dir = tempfile::tempdir().unwrap();
    let followed =
        SyncOptions { subscribe: Some(subscription(SubscriptionKind::Server, "srvr_github", "github")), ..defaults() };
    sync_directory(&api, &identity(), dir.path(), &followed).await.unwrap();
    let before = read_manifest(dir.path()).unwrap().unwrap();
    assert_eq!(before.server_skills.len(), 1);

    // A network error or a 5xx is not an empty listing: the folder and its record stay, also when
    // the folder lost a file. The run reports the failure.
    api.server_listing.set(ServerListing::Fails);
    api.serve("github", "review", &[("SKILL.md", server_doc("review").as_bytes()), ("new.md", b"new\n")]);
    let failed = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((failed.removed, failed.written, failed.warnings.len()), (0, 0, 0));
    assert_eq!(failed.errors.len(), 1);
    assert!(failed.errors[0].contains("the skills of connected servers were not updated"));
    assert!(dir.path().join("review/SKILL.md").exists());
    let after = read_manifest(dir.path()).unwrap().unwrap();
    assert_eq!(
        (after.server_skills, after.subscriptions),
        (before.server_skills.clone(), before.subscriptions.clone())
    );

    // A backend without the route: no warning, no error, nothing pruned, and no server skill in a
    // new directory.
    api.server_listing.set(ServerListing::NoRoute);
    let old_backend = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((old_backend.removed, old_backend.warnings.len(), old_backend.errors.len()), (0, 0, 0));
    assert!(dir.path().join("review/SKILL.md").exists());
    assert_eq!(read_manifest(dir.path()).unwrap().unwrap().server_skills, before.server_skills);
    let fresh = tempfile::tempdir().unwrap();
    let summary = sync_directory(&api, &identity(), fresh.path(), &defaults()).await.unwrap();
    assert_eq!((summary.total, summary.warnings.len(), summary.errors.len()), (1, 0, 0));
    assert!(!read(&fresh.path().join(MANIFEST_FILE)).contains("serverSkills"));
    let no_route = resolve_subscription(&api, "github", Some(SubscriptionKind::Server)).await.unwrap_err();
    assert!(no_route.to_string().contains("update the server"));

    // The listing works again: the sync catches up.
    api.server_listing.set(ServerListing::Works);
    let caught_up = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!(caught_up.written, 1);
    assert_eq!(read(&dir.path().join("review/new.md")), "new\n");
}

#[tokio::test]
async fn a_folder_that_a_server_skill_keeps_in_a_run_goes_to_no_other_skill() {
    // With --no-prune, a server skill that the listing no longer has keeps its folder. Another
    // server skill of that name gets the prefix.
    let api = FakeSkillsApi::new();
    api.serve("alpha", "deploy", &[("SKILL.md", server_doc("deploy").as_bytes())]);
    let dir = tempfile::tempdir().unwrap();
    sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    api.servers.borrow_mut().remove("alpha");
    api.serve("beta", "deploy", &[("SKILL.md", server_doc("deploy").as_bytes()), ("steps.md", b"1\n")]);
    let kept =
        sync_directory(&api, &identity(), dir.path(), &SyncOptions { prune: false, ..defaults() }).await.unwrap();
    assert_eq!(kept.errors.len(), 0);
    assert_eq!(kept.warnings.len(), 1);
    assert!(kept.warnings[0].contains("is in the folder beta-deploy: server \"alpha\" has the folder deploy"));
    assert_eq!(read(&dir.path().join("deploy/SKILL.md")), server_doc("deploy"));
    assert!(dir.path().join("beta-deploy/steps.md").exists());

    // While the listing fails, a new organization skill of that name waits, also with --force.
    let api = FakeSkillsApi::new();
    api.serve("alpha", "deploy", &[("SKILL.md", server_doc("deploy").as_bytes())]);
    let dir = tempfile::tempdir().unwrap();
    sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    api.server_listing.set(ServerListing::Fails);
    api.seed("deploy", "The organization way.\n");
    for options in [defaults(), SyncOptions { force: true, ..defaults() }] {
        let waiting = sync_directory(&api, &identity(), dir.path(), &options).await.unwrap();
        assert_eq!(waiting.warnings.len(), 1);
        assert!(waiting.warnings[0].starts_with("skill \"deploy\" skipped: server \"alpha\" keeps the folder"));
        assert!(waiting.warnings[0].ends_with("because the skills of connected servers were not listed"));
        assert_eq!(read(&dir.path().join("deploy/SKILL.md")), server_doc("deploy"));
    }

    // The listing works again: the organization skill gets the folder and the server skill the prefix.
    api.server_listing.set(ServerListing::Works);
    let moved = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!(moved.errors.len(), 0);
    assert_eq!(body_of(&dir.path().join("deploy/SKILL.md")), "The organization way.\n");
    assert!(dir.path().join("alpha-deploy/SKILL.md").exists());
}

#[tokio::test]
async fn a_bad_path_or_name_from_a_server_is_refused_and_no_file_lands_outside_the_skill_folder() {
    let api = FakeSkillsApi::new();
    let doc = server_doc("tricky");
    let bad: [&str; 9] = [
        "../escape.md",
        "/etc/absolute.md",
        "a/../../escape.md",
        "back\\slash.md",
        "%2e%2e/encoded-dots.md",
        "encoded%2Fslash.md",
        "bad%zzescape.md",
        "CON.txt",
        "skill://other/full-uri.md",
    ];
    let mut files: Vec<(&str, &[u8])> = vec![("SKILL.md", doc.as_bytes()), ("ok/fine.md", b"fine\n")];
    files.extend(bad.iter().map(|path| (*path, b"bad\n".as_slice())));
    api.serve("evil", "tricky", &files);
    // Names that cannot be a folder.
    api.serve("evil", "..", &[("SKILL.md", server_doc("..").as_bytes())]);
    api.serve("evil", "Has Space", &[("SKILL.md", server_doc("Has Space").as_bytes())]);
    let outer = tempfile::tempdir().unwrap();
    let dir = outer.path().join("skills");

    let summary = sync_directory(&api, &identity(), &dir, &defaults()).await.unwrap();
    assert_eq!((summary.written, summary.total, summary.errors.len()), (1, 1, 0));
    for path in bad {
        assert!(summary.warnings.iter().any(|warning| warning.contains(&format!("{path:?}"))), "{path}");
    }
    assert_eq!(summary.warnings.iter().filter(|warning| warning.contains("cannot be a folder name")).count(), 2);
    // Only the manifest and the two good files exist, anywhere.
    let found: Vec<String> = walkdir::WalkDir::new(outer.path())
        .into_iter()
        .map(|entry| entry.unwrap())
        .filter(|entry| entry.file_type().is_file())
        .map(|entry| entry.path().strip_prefix(outer.path()).unwrap().to_string_lossy().into_owned())
        .collect::<std::collections::BTreeSet<_>>()
        .into_iter()
        .collect();
    assert_eq!(found, ["skills/.gatana-skills.json", "skills/tricky/SKILL.md", "skills/tricky/ok/fine.md"]);

    // The skipped files do not make the skill look changed: the next sync asks for no file and
    // repeats no warning.
    api.clear_calls();
    let second = sync_directory(&api, &identity(), &dir, &defaults()).await.unwrap();
    assert_eq!(api.calls(), vec!["list", "listServerSkills"]);
    assert_eq!(second.warnings.iter().filter(|warning| warning.contains("tricky")).count(), 0);
}

#[tokio::test]
async fn a_server_skill_is_written_whole_or_not_at_all_and_local_edits_stay_until_force() {
    let api = FakeSkillsApi::new();
    let doc = server_doc("review");
    api.serve("github", "review", &[("SKILL.md", doc.as_bytes()), ("a.md", b"a1\n"), ("b.md", b"b1\n")]);
    let dir = tempfile::tempdir().unwrap();
    sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    let before = read_manifest(dir.path()).unwrap().unwrap();

    // The server sends content that is not what the listing describes: no file of the skill changes.
    api.serve("github", "review", &[("SKILL.md", doc.as_bytes()), ("a.md", b"a2\n"), ("b.md", b"b2\n")]);
    api.servers.borrow_mut().get_mut("github").unwrap().tampered.insert("skill://review/b.md".into(), b"evil".to_vec());
    let refused = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((refused.written, refused.skipped, refused.errors.len()), (0, 1, 0));
    assert!(refused.warnings[0].contains("review changed on the server during the sync"));
    assert_eq!(read(&dir.path().join("review/a.md")), "a1\n");
    assert_eq!(read(&dir.path().join("review/b.md")), "b1\n");
    assert_eq!(read_manifest(dir.path()).unwrap().unwrap().server_skills, before.server_skills);

    // A local edit blocks the update, with no request for a file.
    api.servers.borrow_mut().get_mut("github").unwrap().tampered.clear();
    std::fs::write(dir.path().join("review/a.md"), "mine\n").unwrap();
    api.clear_calls();
    let edited = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!(edited.written, 0);
    assert!(edited.warnings[0].contains("review has local edits. Skipped. Use --force"));
    assert!(server_file_calls(&api).is_empty());
    assert_eq!(read(&dir.path().join("review/a.md")), "mine\n");

    let forced =
        sync_directory(&api, &identity(), dir.path(), &SyncOptions { force: true, ..defaults() }).await.unwrap();
    assert_eq!(forced.written, 1);
    assert_eq!(read(&dir.path().join("review/a.md")), "a2\n");
    assert_eq!(read(&dir.path().join("review/b.md")), "b2\n");

    // A folder that the sync does not own is not taken for a server skill.
    api.serve("github", "mine", &[("SKILL.md", server_doc("mine").as_bytes())]);
    std::fs::create_dir(dir.path().join("mine")).unwrap();
    std::fs::write(dir.path().join("mine/SKILL.md"), "hand written\n").unwrap();
    let foreign = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert!(foreign.warnings.iter().any(|warning| warning.contains("mine is not tracked by Gatana")));
    assert_eq!(read(&dir.path().join("mine/SKILL.md")), "hand written\n");
}

#[tokio::test]
async fn a_skill_that_fails_does_not_lose_the_record_of_the_skills_that_the_run_wrote() {
    let api = FakeSkillsApi::new();
    let a = api.seed("alpha", "A\n");
    let b = api.seed("beta", "B\n");
    let c = api.seed("gamma", "C\n");
    api.serve("github", "review", &[("SKILL.md", server_doc("review").as_bytes())]);
    *api.fail_files_of.borrow_mut() = Some(b.id.clone());
    let dir = tempfile::tempdir().unwrap();

    // The run goes on after the failure, records what it wrote and names the skill that failed.
    let first = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((first.written, first.skipped, first.total), (3, 1, 3));
    assert_eq!(first.errors.len(), 1);
    assert!(first.errors[0].contains("beta") && first.errors[0].contains("connection reset"));
    assert!(!dir.path().join("beta").exists());
    let manifest = read_manifest(dir.path()).unwrap().unwrap();
    assert_eq!(manifest.skills.keys().collect::<Vec<_>>(), [&a.id, &c.id]);
    assert_eq!(manifest.server_skills.len(), 1);

    // The next sync owns the folders of the first one: no folder is foreign, and only the skill
    // that failed is fetched.
    *api.fail_files_of.borrow_mut() = None;
    api.clear_calls();
    let second = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((second.written, second.warnings.len(), second.errors.len()), (1, 0, 0));
    assert_eq!(
        api.calls(),
        vec![
            "list".to_string(),
            "listServerSkills".to_string(),
            format!("listFiles {}", b.id),
            format!("getFile {} SKILL.md", b.id)
        ]
    );

    // A skill that fails at an update keeps the entry and the folder that it had.
    api.change(&b.id, Change { content: Some("B2\n".into()), ..Change::default() }).unwrap();
    *api.fail_files_of.borrow_mut() = Some(b.id.clone());
    let third = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!(third.errors.len(), 1);
    assert_eq!(body_of(&dir.path().join("beta/SKILL.md")), "B\n");
    assert!(read_manifest(dir.path()).unwrap().unwrap().skills.contains_key(&b.id));
}

#[tokio::test]
async fn the_manifest_on_disk_follows_the_run_so_a_stopped_run_keeps_the_record_of_what_it_finished() {
    let api = FakeSkillsApi::new();
    // More skills than the sync reads at a time, of both kinds.
    for name in ["a1", "a2", "a3", "a4", "a5", "a6"] {
        api.seed(name, "organization\n");
    }
    for name in ["s1", "s2", "s3", "s4", "s5", "s6"] {
        api.serve("github", name, &[("SKILL.md", server_doc(name).as_bytes()), ("more.md", b"more\n")]);
    }
    let dir = tempfile::tempdir().unwrap();

    // At each read of a file: what the manifest on disk holds, and whether every folder that it
    // names is whole. A run that stops at this read leaves exactly that state.
    let seen = std::rc::Rc::new(std::cell::RefCell::new(Vec::new()));
    let (root, log) = (dir.path().to_path_buf(), seen.clone());
    *api.on_file_read.borrow_mut() = Some(Box::new(move |call| {
        let Some(manifest) = read_manifest(&root).unwrap() else {
            return log.borrow_mut().push((call.to_string(), 0, true));
        };
        let org = manifest.skills.values().map(|entry| (&entry.name, &entry.files));
        let server = manifest.server_skills.values().map(|entry| (&entry.name, &entry.files));
        let folders: Vec<_> = org.chain(server).collect();
        let whole = folders.iter().all(|(name, files)| {
            files.iter().all(|(path, file)| {
                std::fs::read(root.join(name).join(path)).is_ok_and(|content| sha256(&content) == file.hash)
            })
        });
        log.borrow_mut().push((call.to_string(), folders.len(), whole));
    }));

    let summary = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((summary.written, summary.total, summary.warnings.len()), (12, 12, 0));
    let seen = seen.borrow().clone();
    assert_eq!(seen.len(), 18);
    // The record grows while the run goes on, and it never names a folder that is not whole.
    assert_eq!(seen[0].1, 0);
    assert!(seen.windows(2).all(|pair| pair[0].1 <= pair[1].1));
    assert!(seen.iter().all(|(_, _, whole)| *whole));
    // While the API serves the last skill, the manifest on disk already holds most of the others.
    let (last_call, recorded, _) = seen.last().unwrap();
    assert!(last_call.contains("skill://s6/"));
    assert!((8..12).contains(recorded), "{recorded}");

    // A sync with no change still writes the manifest once.
    *api.on_file_read.borrow_mut() = None;
    let before = read(&dir.path().join(MANIFEST_FILE));
    let again = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!(again.written, 0);
    let after = read_manifest(dir.path()).unwrap().unwrap();
    assert_eq!(
        serde_json::to_value(&after.skills).unwrap(),
        serde_json::from_str::<serde_json::Value>(&before).unwrap()["skills"]
    );

    // The state of a run that was stopped while it read the files of the last skill: the manifest
    // holds the other folders, and the last folder does not exist. The next run owns the recorded
    // folders, reports no folder as not tracked, and reads only the files of the last skill.
    let mut stopped = after.clone();
    let lost = stopped.server_skills.shift_remove("srvr_github skill://s6/SKILL.md").unwrap();
    std::fs::write(dir.path().join(MANIFEST_FILE), serde_json::to_string(&stopped).unwrap()).unwrap();
    std::fs::remove_dir_all(dir.path().join(&lost.name)).unwrap();
    api.clear_calls();
    let resumed = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((resumed.written, resumed.warnings.len(), resumed.total), (1, 0, 12));
    assert_eq!(
        server_file_calls(&api),
        ["getServerFile github skill://s6/SKILL.md", "getServerFile github skill://s6/more.md"]
    );
}

#[tokio::test]
async fn server_skills_are_read_a_few_at_a_time_and_no_read_starts_after_a_credentials_prompt() {
    let api = FakeSkillsApi::new();
    for name in ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8"] {
        api.serve("safe", name, &[("SKILL.md", server_doc(name).as_bytes())]);
        api.serve("open", &format!("o-{name}"), &[("SKILL.md", server_doc(&format!("o-{name}")).as_bytes())]);
    }
    api.servers.borrow_mut().get_mut("safe").unwrap().needs_credentials = true;
    let dir = tempfile::tempdir().unwrap();

    let summary = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!((summary.written, summary.skipped, summary.errors.len()), (8, 8, 0));
    assert_eq!(summary.warnings.len(), 1);
    assert!(summary.warnings[0].contains("The skills of server \"safe\" were skipped"));
    assert_eq!(server_file_calls(&api).iter().filter(|call| call.contains(" safe ")).count(), 1);
    assert_eq!(read_manifest(dir.path()).unwrap().unwrap().server_skills.len(), 8);
}
