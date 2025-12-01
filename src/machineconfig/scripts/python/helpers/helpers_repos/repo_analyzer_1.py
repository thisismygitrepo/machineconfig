

import subprocess

from git import Repo
from collections import defaultdict
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
from pathlib import Path



def count_historical_line_edits(repo_path: str) -> int:

    repo = Repo(repo_path)
    last_commit = next(repo.iter_commits())
    total_lines, total_files = count_python_lines(last_commit)
    print(f"Total lines of Python code in latest commit ({last_commit.hexsha[:8]}): {total_lines} across {total_files} files")

    gitcs_viz(repo_path=repo_path, pull_full_history=True)

    file_line_counts: "Dict[str, int]" = defaultdict(int)
    total_commits: int = sum(1 for _ in repo.iter_commits())
    print(f"Total commits to process: {total_commits}")
    for i, commit in enumerate(repo.iter_commits(), 1):
        if i % 100 == 0 or i == total_commits:
            print(f"Processing commit {i}/{total_commits} ({i / total_commits:.1%})")
        try:
            # Handle initial commits that have no parents
            if not commit.parents:
                # For initial commit, count all lines in Python files
                for file in commit.stats.files:
                    if str(file).endswith(".py"):
                        file_line_counts[str(file)] += commit.stats.files[file]["insertions"]
            else:
                # For commits with parents, use stats
                for file in commit.stats.files:
                    if str(file).endswith(".py"):
                        file_line_counts[str(file)] += commit.stats.files[file]["insertions"]
        except Exception:
            # If stats fail (e.g., corrupted parent), skip this commit
            print(f"Warning: Could not get stats for commit {commit.hexsha[:8]}, skipping")
            continue

    print(f"\nProcessed files: {len(file_line_counts)}")
    res = sum(file_line_counts.values())
    print(f"Total historical lines of Python code: {res}")
    return res




def count_lines_changed_in_commit(commit: "Any") -> int:
    _total_lines = 0
    for _file in commit.stats.files:
        if str(_file).endswith(".py"):
            _blob = commit.tree / _file
            _total_lines += len(_blob.data_stream.read().decode("utf-8").splitlines())
    return _total_lines
def count_python_lines(commit: "Any") -> tuple[int, int]:
    """Count total lines in Python files for a specific commit"""
    total_lines = 0
    total_files = 0
    try:
        for blob in commit.tree.traverse():
            if blob.path.endswith(".py"):
                try:
                    content = blob.data_stream.read().decode("utf-8")
                    total_lines += len(content.splitlines())
                    total_files += 1
                except Exception as _e:
                    continue
    except Exception as e:
        print(f"Error traversing commit {commit.hexsha[:8]}: {e}")
        pass
    return total_lines, total_files


def get_default_branch(repo: Repo) -> str:
    """Get the default branch name of the repository"""
    try:
        _ = repo.refs["main"]
        return "main"  # First try 'main'
    except IndexError:
        try:
            _ = repo.refs["master"]
            return "master"  # Then try 'master'
        except IndexError:
            return repo.head.reference.name  # If neither exists, get the branch the HEAD is pointing to



def gitcs_viz(repo_path: Union[str, Path], email: Optional[str] = None, pull_full_history: bool = False) -> None:
    """Invoke the gitcs CLI across 6-month windows covering the repo history.
    
    Args:
        repo_path: Path to the git repository
        email: Optional email filter for gitcs
        pull_full_history: If True, unshallow the repo to fetch full history (useful for shallow clones)
    """
    from machineconfig.utils.installer_utils.installer_cli import install_if_missing
    install_if_missing("gitcs")

    repo_path = Path(repo_path).expanduser().resolve()
    repo = Repo(repo_path)
    
    # Check if repo is shallow and optionally unshallow it
    if pull_full_history:
        shallow_file = Path(repo.git_dir) / "shallow"
        if shallow_file.exists():
            print("🔄 Detected shallow clone. Fetching full history...")
            try:
                repo.git.fetch("--unshallow")
                print("✅ Successfully fetched full history")
            except Exception as e:
                print(f"⚠️ Failed to unshallow repository: {e}")
                print("Continuing with available history...")
        else:
            print("ℹ️ Repository already has full history")
    
    branch_name = get_default_branch(repo)
    commits: "List[Any]" = list(repo.iter_commits(branch_name))
    if not commits:
        print("⚠️ No commits found; skipping gitcs visualization.")
        return

    from datetime import timezone

    commit_dates = [datetime.fromtimestamp(commit.committed_date, tz=timezone.utc).date() for commit in commits]
    min_year = min(commit_dates).year
    max_year = max(commit_dates).year

    print(f"📆 gitcs windows: {min_year}-01-01 → {max_year}-12-31 (fixed half-year slices)")

    chunk_idx = 1
    for year in range(min_year, max_year + 1):
        windows = [(date(year, 1, 1), date(year, 6, 30)), (date(year, 7, 1), date(year, 12, 31))]
        for chunk_start, chunk_end in windows:
            cmd = ["gitcs", "--since", chunk_start.isoformat(), "--until", chunk_end.isoformat()]
            if email:
                cmd.extend(["--email", email])

            print(f"\n===== gitcs chunk {chunk_idx}: {chunk_start.isoformat()} → {chunk_end.isoformat()} =====")
            try:
                completed = subprocess.run(cmd, cwd=str(repo_path), capture_output=True, text=True, input=f"{repo_path}\n")
            except FileNotFoundError:
                print("❌ gitcs CLI is not available on PATH; aborting visualization.")
                return

            if completed.stdout.strip():
                print(completed.stdout.strip())
            if completed.stderr.strip():
                print(completed.stderr.strip())
            if completed.returncode != 0:
                print(f"⚠️ gitcs exited with code {completed.returncode} for this range.")

            chunk_idx += 1



