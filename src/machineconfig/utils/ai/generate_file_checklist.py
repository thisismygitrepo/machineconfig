#!/usr/bin/env python

from pathlib import Path
from typing import List, Optional, Union
from rich.console import Console
from rich.panel import Panel


def generate_file_checklist(repo_root: Union[str, Path], exclude_dirs: Optional[List[str]] = None) -> Path:
    actual_exclude_dirs: List[str] = [".venv", ".git", "__pycache__", "build", "dist", "*.egg-info"]
    if exclude_dirs is not None:
        actual_exclude_dirs = exclude_dirs
    repo_root = Path(repo_root).expanduser().absolute()
    output_path: Path = repo_root / ".ai" / "repo_task" / "file_checklist.md"
    py_files: List[Path] = []
    for filepath in repo_root.glob("**/*.py"):
        if any(excl in filepath.parts for excl in actual_exclude_dirs) or any(filepath.match(f"**/{excl}/**") for excl in actual_exclude_dirs) or filepath.name == "__init__.py":
            continue
        py_files.append(filepath.relative_to(repo_root))

    sh_files: List[Path] = []
    for filepath in repo_root.glob("**/*.sh"):
        if any(excl in filepath.parts for excl in actual_exclude_dirs) or any(filepath.match(f"**/{excl}/**") for excl in actual_exclude_dirs):
            continue
        sh_files.append(filepath.relative_to(repo_root))

    py_files.sort()
    sh_files.sort()

    markdown_content: str = "# File Checklist\n\n"

    markdown_content += "## Python Files\n\n"
    for py_file in py_files:
        markdown_content += f"- [ ] {py_file}\n"

    markdown_content += "\n## Shell Script Files\n\n"
    for sh_file in sh_files:
        markdown_content += f"- [ ] {sh_file}\n"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(markdown_content, encoding="utf-8")

    print(f"📋 Checklist generated at: {output_path}")
    return output_path


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Generate a markdown file with checkboxes for all .py and .sh files.")
    parser.add_argument("--repo", "-r", type=str, default=str(Path.cwd()), help="Repository root path. Defaults to current working directory.")
    parser.add_argument("--exclude", "-e", nargs="+", type=str, help="Additional directories to exclude (by default excludes .venv, .git, __pycache__, build, dist, *.egg-info)")

    args = parser.parse_args()

    exclude_dirs: List[str] = [".venv", ".git", "__pycache__", "build", "dist", "*.egg-info"]
    if args.exclude:
        exclude_dirs.extend(args.exclude)
    if args.repo == "":
        print("Error: Repository path cannot be empty.")
        return

    output_path = generate_file_checklist(args.repo, exclude_dirs)
    console = Console()
    console.print(Panel(f"✅ SUCCESS | Markdown checklist generated successfully!\n📄 File Location: {output_path}", border_style="bold blue", expand=False))


if __name__ == "__main__":
    main()
