from enum import Enum
from machineconfig.utils.path_extended import PathExtended


from dataclasses import dataclass

from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table


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


class GitAction(Enum):
    commit = "commit"
    push = "push"
    pull = "pull"


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


def print_git_operations_summary(summary: GitOperationSummary, operations_performed: list[str]) -> None:
    """Print a detailed summary of git operations with rich formatting and tables."""
    from rich.console import Console

    console = Console()

    # Main summary panel
    summary_stats = [
        f"Total paths processed: {summary.total_paths_processed}",
        f"Git repositories found: {summary.git_repos_found}",
        f"Non-git paths skipped: {summary.non_git_paths}",
    ]

    console.print(Panel.fit("\n".join(summary_stats), title="[bold blue]📊 Git Operations Summary[/bold blue]", border_style="blue"))

    # Statistics panels in columns
    stat_panels = []

    if "commit" in operations_performed:
        commit_stats = [
            f"Attempted: {summary.commits_attempted}",
            f"Successful: {summary.commits_successful}",
            f"No changes: {summary.commits_no_changes}",
            f"Failed: {summary.commits_failed}",
        ]
        stat_panels.append(Panel.fit("\n".join(commit_stats), title="[bold green]💾 Commit Operations[/bold green]", border_style="green"))

    if "pull" in operations_performed:
        pull_stats = [f"Attempted: {summary.pulls_attempted}", f"Successful: {summary.pulls_successful}", f"Failed: {summary.pulls_failed}"]
        stat_panels.append(Panel.fit("\n".join(pull_stats), title="[bold cyan]⬇️ Pull Operations[/bold cyan]", border_style="cyan"))

    if "push" in operations_performed:
        push_stats = [f"Attempted: {summary.pushes_attempted}", f"Successful: {summary.pushes_successful}", f"Failed: {summary.pushes_failed}"]
        stat_panels.append(Panel.fit("\n".join(push_stats), title="[bold magenta]🚀 Push Operations[/bold magenta]", border_style="magenta"))

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
    total_operations = summary.commits_attempted + summary.pulls_attempted + summary.pushes_attempted

    if total_failed == 0 and total_operations > 0:
        console.print(f"\n[bold green]🎉 SUCCESS: All {total_operations} operations completed successfully![/bold green]")
    elif total_operations == 0:
        console.print("\n[blue]📝 No git operations were performed.[/blue]")
    else:
        success_rate = ((total_operations - total_failed) / total_operations * 100) if total_operations > 0 else 0
        if total_failed > 0:
            console.print(
                f"\n[bold yellow]⚖️ SUMMARY: {total_operations - total_failed}/{total_operations} operations succeeded ({success_rate:.1f}% success rate)[/bold yellow]"
            )
            console.print("[yellow]Review the failed operations table above for details on what needs attention.[/yellow]")
        else:
            console.print(f"\n[bold green]⚖️ SUMMARY: {total_operations}/{total_operations} operations succeeded (100% success rate)[/bold green]")