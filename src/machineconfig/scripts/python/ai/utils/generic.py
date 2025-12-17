
from pathlib import Path
import platform

from machineconfig.utils.source_of_truth import LIBRARY_ROOT


def create_dot_scripts(repo_root: Path) -> None:
    scripts_dir = LIBRARY_ROOT.joinpath("scripts/python/ai/scripts")
    target_dir = repo_root.joinpath(".ai/scripts")
    import shutil
    shutil.rmtree(target_dir, ignore_errors=True)
    target_dir.mkdir(parents=True, exist_ok=True)
    import platform
    if platform.system() == "Windows":
        script_path = scripts_dir.joinpath("lint_and_type_check.ps1")
    elif platform.system() in ["Linux", "Darwin"]:
        script_path = scripts_dir.joinpath("lint_and_type_check.sh")
    else:
        raise NotImplementedError(f"Platform {platform.system()} is not supported.")
    target_dir.joinpath(script_path.name).write_text(data=script_path.read_text(encoding="utf-8"), encoding="utf-8")


def adjust_for_os(config_path: Path) -> str:
    if config_path.suffix not in [".md", ".txt"]:
        return config_path.read_text(encoding="utf-8")
    english_text = config_path.read_text(encoding="utf-8")
    if platform.system() == "Windows":
        return english_text.replace("bash", "PowerShell").replace("sh ", "pwsh ").replace("./", ".\\").replace(".sh", ".ps1")
    elif platform.system() in ["Linux", "Darwin"]:
        return english_text.replace("PowerShell", "bash").replace("pwsh ", "sh ").replace(".\\", "./").replace(".ps1", ".sh")
    else:
        raise NotImplementedError(f"Platform {platform.system()} is not supported.")


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
        "GEMINI.md",
        "CLAUDE.md",
        "CRUSH.md",
        "AGENTS.md",
        ".cursor",
        ".clinerules",
        ".github/instructions",
        ".github/agents",
        ".github/prompts",
    ]

    for entry in required_entries:
        if entry not in dot_git_ignore_content:
            entries_to_add.append(entry)

    if len(entries_to_add) == 0:
        return

    dot_git_ignore_path.write_text(data=dot_git_ignore_content + "\n" + "\n".join(entries_to_add), encoding="utf-8")
