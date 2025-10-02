"""Update repositories with fancy output"""

from pathlib import Path

import git
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from machineconfig.scripts.python.repos_helpers.repos_helper_update import RepositoryUpdateResult, run_uv_sync, update_repository
from machineconfig.utils.io import read_ini
from machineconfig.utils.source_of_truth import DEFAULTS_PATH


console = Console()


def _display_summary(results: list[RepositoryUpdateResult]) -> None:
    """Display a comprehensive summary of all repository update operations."""

    console.rule("[bold blue]📊 Repository Update Summary[/bold blue]")

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

    overview_lines = [
        f"[bold]Total repositories processed:[/] {total_repos}",
        f"✅ Successful updates: {successful_repos}",
        f"❌ Failed updates: {error_repos}",
        f"⏭️  Skipped: {skipped_repos}",
    ]
    if auth_failed_repos > 0:
        overview_lines.append(f"🔐 Authentication failed: {auth_failed_repos}")

    console.print(
        Panel(
            "\n".join(overview_lines),
            title="� Overview",
            border_style="blue",
            padding=(1, 2),
        )
    )

    changes_lines = [
        f"Repositories with new commits: {repos_with_changes}",
        f"Repositories with dependency changes: {repos_with_dep_changes}",
        f"Repositories with uncommitted changes: {repos_with_uncommitted}",
    ]
    console.print(
        Panel(
            "\n".join(changes_lines),
            title="� Changes",
            border_style="magenta",
            padding=(1, 2),
        )
    )

    uv_sync_lines = [
        f"uv sync operations attempted: {uv_sync_runs}",
        f"uv sync operations successful: {uv_sync_successes}",
    ]
    if uv_sync_runs > uv_sync_successes:
        uv_sync_lines.append(f"uv sync operations failed: {uv_sync_runs - uv_sync_successes}")

    console.print(
        Panel(
            "\n".join(uv_sync_lines),
            title="📦 uv sync",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    table = Table(title="📋 Detailed Results", show_lines=True, header_style="bold blue")
    table.add_column("Repository", style="bold")
    table.add_column("Status")
    table.add_column("Details", overflow="fold")

    for result in results:
        repo_name = Path(result["repo_path"]).name
        status_icon = {"success": "✅", "error": "❌", "skipped": "⏭️", "auth_failed": "🔐"}.get(result["status"], "❓")
        status_label = result["status"].replace("_", " ").title()

        detail_lines: list[str] = []

        if result["status"] == "error" and result["error_message"]:
            detail_lines.append(f"💥 Error: {result['error_message']}")

        if result["commits_changed"]:
            detail_lines.append(f"🔄 Updated: {result['commit_before'][:8]} → {result['commit_after'][:8]}")
        elif result["status"] == "success":
            detail_lines.append("📍 Already up to date")

        if result["had_uncommitted_changes"]:
            files_str = ", ".join(result["uncommitted_files"])
            detail_lines.append(f"⚠️  Uncommitted changes: {files_str}")

        if result["dependencies_changed"]:
            changes = []
            if result["pyproject_changed"]:
                changes.append("pyproject.toml")
            if changes:
                detail_lines.append(f"📋 Dependencies changed: {', '.join(changes)}")

        if result["uv_sync_ran"]:
            sync_status = "✅" if result["uv_sync_success"] else "❌"
            detail_lines.append(f"📦 uv sync: {sync_status}")

        if result["is_machineconfig_repo"] and result["permissions_updated"]:
            detail_lines.append("🛠  Updated permissions for machineconfig files")

        if result["remotes_processed"]:
            detail_lines.append(f"📡 Processed remotes: {', '.join(result['remotes_processed'])}")
        if result["remotes_skipped"]:
            detail_lines.append(f"⏭️  Skipped remotes: {', '.join(result['remotes_skipped'])}")

        table.add_row(f"{status_icon} {repo_name}", status_label, "\n".join(detail_lines) or "—")

    console.print(table)

    if error_repos == 0 and auth_failed_repos == 0:
        summary_text = Text("🎉 All repositories processed successfully!", style="green", justify="center")
        border = "green"
    elif successful_repos > 0:
        summary_text = Text(
            f"⚠️  {successful_repos}/{total_repos} repositories processed successfully",
            style="yellow",
            justify="center",
        )
        border = "yellow"
    else:
        summary_text = Text("❌ No repositories were successfully processed", style="red", justify="center")
        border = "red"

    console.print(Panel(summary_text, title="Summary", border_style=border, padding=(1, 2)))


def main(verbose: bool = True, allow_password_prompt: bool = False) -> None:
    """Main function to update all configured repositories."""
    _ = verbose
    repos: list[Path] = [Path.home() / "code/machineconfig"]
    try:
        tmp = read_ini(DEFAULTS_PATH)["general"]["repos"].split(",")
        if tmp[-1] == "":
            tmp = tmp[:-1]
        for item in tmp:
            item_obj = Path(item).expanduser()
            if item_obj not in repos:
                repos.append(item_obj)
    except (FileNotFoundError, KeyError, IndexError):
        console.print(
            Panel(
                "\n".join(
                    [
                        f"🚫 Configuration error: missing {DEFAULTS_PATH} or the [general] section / repos key.",
                        "ℹ️  Using default repositories instead.",
                    ]
                ),
                title="Configuration Missing",
                border_style="red",
                padding=(1, 2),
            )
        )
        console.print(
            Panel(
                "\n".join(
                    [
                        "✨ Example configuration:",
                        "",
                        "[general]",
                        "repos = ~/code/repo1,~/code/repo2",
                        "rclone_config_name = onedrivePersonal",
                        "email_config_name = Yahoo3",
                        "to_email = myemail@email.com",
                    ]
                ),
                border_style="cyan",
                padding=(1, 2),
            )
        )

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
            console.print(
                Panel(
                    "\n".join(
                        [
                            f"❌ Repository error: {expanded_path}",
                            f"Exception: {ex}",
                        ]
                    ),
                    border_style="red",
                    padding=(1, 2),
                )
            )
    # Run uv sync for repositories where pyproject.toml changed but sync wasn't run yet
    for repo_path in repos_with_changes:
        run_uv_sync(repo_path)
    # Generate and display summary
    _display_summary(results)


if __name__ == "__main__":
    main()
