from machineconfig.utils.path_extended import PathExtended
from machineconfig.utils.accessories import randstr
from machineconfig.scripts.python.repos_helpers.update import update_repository

from typing import Optional
from dataclasses import dataclass
from enum import Enum

from rich import print as pprint
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns


class GitAction(Enum):
    commit = "commit"
    push = "push"
    pull = "pull"


@dataclass
class GitOperationResult:
    """Result of a git operation on a single repository."""
    repo_path: PathExtended
    action: str
    success: bool
    message: str
    is_git_repo: bool = True
    had_changes: bool = False
    remote_count: int = 0


@dataclass  
class GitOperationSummary:
    """Summary of all git operations performed."""
    # Basic statistics
    total_paths_processed: int = 0
    git_repos_found: int = 0
    non_git_paths: int = 0
    
    # Per-operation statistics
    commits_attempted: int = 0
    commits_successful: int = 0
    commits_no_changes: int = 0
    commits_failed: int = 0
    
    pulls_attempted: int = 0
    pulls_successful: int = 0
    pulls_failed: int = 0
    
    pushes_attempted: int = 0
    pushes_successful: int = 0
    pushes_failed: int = 0
    
    def __post_init__(self):
        self.failed_operations: list[GitOperationResult] = []
        self.repos_without_remotes: list[PathExtended] = []


def git_action(path: PathExtended, action: GitAction, mess: Optional[str], r: bool, auto_uv_sync: bool) -> GitOperationResult:
    """Perform git actions using Python instead of shell scripts. Returns detailed operation result."""
    from git.exc import InvalidGitRepositoryError
    from git.repo import Repo

    try:
        repo = Repo(str(path), search_parent_directories=False)
    except InvalidGitRepositoryError:
        pprint(f"⚠️ Skipping {path} because it is not a git repository.")
        if r:
            results = [git_action(path=sub_path, action=action, mess=mess, r=r, auto_uv_sync=auto_uv_sync) for sub_path in path.search()]
            # For recursive calls, we need to aggregate results somehow
            # For now, return success if all recursive operations succeeded
            all_successful = all(result.success for result in results)
            return GitOperationResult(
                repo_path=path,
                action=action.value,
                success=all_successful,
                message=f"Recursive operation: {len([r for r in results if r.success])}/{len(results)} succeeded",
                is_git_repo=False
            )
        else:
            return GitOperationResult(
                repo_path=path,
                action=action.value,
                success=False,
                message="Not a git repository",
                is_git_repo=False
            )

    print(f">>>>>>>>> 🔧{action} - {path}")
    remote_count = len(repo.remotes)

    try:
        if action == GitAction.commit:
            if mess is None:
                mess = "auto_commit_" + randstr()

            # Check if there are changes to commit
            if repo.is_dirty() or repo.untracked_files:
                repo.git.add(A=True)  # Stage all changes
                repo.index.commit(mess)
                print(f"✅ Committed changes with message: {mess}")
                return GitOperationResult(
                    repo_path=path,
                    action=action.value,
                    success=True,
                    message=f"Committed changes with message: {mess}",
                    had_changes=True,
                    remote_count=remote_count
                )
            else:
                print("ℹ️  No changes to commit")
                return GitOperationResult(
                    repo_path=path,
                    action=action.value,
                    success=True,
                    message="No changes to commit",
                    had_changes=False,
                    remote_count=remote_count
                )

        elif action == GitAction.push:
            if not repo.remotes:
                print("⚠️ No remotes configured for push")
                return GitOperationResult(
                    repo_path=path,
                    action=action.value,
                    success=False,
                    message="No remotes configured",
                    remote_count=0
                )
                
            success = True
            failed_remotes = []
            for remote in repo.remotes:
                try:
                    print(f"🚀 Pushing to {remote.url}")
                    remote.push(repo.active_branch.name)
                    print(f"✅ Pushed to {remote.name}")
                except Exception as e:
                    print(f"❌ Failed to push to {remote.name}: {e}")
                    failed_remotes.append(f"{remote.name}: {str(e)}")
                    success = False
                    
            message = "Push successful" if success else f"Push failed for: {', '.join(failed_remotes)}"
            return GitOperationResult(
                repo_path=path,
                action=action.value,
                success=success,
                message=message,
                remote_count=remote_count
            )

        elif action == GitAction.pull:
            # Use the enhanced update function with uv sync support
            try:
                update_repository(repo, auto_uv_sync=auto_uv_sync, allow_password_prompt=False)
                print("✅ Pull completed")
                return GitOperationResult(
                    repo_path=path,
                    action=action.value,
                    success=True,
                    message="Pull completed successfully",
                    remote_count=remote_count
                )
            except Exception as e:
                print(f"❌ Pull failed: {e}")
                return GitOperationResult(
                    repo_path=path,
                    action=action.value,
                    success=False,
                    message=f"Pull failed: {str(e)}",
                    remote_count=remote_count
                )

    except Exception as e:
        print(f"❌ Error performing {action} on {path}: {e}")
        return GitOperationResult(
            repo_path=path,
            action=action.value,
            success=False,
            message=f"Error: {str(e)}",
            remote_count=remote_count
        )

    # This should never be reached, but just in case
    return GitOperationResult(
        repo_path=path,
        action=action.value,
        success=False,
        message="Unknown error",
        remote_count=remote_count
    )


def print_git_operations_summary(summary: GitOperationSummary, operations_performed: list[str]) -> None:
    """Print a detailed summary of git operations with rich formatting and tables."""
    from rich.console import Console
    console = Console()

    # Main summary panel
    summary_stats = [
        f"Total paths processed: {summary.total_paths_processed}",
        f"Git repositories found: {summary.git_repos_found}",
        f"Non-git paths skipped: {summary.non_git_paths}"
    ]

    console.print(Panel.fit(
        "\n".join(summary_stats),
        title="[bold blue]📊 Git Operations Summary[/bold blue]",
        border_style="blue"
    ))

    # Statistics panels in columns
    stat_panels = []

    if "commit" in operations_performed:
        commit_stats = [
            f"Attempted: {summary.commits_attempted}",
            f"Successful: {summary.commits_successful}",
            f"No changes: {summary.commits_no_changes}",
            f"Failed: {summary.commits_failed}"
        ]
        stat_panels.append(Panel.fit(
            "\n".join(commit_stats),
            title="[bold green]💾 Commit Operations[/bold green]",
            border_style="green"
        ))

    if "pull" in operations_performed:
        pull_stats = [
            f"Attempted: {summary.pulls_attempted}",
            f"Successful: {summary.pulls_successful}",
            f"Failed: {summary.pulls_failed}"
        ]
        stat_panels.append(Panel.fit(
            "\n".join(pull_stats),
            title="[bold cyan]⬇️ Pull Operations[/bold cyan]",
            border_style="cyan"
        ))

    if "push" in operations_performed:
        push_stats = [
            f"Attempted: {summary.pushes_attempted}",
            f"Successful: {summary.pushes_successful}",
            f"Failed: {summary.pushes_failed}"
        ]
        stat_panels.append(Panel.fit(
            "\n".join(push_stats),
            title="[bold magenta]🚀 Push Operations[/bold magenta]",
            border_style="magenta"
        ))

    if stat_panels:
        console.print(Columns(stat_panels, equal=True, expand=True))

    # Repositories without remotes warning
    if summary.repos_without_remotes:
        repos_table = Table(title="[bold yellow]⚠️ Repositories Without Remotes[/bold yellow]")
        repos_table.add_column("Repository Name", style="cyan", no_wrap=True)
        repos_table.add_column("Full Path", style="dim")

        for repo_path in summary.repos_without_remotes:
            repos_table.add_row(repo_path.name, str(repo_path))

        console.print(repos_table)
        console.print("[yellow]These repositories cannot be pushed to remote servers.[/yellow]")
    elif "push" in operations_performed:
        console.print("[green]✅ All repositories have remote configurations.[/green]")

    # Failed operations table
    if summary.failed_operations:
        failed_table = Table(title=f"[bold red]❌ Failed Operations ({len(summary.failed_operations)} total)[/bold red]")
        failed_table.add_column("Action", style="bold red", no_wrap=True)
        failed_table.add_column("Repository", style="cyan", no_wrap=True)
        failed_table.add_column("Problem", style="red")

        # Group failed operations by type for better organization
        failed_by_action = {}
        for failed_op in summary.failed_operations:
            if failed_op.action not in failed_by_action:
                failed_by_action[failed_op.action] = []
            failed_by_action[failed_op.action].append(failed_op)

        for action, failures in failed_by_action.items():
            for failure in failures:
                repo_name = failure.repo_path.name if failure.is_git_repo else f"{failure.repo_path.name} (not git repo)"
                problem = failure.message if failure.is_git_repo else "Not a git repository"
                failed_table.add_row(action.upper(), repo_name, problem)

        console.print(failed_table)
    else:
        console.print("[green]✅ All git operations completed successfully![/green]")

    # Overall success assessment
    total_failed = len(summary.failed_operations)
    total_operations = (summary.commits_attempted + summary.pulls_attempted +
                       summary.pushes_attempted)

    if total_failed == 0 and total_operations > 0:
        console.print(f"\n[bold green]🎉 SUCCESS: All {total_operations} operations completed successfully![/bold green]")
    elif total_operations == 0:
        console.print("\n[blue]📝 No git operations were performed.[/blue]")
    else:
        success_rate = ((total_operations - total_failed) / total_operations * 100) if total_operations > 0 else 0
        if total_failed > 0:
            console.print(f"\n[bold yellow]⚖️ SUMMARY: {total_operations - total_failed}/{total_operations} operations succeeded ({success_rate:.1f}% success rate)[/bold yellow]")
            console.print("[yellow]Review the failed operations table above for details on what needs attention.[/yellow]")
        else:
            console.print(f"\n[bold green]⚖️ SUMMARY: {total_operations}/{total_operations} operations succeeded (100% success rate)[/bold green]")


def perform_git_operations(repos_root: PathExtended, pull: bool, commit: bool, push: bool, recursive: bool, auto_uv_sync: bool) -> None:
    """Perform git operations on all repositories and provide detailed summary."""
    print(f"\n🔄 Performing Git actions on repositories @ `{repos_root}`...")
    summary = GitOperationSummary()
    operations_performed = []    
    # Determine which operations to perform
    if pull:
        operations_performed.append("pull")
    if commit:
        operations_performed.append("commit")
    if push:
        operations_performed.append("push")
        
    for a_path in repos_root.search("*"):
        print(f"{('Handling ' + str(a_path)).center(80, '-')}")
        summary.total_paths_processed += 1
        
        # Check if this is a git repository first
        from git.exc import InvalidGitRepositoryError
        from git.repo import Repo
        
        try:
            repo = Repo(str(a_path), search_parent_directories=False)
            summary.git_repos_found += 1
            
            # Track repos without remotes
            if len(repo.remotes) == 0:
                summary.repos_without_remotes.append(a_path)
                
            # Now perform the actual operations
            if pull:
                result = git_action(path=a_path, action=GitAction.pull, mess=None, r=recursive, auto_uv_sync=auto_uv_sync)
                summary.pulls_attempted += 1
                if result.success:
                    summary.pulls_successful += 1
                else:
                    summary.pulls_failed += 1
                    summary.failed_operations.append(result)
                    
            if commit:
                result = git_action(a_path, action=GitAction.commit, mess=None, r=recursive, auto_uv_sync=auto_uv_sync)
                summary.commits_attempted += 1
                if result.success:
                    if result.had_changes:
                        summary.commits_successful += 1
                    else:
                        summary.commits_no_changes += 1
                else:
                    summary.commits_failed += 1
                    summary.failed_operations.append(result)
                    
            if push:
                result = git_action(a_path, action=GitAction.push, mess=None, r=recursive, auto_uv_sync=auto_uv_sync)
                summary.pushes_attempted += 1
                if result.success:
                    summary.pushes_successful += 1
                else:
                    summary.pushes_failed += 1
                    summary.failed_operations.append(result)
                    
        except InvalidGitRepositoryError:
            summary.non_git_paths += 1
            pprint(f"⚠️ Skipping {a_path} because it is not a git repository.")

    # Print the detailed summary
    print_git_operations_summary(summary, operations_performed)