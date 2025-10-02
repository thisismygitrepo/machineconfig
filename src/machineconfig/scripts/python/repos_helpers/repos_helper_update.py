from pathlib import Path
from typing import TypedDict
import subprocess
import git


class RepositoryUpdateResult(TypedDict):
    """Result of updating a single repository."""

    repo_path: str
    status: str  # "success", "error", "skipped", "auth_failed"
    had_uncommitted_changes: bool
    uncommitted_files: list[str]
    commit_before: str
    commit_after: str
    commits_changed: bool
    pyproject_changed: bool
    dependencies_changed: bool
    uv_sync_ran: bool
    uv_sync_success: bool
    remotes_processed: list[str]
    remotes_skipped: list[str]
    error_message: str | None
    is_machineconfig_repo: bool
    permissions_updated: bool


def set_permissions_recursive(path: Path, executable: bool = True) -> None:
    """Set permissions recursively for a directory."""
    if not path.exists():
        return
    if path.is_file():
        if executable:
            path.chmod(0o755)
        else:
            path.chmod(0o644)
    elif path.is_dir():
        path.chmod(0o755)
        for item in path.rglob("*"):
            set_permissions_recursive(item, executable)


def run_uv_sync(repo_path: Path) -> bool:
    """Run uv sync in the given repository path. Returns True if successful."""
    try:
        print(f"🔄 Running uv sync in {repo_path}")
        # Run uv sync with output directly to terminal (no capture)
        subprocess.run(["uv", "sync"], cwd=repo_path, check=True)
        print("✅ uv sync completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ uv sync failed with return code {e.returncode}")
        return False
    except FileNotFoundError:
        print("⚠️  uv command not found. Please install uv first.")
        return False


def get_file_hash(file_path: Path) -> str | None:
    """Get SHA256 hash of a file, return None if file doesn't exist."""
    if not file_path.exists():
        return None
    import hashlib

    return hashlib.sha256(file_path.read_bytes()).hexdigest()


def update_repository(repo: git.Repo, auto_sync: bool, allow_password_prompt: bool) -> RepositoryUpdateResult:
    """Update a single repository and return detailed information about what happened."""
    repo_path = Path(repo.working_dir)
    print(f"🔄 {'Updating ' + str(repo_path):.^80}")

    # Initialize result dict
    result: RepositoryUpdateResult = {
        "repo_path": str(repo_path),
        "status": "success",
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
        "error_message": None,
        "is_machineconfig_repo": "machineconfig" in str(repo_path),
        "permissions_updated": False,
    }

    # Check git status first
    print("📊 Checking git status...")
    if repo.is_dirty():
        # Get the list of modified files
        changed_files_raw = [item.a_path for item in repo.index.diff(None)]
        changed_files_raw.extend([item.a_path for item in repo.index.diff("HEAD")])
        # Filter out None values and remove duplicates
        changed_files = list(set(file for file in changed_files_raw if file is not None))

        result["had_uncommitted_changes"] = True
        result["uncommitted_files"] = changed_files
        print(f"⚠️  Repository has uncommitted changes: {', '.join(changed_files)}")

        # Repository has uncommitted changes - cannot update
        result["status"] = "error"
        result["error_message"] = f"Cannot update repository - there are pending changes in: {', '.join(changed_files)}. Please commit or stash your changes first."
        raise RuntimeError(result["error_message"])
    else:
        print("✅ Repository is clean")

    # Check if this repo has pyproject.toml
    pyproject_path = repo_path / "pyproject.toml"

    # Get hashes before pull
    pyproject_hash_before = get_file_hash(pyproject_path)

    # Get current commit hash before pull
    result["commit_before"] = repo.head.commit.hexsha

    try:
        # Use subprocess for git pull to get better output control

        # Get list of remotes
        remotes = list(repo.remotes)
        if not remotes:
            print("⚠️  No remotes configured for this repository")
            result["status"] = "skipped"
            result["error_message"] = "No remotes configured for this repository"
            return result

        for remote in remotes:
            try:
                print(f"📥 Fetching from {remote.name}...")

                # Set up environment for git commands
                env = None
                if not allow_password_prompt:
                    # Disable interactive prompts
                    import os

                    env = os.environ.copy()
                    env["GIT_TERMINAL_PROMPT"] = "0"
                    env["GIT_ASKPASS"] = "echo"  # Returns empty string for any credential request

                # First fetch to see what's available
                fetch_result = subprocess.run(
                    ["git", "fetch", remote.name, "--verbose"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=30,  # Add timeout to prevent hanging
                )

                # Check if fetch failed due to authentication
                if fetch_result.returncode != 0 and not allow_password_prompt:
                    auth_error_indicators = [
                        "Authentication failed",
                        "Password for",
                        "Username for",
                        "could not read Username",
                        "could not read Password",
                        "fatal: Authentication failed",
                        "fatal: could not read Username",
                        "fatal: could not read Password",
                    ]

                    error_output = (fetch_result.stderr or "") + (fetch_result.stdout or "")
                    if any(indicator in error_output for indicator in auth_error_indicators):
                        print(f"⚠️  Skipping {remote.name} - authentication required but password prompts are disabled")
                        continue

                if fetch_result.stdout:
                    print(f"📡 Fetch output: {fetch_result.stdout.strip()}")
                if fetch_result.stderr:
                    print(f"📡 Fetch info: {fetch_result.stderr.strip()}")

                # Now pull with verbose output
                print(f"📥 Pulling from {remote.name}/{repo.active_branch.name}...")
                pull_result = subprocess.run(["git", "pull", remote.name, repo.active_branch.name, "--verbose"], cwd=repo_path, capture_output=True, text=True, env=env, timeout=30)

                # Check if pull failed due to authentication
                if pull_result.returncode != 0 and not allow_password_prompt:
                    auth_error_indicators = [
                        "Authentication failed",
                        "Password for",
                        "Username for",
                        "could not read Username",
                        "could not read Password",
                        "fatal: Authentication failed",
                        "fatal: could not read Username",
                        "fatal: could not read Password",
                    ]

                    error_output = (pull_result.stderr or "") + (pull_result.stdout or "")
                    if any(indicator in error_output for indicator in auth_error_indicators):
                        print(f"⚠️  Skipping pull from {remote.name} - authentication required but password prompts are disabled")
                        continue

                if pull_result.stdout:
                    print(f"📦 Pull output: {pull_result.stdout.strip()}")
                if pull_result.stderr:
                    print(f"📦 Pull info: {pull_result.stderr.strip()}")

                # Check if pull was successful
                if pull_result.returncode == 0:
                    result["remotes_processed"].append(remote.name)
                    # Check if commits changed
                    result["commit_after"] = repo.head.commit.hexsha
                    if result["commit_before"] != result["commit_after"]:
                        result["commits_changed"] = True
                        print(f"✅ Repository updated: {result['commit_before'][:8]} → {result['commit_after'][:8]}")
                    else:
                        print("✅ Already up to date")
                else:
                    result["remotes_skipped"].append(remote.name)
                    print(f"❌ Pull failed with return code {pull_result.returncode}")

            except Exception as e:
                result["remotes_skipped"].append(remote.name)
                print(f"⚠️  Failed to pull from {remote.name}: {e}")
                continue

        # Check if pyproject.toml changed after pull
        pyproject_hash_after = get_file_hash(pyproject_path)

        if pyproject_hash_before != pyproject_hash_after:
            print("📋 pyproject.toml has changed")
            result["pyproject_changed"] = True
            result["dependencies_changed"] = True

        # Special handling for machineconfig repository
        if result["is_machineconfig_repo"]:
            print("🛠  Special handling for machineconfig repository...")
            scripts_path = Path.home() / "scripts"
            if scripts_path.exists():
                set_permissions_recursive(scripts_path)
                result["permissions_updated"] = True
                print(f"✅ Set permissions for {scripts_path}")

            linux_jobs_path = repo_path / "src" / "machineconfig" / "jobs" / "linux"
            if linux_jobs_path.exists():
                set_permissions_recursive(linux_jobs_path)
                result["permissions_updated"] = True
                print(f"✅ Set permissions for {linux_jobs_path}")

            lf_exe_path = repo_path / "src" / "machineconfig" / "settings" / "lf" / "linux" / "exe"
            if lf_exe_path.exists():
                set_permissions_recursive(lf_exe_path)
                result["permissions_updated"] = True
                print(f"✅ Set permissions for {lf_exe_path}")

        # Run uv sync if dependencies changed and auto_sync is enabled
        if result["dependencies_changed"] and auto_sync:
            result["uv_sync_ran"] = True
            result["uv_sync_success"] = run_uv_sync(repo_path)

        return result

    except Exception as e:
        result["status"] = "error"
        result["error_message"] = str(e)
        print(f"❌ Error updating repository {repo_path}: {e}")
        return result
