#!/usr/bin/env python3
"""Script to generate a markdown table with checkboxes for all Python and shell files in the repo."""

from pathlib import Path
from typing import Annotated
from rich.console import Console
from rich.panel import Panel
import typer


def get_python_files(repo_root: Path, exclude_init: bool = False) -> list[str]:
    """Get all Python files relative to repo root."""
    excluded_parts = {".venv", "__pycache__", ".git", "build", "dist"}
    excluded_patterns = {"*.egg-info"}

    # Get all .py files recursively
    py_files = list(repo_root.glob("**/*.py"))

    # Filter out files in excluded directories
    filtered_files = []
    for file_path in py_files:
        relative_path = file_path.relative_to(repo_root)
        path_parts = relative_path.parts

        # Skip files in excluded directories
        if any(part in excluded_parts for part in path_parts):
            continue

        # Skip files matching excluded patterns
        if any(file_path.match(f"**/{pattern}/**") for pattern in excluded_patterns):
            continue

        # Skip __init__.py files if requested
        if exclude_init and file_path.name == "__init__.py":
            continue

        filtered_files.append(str(relative_path))

    return sorted(filtered_files)


def get_shell_files(repo_root: Path) -> list[str]:
    """Get all shell script files relative to repo root."""
    excluded_parts = {".venv", "__pycache__", ".git", "build", "dist"}
    excluded_patterns = {"*.egg-info"}

    # Get all .sh files recursively
    sh_files = list(repo_root.glob("**/*.sh"))

    # Filter out files in excluded directories
    filtered_files = []
    for file_path in sh_files:
        relative_path = file_path.relative_to(repo_root)
        path_parts = relative_path.parts

        # Skip files in excluded directories
        if any(part in excluded_parts for part in path_parts):
            continue

        # Skip files matching excluded patterns
        if any(file_path.match(f"**/{pattern}/**") for pattern in excluded_patterns):
            continue

        filtered_files.append(str(relative_path))

    return sorted(filtered_files)


def generate_markdown_table(python_files: list[str], shell_files: list[str]) -> str:
    """Generate markdown table with checkboxes."""
    header = "# File Checklist\n\n"

    content = ""

    if python_files:
        content += "## Python Files\n\n"
        content += "| Index | File Path | Status |\n|-------|-----------|--------|\n"
        for index, file_path in enumerate(python_files, start=1):
            clean_path = file_path.lstrip("./")
            content += f"| {index} | {clean_path} | - [ ] |\n"

    if shell_files:
        content += "\n## Shell Script Files\n\n"
        content += "| Index | File Path | Status |\n|-------|-----------|--------|\n"
        for index, file_path in enumerate(shell_files, start=1):
            clean_path = file_path.lstrip("./")
            content += f"| {index} | {clean_path} | - [ ] |\n"

    return header + content


def create_repo_symlinks(repo_root: Path) -> None:
    """Create 5 symlinks to repo_root at ~/code_copies/${repo_name}_copy_{i}."""
    repo_name: str = repo_root.name
    symlink_dir: Path = Path.home() / "code_copies"
    symlink_dir.mkdir(exist_ok=True)
    for i in range(1, 6):
        symlink_path: Path = symlink_dir / f"{repo_name}_copy_{i}"
        if symlink_path.exists() or symlink_path.is_symlink():
            symlink_path.unlink()
        symlink_path.symlink_to(repo_root, target_is_directory=True)


def main(
    repo: Annotated[str, typer.Argument(help="Repository root path. Defaults to current working directory.")] = str(Path.cwd()),
    exclude_init: Annotated[bool, typer.Option("--exclude-init", help="Exclude __init__.py files from the checklist")] = False,
    create_symlinks: Annotated[bool, typer.Option("--symlinks", help="Create 5 symlinks to repo in ~/code_copies/")] = False,
) -> None:
    """Generate markdown checklist with all Python and shell script files in the repository."""
    repo_root = Path(repo).expanduser().absolute()

    if not repo_root.joinpath("pyproject.toml").exists():
        console = Console()
        console.print(Panel(f"❌ ERROR | Not a repository root: {repo_root}", border_style="bold red", expand=False))
        raise typer.Exit(code=1)

    output_file = repo_root / ".ai" / "all_files_with_index.md"

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Get Python and shell files
    python_files = get_python_files(repo_root, exclude_init=exclude_init)
    shell_files = get_shell_files(repo_root)

    print(f"Repo root: {repo_root}")
    print(f"Found {len(python_files)} Python files")
    print(f"Found {len(shell_files)} Shell script files")

    # Generate markdown
    markdown_content = generate_markdown_table(python_files, shell_files)

    # Write to file
    output_file.write_text(markdown_content)

    # Create symlinks if requested
    if create_symlinks:
        create_repo_symlinks(repo_root)
        print("✅ Created 5 symlinks in ~/code_copies/")

    console = Console()
    console.print(Panel(f"""✅ SUCCESS | Markdown checklist generated successfully!
📄 File Location: {output_file}
🐍 Python files: {len(python_files)}
🔧 Shell files: {len(shell_files)}""", border_style="bold blue", expand=False))


if __name__ == "__main__":
    typer.run(main)
