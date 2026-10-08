mod common;

use common::{Change, FakeSkillsApi};
use gatana_cli::skills::frontmatter::parse_skill_md;
use gatana_cli::skills::manifest::{Subscription, SubscriptionKind, read_manifest};
use gatana_cli::skills::subscriptions::resolve_subscription;
use gatana_cli::skills::sync::{SkillsIdentity, SyncOptions, sync_directory, sync_targets};
use gatana_cli::skills::targets::prepare_targets;
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
    let (frontmatter, body) = parse_skill_md(&read(&dir.path().join("alpha/SKILL.md"))).unwrap();
    assert_eq!(frontmatter.meta("gatana-id"), Some(a.id.as_str()));
    assert_eq!(body, "# Alpha\n");
    let manifest = read_manifest(dir.path()).unwrap().unwrap();
    assert_eq!(manifest.org_id, "acme");
    assert_eq!(manifest.skills[&a.id].name, "alpha");

    api.clear_calls();
    let second = sync_directory(&api, &identity(), dir.path(), &defaults()).await.unwrap();
    assert_eq!(second.written, 0);
    assert_eq!(api.calls(), vec!["list"]);
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
    assert!(summary.warnings[0].contains("not created by this sync"));

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
    assert!(skipped.warnings[0].contains("edited locally"));
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
    assert!(refused.to_string().contains("synced from acme"));
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
    let (frontmatter, _) = parse_skill_md(&read(&dir.path().join("deploy/SKILL.md"))).unwrap();
    assert_eq!(frontmatter.meta("gatana-collection"), Some("release"));

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
