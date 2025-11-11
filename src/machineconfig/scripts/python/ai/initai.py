from pathlib import Path

from machineconfig.scripts.python.ai.solutions import generic
from machineconfig.scripts.python.ai.solutions.claude import claude
from machineconfig.scripts.python.ai.solutions.cline import cline
from machineconfig.scripts.python.ai.solutions.copilot import github_copilot
from machineconfig.scripts.python.ai.solutions.crush import crush
from machineconfig.scripts.python.ai.solutions.cursor import cursors
from machineconfig.scripts.python.ai.solutions.gemini import gemini
from machineconfig.scripts.python.ai.utils.vscode_tasks import add_lint_and_type_check_task
from machineconfig.utils.accessories import get_repo_root


def add_ai_configs(repo_root: Path) -> None:
    repo_root_resolved = get_repo_root(repo_root)
    if repo_root_resolved is not None:
        repo_root = repo_root_resolved  # this means you can run the command from any subdirectory of the repo.
    dot_ai_dir = repo_root.joinpath(".ai")
    dot_ai_dir.mkdir(parents=True, exist_ok=True)
    dot_scripts_dir = repo_root.joinpath(".scripts")
    dot_scripts_dir.mkdir(parents=True, exist_ok=True)
    generic.create_dot_scripts(repo_root=repo_root)
    generic.adjust_gitignore(repo_root=repo_root)

    add_lint_and_type_check_task(repo_root=repo_root)

    github_copilot.build_configuration(repo_root=repo_root)
    cursors.build_configuration(repo_root=repo_root)
    gemini.build_configuration(repo_root=repo_root)
    claude.build_configuration(repo_root=repo_root)
    crush.build_configuration(repo_root=repo_root)
    cline.build_configuration(repo_root=repo_root)

