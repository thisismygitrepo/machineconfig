"""Update repositories with fancy output"""

import git
from pathlib import Path
from machineconfig.scripts.python.repos_helper_update import RepositoryUpdateResult, run_uv_sync, update_repository
from machineconfig.utils.path_reduced import PathExtended as PathExtended
from machineconfig.utils.source_of_truth import DEFAULTS_PATH
from machineconfig.utils.utils2 import read_ini


def _display_summary(results: list[RepositoryUpdateResult]) -> None:
    """Display a comprehensive summary of all repository update operations."""
    print("\n" + "=" * 80)
    print("📊 REPOSITORY UPDATE SUMMARY")
    print("=" * 80)

    # Calculate statistics
    total_repos = len(results)
    successful_repos = sum(1 for r in results if r["status"] == "success")
    error_repos = sum(1 for r in results if r["status"] == "error")
    skipped_repos = sum(1 for r in results if r["status"] == "skipped")
    auth_failed_repos = sum(1 for r in results if r["status"] == "auth_failed")

    repos_with_changes = sum(1 for r in results if r["commits_changed"])
    repos_with_uncommitted = sum(1 for r in results if r["had_uncommitted_changes"])
    repos_with_dep_changes = sum(1 for r in results if r["dependencies_changed"])
    uv_sync_runs = sum(1 for r in results if r["uv_sync_ran"])
    uv_sync_successes = sum(1 for r in results if r["uv_sync_ran"] and r["uv_sync_success"])

    # Overview statistics
    print("📈 OVERVIEW:")
    print(f"   Total repositories processed: {total_repos}")
    print(f"   ✅ Successful updates: {successful_repos}")
    print(f"   ❌ Failed updates: {error_repos}")
    print(f"   ⏭️  Skipped: {skipped_repos}")
    if auth_failed_repos > 0:
        print(f"   🔐 Authentication failed: {auth_failed_repos}")
    print()

    print("🔄 CHANGES:")
    print(f"   Repositories with new commits: {repos_with_changes}")
    print(f"   Repositories with dependency changes: {repos_with_dep_changes}")
    print(f"   Repositories with uncommitted changes: {repos_with_uncommitted}")
    print()

    print("📦 UV SYNC:")
    print(f"   uv sync operations attempted: {uv_sync_runs}")
    print(f"   uv sync operations successful: {uv_sync_successes}")
    if uv_sync_runs > uv_sync_successes:
        print(f"   uv sync operations failed: {uv_sync_runs - uv_sync_successes}")
    print()

    # Detailed results per repository
    print("📋 DETAILED RESULTS:")
    for result in results:
        repo_name = Path(result["repo_path"]).name
        status_icon = {"success": "✅", "error": "❌", "skipped": "⏭️", "auth_failed": "🔐"}.get(result["status"], "❓")
        print(f"   {status_icon} {repo_name}")

        if result["status"] == "error" and result["error_message"]:
            print(f"      💥 Error: {result['error_message']}")

        if result["commits_changed"]:
            print(f"      🔄 Updated: {result['commit_before'][:8]} → {result['commit_after'][:8]}")
        elif result["status"] == "success":
            print("      📍 Already up to date")

        if result["had_uncommitted_changes"]:
            files_str = ", ".join(result["uncommitted_files"])
            print(f"      ⚠️  Had uncommitted changes: {files_str}")

        if result["dependencies_changed"]:
            changes = []
            if result["pyproject_changed"]:
                changes.append("pyproject.toml")
            print(f"      📋 Dependencies changed: {', '.join(changes)}")

        if result["uv_sync_ran"]:
            sync_status = "✅" if result["uv_sync_success"] else "❌"
            print(f"      📦 uv sync: {sync_status}")

        if result["is_machineconfig_repo"] and result["permissions_updated"]:
            print("      🛠  Updated permissions for machineconfig files")

        if result["remotes_processed"]:
            print(f"      📡 Processed remotes: {', '.join(result['remotes_processed'])}")
        if result["remotes_skipped"]:
            print(f"      ⏭️  Skipped remotes: {', '.join(result['remotes_skipped'])}")

    print("\n" + "=" * 80)

    # Final status
    if error_repos == 0 and auth_failed_repos == 0:
        print("🎉 All repositories processed successfully!")
    elif successful_repos > 0:
        print(f"⚠️  {successful_repos}/{total_repos} repositories processed successfully")
    else:
        print("❌ No repositories were successfully processed")
    print("=" * 80)


def main(verbose: bool = True, allow_password_prompt: bool = False) -> None:
    """Main function to update all configured repositories."""
    _ = verbose
    repos: list[PathExtended] = [PathExtended.home() / "code/machineconfig", PathExtended.home() / "code/crocodile"]
    try:
        tmp = read_ini(DEFAULTS_PATH)["general"]["repos"].split(",")
        if tmp[-1] == "":
            tmp = tmp[:-1]
        for item in tmp:
            item_obj = PathExtended(item).expanduser()
            if item_obj not in repos:
                repos.append(item_obj)
    except (FileNotFoundError, KeyError, IndexError):
        print(f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 🚫 Configuration Error: Missing {DEFAULTS_PATH} or section [general] or key repos
┃ ℹ️  Using default repositories instead
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
        print("""
┌────────────────────────────────────────────────────────────────
│ ✨ Example Configuration:
│
│ [general]
│ repos = ~/code/repo1,~/code/repo2
│ rclone_config_name = onedrivePersonal
│ email_config_name = Yahoo3
│ to_email = myemail@email.com
└────────────────────────────────────────────────────────────────""")

    # Process repositories
    results: list[RepositoryUpdateResult] = []
    repos_with_changes = []

    for expanded_path in repos:
        try:
            repo = git.Repo(str(expanded_path), search_parent_directories=True)
            # Update repository and get detailed results
            result = update_repository(repo, allow_password_prompt=allow_password_prompt, auto_sync=True)
            results.append(result)

            # Keep track of repos with dependency changes for additional uv sync
            if result["dependencies_changed"] and not result["uv_sync_ran"]:
                repos_with_changes.append(Path(repo.working_dir))

        except Exception as ex:
            # Create a result for failed repos
            error_result: RepositoryUpdateResult = {
                "repo_path": str(expanded_path),
                "status": "error",
                "had_uncommitted_changes": False,
                "uncommitted_files": [],
                "commit_before": "",
                "commit_after": "",
                "commits_changed": False,
                "pyproject_changed": False,
                "dependencies_changed": False,
                "uv_sync_ran": False,
                "uv_sync_success": False,
                "remotes_processed": [],
                "remotes_skipped": [],
                "error_message": str(ex),
                "is_machineconfig_repo": False,
                "permissions_updated": False,
            }
            results.append(error_result)
            print(f"""❌ Repository Error: Path: {expanded_path}
Exception: {ex}
{"-" * 50}""")

    # Run uv sync for repositories where pyproject.toml changed but sync wasn't run yet
    for repo_path in repos_with_changes:
        run_uv_sync(repo_path)

    # Generate and display summary
    _display_summary(results)


if __name__ == "__main__":
    main()
