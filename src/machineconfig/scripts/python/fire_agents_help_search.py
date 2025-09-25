from machineconfig.utils.source_of_truth import EXCLUDE_DIRS
import fnmatch
from pathlib import Path


def search_files_by_pattern(repo_root: Path, pattern: str) -> list[Path]:
    """Return all files under repo_root whose filename matches the given pattern.

    Notes:
      - Uses glob-style pattern matching (e.g., "*.py", "*test*", "config.*")
      - Skips any paths that reside under directories listed in EXCLUDE_DIRS at any depth.
    """
    matches: list[Path] = []

    def _should_skip_dir(dir_path: Path) -> bool:
        """Check if directory should be skipped based on EXCLUDE_DIRS."""
        return any(part in EXCLUDE_DIRS for part in dir_path.parts)

    def _walk_and_filter(current_path: Path) -> None:
        """Recursively walk directories, filtering out excluded ones early."""
        try:
            if not current_path.is_dir():
                return

            # Skip if current directory is in exclude list
            if _should_skip_dir(current_path):
                return

            for item in current_path.iterdir():
                if item.is_dir():
                    _walk_and_filter(item)
                elif item.is_file() and fnmatch.fnmatch(item.name, pattern):
                    matches.append(item)
        except (OSError, PermissionError):
            # Skip directories we can't read
            return

    _walk_and_filter(repo_root)
    return matches


def search_python_files(repo_root: Path, keyword: str) -> list[Path]:
    """Return all Python files under repo_root whose text contains keyword.

    Notes:
      - Skips any paths that reside under directories listed in EXCLUDE_DIRS at any depth.
      - Errors reading individual files are ignored (decoded with 'ignore').
    """
    keyword_lower = keyword.lower()
    matches: list[Path] = []

    def _should_skip_dir(dir_path: Path) -> bool:
        """Check if directory should be skipped based on EXCLUDE_DIRS."""
        return any(part in EXCLUDE_DIRS for part in dir_path.parts)

    def _walk_and_filter(current_path: Path) -> None:
        """Recursively walk directories, filtering out excluded ones early."""
        try:
            if not current_path.is_dir():
                return

            # Skip if current directory is in exclude list
            if _should_skip_dir(current_path):
                return

            for item in current_path.iterdir():
                if item.is_dir():
                    _walk_and_filter(item)
                elif item.is_file() and item.suffix == ".py":
                    try:
                        if keyword_lower in item.read_text(encoding="utf-8", errors="ignore").lower():
                            matches.append(item)
                    except OSError:
                        # Skip unreadable file
                        continue
        except (OSError, PermissionError):
            # Skip directories we can't read
            return

    _walk_and_filter(repo_root)
    return matches
