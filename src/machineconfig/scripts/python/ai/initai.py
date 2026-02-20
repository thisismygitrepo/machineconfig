from pathlib import Path
from collections.abc import Sequence

from machineconfig.scripts.python.ai.utils import generic
from machineconfig.scripts.python.ai.solutions.claude import claude
from machineconfig.scripts.python.ai.solutions.cline import cline
from machineconfig.scripts.python.ai.solutions.copilot import github_copilot
from machineconfig.scripts.python.ai.solutions.crush import crush
from machineconfig.scripts.python.ai.solutions.cursor import cursors
from machineconfig.scripts.python.ai.solutions.gemini import gemini
from machineconfig.scripts.python.ai.solutions.qwen_code import qwen_code
from machineconfig.scripts.python.ai.solutions.codex import codex
from machineconfig.scripts.python.ai.solutions.q import amazon_q
from machineconfig.scripts.python.ai.solutions.opencode import opencode
from machineconfig.scripts.python.ai.solutions.kilocode import kilocode
from machineconfig.scripts.python.ai.solutions.auggie import auggie
from machineconfig.scripts.python.ai.solutions.warp import warp
from machineconfig.scripts.python.ai.solutions.droid import droid
from machineconfig.scripts.python.ai.utils.vscode_tasks import (
    add_lint_and_type_check_task,
)
from machineconfig.scripts.python.helpers.helpers_agents.fire_agents_helper_types import (
    AGENTS,
)
from machineconfig.utils.accessories import get_repo_root


def _build_framework_config(repo_root: Path, framework: AGENTS) -> None:
    match framework:
        case "copilot":
            github_copilot.build_configuration(repo_root=repo_root)
        case "cursor":
            cursors.build_configuration(repo_root=repo_root)
        case "gemini":
            gemini.build_configuration(repo_root=repo_root)
        case "claude":
            claude.build_configuration(repo_root=repo_root)
        case "crush":
            crush.build_configuration(repo_root=repo_root)
        case "cline":
            cline.build_configuration(repo_root=repo_root)
        case "qwen-code":
            qwen_code.build_configuration(repo_root=repo_root)
        case "codex":
            codex.build_configuration(repo_root=repo_root)
        case "q":
            amazon_q.build_configuration(repo_root=repo_root)
        case "opencode":
            opencode.build_configuration(repo_root=repo_root)
        case "kilocode":
            kilocode.build_configuration(repo_root=repo_root)
        case "auggie":
            auggie.build_configuration(repo_root=repo_root)
        case "warp":
            warp.build_configuration(repo_root=repo_root)
        case "droid":
            droid.build_configuration(repo_root=repo_root)
        case _:
            print(ValueError(f"Unsupported framework: {framework}"))


def add_ai_configs(
    repo_root: Path,
    frameworks: Sequence[AGENTS],
    include_common_scaffold: bool,
    add_vscode_task: bool,
) -> None:
    if len(frameworks) == 0:
        raise ValueError("At least one framework must be provided")

    repo_root_resolved = get_repo_root(repo_root)
    if repo_root_resolved is not None:
        repo_root = repo_root_resolved  # this means you can run the command from any subdirectory of the repo.
    if include_common_scaffold:
        dot_ai_dir = repo_root.joinpath(".ai")
        dot_ai_dir.mkdir(parents=True, exist_ok=True)
        dot_scripts_dir = repo_root.joinpath(".scripts")
        dot_scripts_dir.mkdir(parents=True, exist_ok=True)
        generic.create_dot_scripts(repo_root=repo_root)
        if not repo_root.joinpath(".gitignore").exists():
            repo_root.joinpath(".gitignore").touch()
        generic.adjust_gitignore(repo_root=repo_root)

    if add_vscode_task:
        add_lint_and_type_check_task(repo_root=repo_root)

    selected_frameworks: tuple[AGENTS, ...] = tuple(dict.fromkeys(frameworks))
    for framework in selected_frameworks:
        _build_framework_config(repo_root=repo_root, framework=framework)
