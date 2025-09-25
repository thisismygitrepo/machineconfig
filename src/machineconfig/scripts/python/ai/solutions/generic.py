from pathlib import Path

from machineconfig.utils.source_of_truth import LIBRARY_ROOT


def create_dot_scripts(repo_root: Path) -> None:
    scripts_dir = LIBRARY_ROOT.joinpath("scripts/python/ai/scripts")
    target_dir = repo_root.joinpath(".scripts")
    target_dir.mkdir(parents=True, exist_ok=True)
    for script_path in scripts_dir.iterdir():
        target_dir.joinpath(script_path.name).write_text(data=script_path.read_text(encoding="utf-8"), encoding="utf-8")


def adjust_gitignore(repo_root: Path) -> None:
    dot_git_ignore_path = repo_root.joinpath(".gitignore")
    if dot_git_ignore_path.exists() is False:
        return

    dot_git_ignore_content = dot_git_ignore_path.read_text(encoding="utf-8")
    entries_to_add: list[str] = []
    required_entries: list[str] = [
        ".links",
        "notebooks",
        ".ai",
        ".scripts",
        "GEMINI.md",
        "CLAUDE.md",
        ".cursor",
        ".github/instructions",
        ".github/chatmodes",
        ".github/prompts",
    ]

    for entry in required_entries:
        if entry not in dot_git_ignore_content:
            entries_to_add.append(entry)

    if len(entries_to_add) == 0:
        return

    dot_git_ignore_path.write_text(data=dot_git_ignore_content + "\n" + "\n".join(entries_to_add), encoding="utf-8")
