from machineconfig.utils.path_extended import PathExtended as PathExtended
from machineconfig.utils.accessories import randstr
from machineconfig.scripts.python.repos_helper_update import update_repository

from typing import Optional
from dataclasses import dataclass
from enum import Enum

from rich import print as pprint


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


def git_action(path: PathExtended, action: GitAction, mess: Optional[str] = None, r: bool = False, auto_sync: bool = True) -> GitOperationResult:
    """Perform git actions using Python instead of shell scripts. Returns detailed operation result."""
    from git.exc import InvalidGitRepositoryError
    from git.repo import Repo

    try:
        repo = Repo(str(path), search_parent_directories=False)
    except InvalidGitRepositoryError:
        pprint(f"⚠️ Skipping {path} because it is not a git repository.")
        if r:
            results = [git_action(path=sub_path, action=action, mess=mess, r=r, auto_sync=auto_sync) for sub_path in path.search()]
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
                update_repository(repo, auto_sync=auto_sync, allow_password_prompt=False)
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
    """Print a detailed summary of git operations similar to repos_helper_record.py."""
    print("\n📊 Git Operations Summary:")
    print(f"   Total paths processed: {summary.total_paths_processed}")
    print(f"   Git repositories found: {summary.git_repos_found}")
    print(f"   Non-git paths skipped: {summary.non_git_paths}")
    
    # Show per-operation statistics
    if "commit" in operations_performed:
        print("\n💾 Commit Operations:")
        print(f"   Attempted: {summary.commits_attempted}")
        print(f"   Successful: {summary.commits_successful}")
        print(f"   No changes: {summary.commits_no_changes}")
        print(f"   Failed: {summary.commits_failed}")
        
    if "pull" in operations_performed:
        print("\n⬇️ Pull Operations:")
        print(f"   Attempted: {summary.pulls_attempted}")
        print(f"   Successful: {summary.pulls_successful}")
        print(f"   Failed: {summary.pulls_failed}")
        
    if "push" in operations_performed:
        print("\n🚀 Push Operations:")
        print(f"   Attempted: {summary.pushes_attempted}")
        print(f"   Successful: {summary.pushes_successful}")
        print(f"   Failed: {summary.pushes_failed}")

    # Show repositories without remotes (important for push operations)
    if summary.repos_without_remotes:
        print(f"\n⚠️  WARNING: {len(summary.repos_without_remotes)} repositories have no remote configurations:")
        for repo_path in summary.repos_without_remotes:
            print(f"   • {repo_path.name} ({repo_path})")
        print("   These repositories cannot be pushed to remote servers.")
    else:
        if "push" in operations_performed:
            print("\n✅ All repositories have remote configurations.")

    # Show failed operations
    if summary.failed_operations:
        print(f"\n❌ FAILED OPERATIONS ({len(summary.failed_operations)} total):")
        
        # Group failed operations by type
        failed_by_action = {}
        for failed_op in summary.failed_operations:
            if failed_op.action not in failed_by_action:
                failed_by_action[failed_op.action] = []
            failed_by_action[failed_op.action].append(failed_op)
            
        for action, failures in failed_by_action.items():
            print(f"\n   {action.upper()} failures ({len(failures)}):")
            for failure in failures:
                if not failure.is_git_repo:
                    print(f"   • {failure.repo_path.name} ({failure.repo_path}) - Not a git repository")
                else:
                    print(f"   • {failure.repo_path.name} ({failure.repo_path}) - {failure.message}")
    else:
        print("\n✅ All git operations completed successfully!")

    # Overall success assessment
    total_failed = len(summary.failed_operations)
    total_operations = (summary.commits_attempted + summary.pulls_attempted + 
                       summary.pushes_attempted)
    
    if total_failed == 0 and total_operations > 0:
        print(f"\n🎉 SUCCESS: All {total_operations} operations completed successfully!")
    elif total_operations == 0:
        print("\n📝 No git operations were performed.")
    else:
        success_rate = ((total_operations - total_failed) / total_operations * 100) if total_operations > 0 else 0
        print(f"\n⚖️  SUMMARY: {total_operations - total_failed}/{total_operations} operations succeeded ({success_rate:.1f}% success rate)")
        if total_failed > 0:
            print("   Review the failed operations above for details on what needs attention.")


def perform_git_operations(repos_root: PathExtended, pull: bool, commit: bool, push: bool, recursive: bool, auto_sync: bool) -> None:
    """Perform git operations on all repositories and provide detailed summary."""
    print(f"\n🔄 Performing Git actions on repositories @ `{repos_root}`...")
    
    # Initialize summary tracking
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
                result = git_action(path=a_path, action=GitAction.pull, r=recursive, auto_sync=auto_sync)
                summary.pulls_attempted += 1
                if result.success:
                    summary.pulls_successful += 1
                else:
                    summary.pulls_failed += 1
                    summary.failed_operations.append(result)
                    
            if commit:
                result = git_action(a_path, action=GitAction.commit, r=recursive, auto_sync=auto_sync)
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
                result = git_action(a_path, action=GitAction.push, r=recursive, auto_sync=auto_sync)
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