from machineconfig.scripts.python.helpers.helpers_repos.action_helper import GitAction, GitOperationResult, GitOperationSummary, print_git_operations_summary
from machineconfig.utils.path_extended import PathExtended
from machineconfig.utils.accessories import randstr
from machineconfig.scripts.python.helpers.helpers_repos.update import update_repository

from typing import Optional, Dict, Any, List, cast
import concurrent.futures
import os

from rich import print as pprint


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
                is_git_repo=False,
            )
        else:
            return GitOperationResult(repo_path=path, action=action.value, success=False, message="Not a git repository", is_git_repo=False)

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
                    remote_count=remote_count,
                )
            else:
                print("ℹ️  No changes to commit")
                return GitOperationResult(
                    repo_path=path, action=action.value, success=True, message="No changes to commit", had_changes=False, remote_count=remote_count
                )

        elif action == GitAction.push:
            if not repo.remotes:
                print("⚠️ No remotes configured for push")
                return GitOperationResult(repo_path=path, action=action.value, success=False, message="No remotes configured", remote_count=0)

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
            return GitOperationResult(repo_path=path, action=action.value, success=success, message=message, remote_count=remote_count)

        elif action == GitAction.pull:
            # Use the enhanced update function with uv sync support
            try:
                update_repository(repo, auto_uv_sync=auto_uv_sync, allow_password_prompt=False)
                print("✅ Pull completed")
                return GitOperationResult(
                    repo_path=path, action=action.value, success=True, message="Pull completed successfully", remote_count=remote_count
                )
            except Exception as e:
                print(f"❌ Pull failed: {e}")
                return GitOperationResult(
                    repo_path=path, action=action.value, success=False, message=f"Pull failed: {str(e)}", remote_count=remote_count
                )

    except Exception as e:
        print(f"❌ Error performing {action} on {path}: {e}")
        return GitOperationResult(repo_path=path, action=action.value, success=False, message=f"Error: {str(e)}", remote_count=remote_count)

    # This should never be reached, but just in case
    return GitOperationResult(repo_path=path, action=action.value, success=False, message="Unknown error", remote_count=remote_count)


def perform_git_operations(repos_root: PathExtended, pull: bool, commit: bool, push: bool, recursive: bool, auto_uv_sync: bool) -> None:
    """Perform git operations on all repositories and provide detailed summary."""
    print(f"\n🔄 Performing Git actions on repositories @ `{repos_root}`...")
    summary = GitOperationSummary()
    # Keep track of which operations we are performing
    operations_performed: List[str] = []
    if pull:
        operations_performed.append("pull")
    if commit:
        operations_performed.append("commit")
    if push:
        operations_performed.append("push")

    # Collect all candidate paths first
    paths = list(repos_root.glob("*"))

    def _process_path(a_path: PathExtended) -> Dict[str, Any]:
        """Worker that processes a single path and returns metadata and results."""
        from git.exc import InvalidGitRepositoryError
        from git.repo import Repo

        result_payload: Dict[str, Any] = {"path": a_path, "is_git": False, "results": [], "repo_remotes_count": 0}
        print(f"{('Handling ' + str(a_path)).center(80, '-')}")

        try:
            repo = Repo(str(a_path), search_parent_directories=False)
        except InvalidGitRepositoryError:
            result_payload["non_git"] = True
            pprint(f"⚠️ Skipping {a_path} because it is not a git repository.")
            return result_payload

        # It's a git repo
        result_payload["is_git"] = True
        result_payload["repo_remotes_count"] = len(repo.remotes)

        # Perform configured operations sequentially for this repo (the repo-level work is done concurrently between repos)
        try:
            if pull:
                r = git_action(path=a_path, action=GitAction.pull, mess=None, r=recursive, auto_uv_sync=auto_uv_sync)
                result_payload["results"].append(r)
            if commit:
                r = git_action(path=a_path, action=GitAction.commit, mess=None, r=recursive, auto_uv_sync=auto_uv_sync)
                result_payload["results"].append(r)
            if push:
                r = git_action(path=a_path, action=GitAction.push, mess=None, r=recursive, auto_uv_sync=auto_uv_sync)
                result_payload["results"].append(r)
        except Exception as e:
            # Capture any unexpected exception for this path
            pprint(f"❌ Error processing {a_path}: {e}")

        return result_payload

    # Choose a reasonable number of workers
    max_workers = min(32, (os.cpu_count() or 1) * 5, len(paths) or 1)

    # Run the workers in parallel and aggregate results
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as exc:
        future_to_path = {exc.submit(_process_path, p): p for p in paths}
        for fut in concurrent.futures.as_completed(future_to_path):
            payload = fut.result()
            a_path = cast(PathExtended, payload.get("path"))
            summary.total_paths_processed += 1

            if not payload.get("is_git"):
                summary.non_git_paths += 1
                continue

            # git repo found
            summary.git_repos_found += 1
            if payload.get("repo_remotes_count", 0) == 0:
                summary.repos_without_remotes.append(a_path)

            for r in payload.get("results", []):
                action_name = r.action if hasattr(r, "action") else ""
                # Pull
                if action_name == "pull":
                    summary.pulls_attempted += 1
                    if r.success:
                        summary.pulls_successful += 1
                    else:
                        summary.pulls_failed += 1
                        summary.failed_operations.append(r)
                # Commit
                elif action_name == "commit":
                    summary.commits_attempted += 1
                    if r.success:
                        if getattr(r, "had_changes", False):
                            summary.commits_successful += 1
                        else:
                            summary.commits_no_changes += 1
                    else:
                        summary.commits_failed += 1
                        summary.failed_operations.append(r)
                # Push
                elif action_name == "push":
                    summary.pushes_attempted += 1
                    if r.success:
                        summary.pushes_successful += 1
                    else:
                        summary.pushes_failed += 1
                        summary.failed_operations.append(r)

    # Print the detailed summary
    print_git_operations_summary(summary, operations_performed)
