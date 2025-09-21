#!/usr/bin/env python3
"""Script to generate a markdown table with checkboxes for all Python files in the repo."""

from pathlib import Path


def get_python_files(repo_root: Path) -> list[str]:
    """Get all Python files relative to repo root."""
    # Get all .py files recursively
    py_files = list(repo_root.glob("**/*.py"))

    # Filter out files in .venv and __pycache__ directories
    filtered_files = []
    for file_path in py_files:
        relative_path = file_path.relative_to(repo_root)
        path_parts = relative_path.parts

        # Skip files in .venv or __pycache__ directories
        if any(part in {".venv", "__pycache__"} for part in path_parts):
            continue

        filtered_files.append(str(relative_path))

    return sorted(filtered_files)


def generate_markdown_table(files: list[str]) -> str:
    """Generate markdown table with checkboxes."""
    header = "# Python Files Checklist\n\n"
    table = "| Index | File Path | Status |\n|-------|-----------|--------|\n"

    for index, file_path in enumerate(files, start=1):
        # Remove leading ./ if present
        clean_path = file_path.lstrip("./")
        table += f"| {index} | {clean_path} | - [ ] |\n"

    return header + table


def main() -> None:
    """Main function."""
    repo_root = Path.cwd()
    if not repo_root.joinpath("pyproject.toml").exists():
        raise RuntimeError(f" {repo_root} Not a repo root")
    output_file = repo_root / ".ai" / "all_files_with_index.md"

    print(f"Repo root: {repo_root}")
    print(f"Output file: {output_file}")

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Get Python files
    python_files = get_python_files(repo_root)
    print(f"Found {len(python_files)} Python files")

    # Generate markdown
    markdown_content = generate_markdown_table(python_files)
    print(f"Generated markdown content length: {len(markdown_content)}")

    # Write to file
    output_file.write_text(markdown_content)
    print(f"Generated {output_file} with {len(python_files)} Python files")

    # Create 5 symlinks to repo_root at ~/code_copies/${repo_name}_copy_{i}
    import pathlib

    # import os
    repo_root = pathlib.Path.cwd().resolve()
    repo_name: str = pathlib.Path(repo_root).name
    symlink_dir: pathlib.Path = pathlib.Path.home() / "code_copies"
    symlink_dir.mkdir(exist_ok=True)
    for i in range(1, 6):
        symlink_path: pathlib.Path = symlink_dir / f"{repo_name}_copy_{i}"
        if symlink_path.exists() or symlink_path.is_symlink():
            symlink_path.unlink()
        symlink_path.symlink_to(repo_root, target_is_directory=True)
    # Windows equivalent (comment):
    # for /l %i in (1,1,5) do mklink /D "%USERPROFILE%\code_copies\{repo_name}_copy_%i" "C:\path\to\repo_root"


if __name__ == "__main__":
    main()
