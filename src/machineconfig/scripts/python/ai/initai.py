from pathlib import Path
from collections.abc import Sequence
from time import perf_counter

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


def _snapshot_repo_files(repo_root: Path) -> dict[Path, tuple[int, int]]:
    files_state: dict[Path, tuple[int, int]] = {}
    for path in repo_root.rglob("*"):
        if path.is_file() is False:
            continue
        if ".git" in path.parts:
            continue
        file_stat = path.stat()
        files_state[path.relative_to(repo_root)] = (file_stat.st_mtime_ns, file_stat.st_size)
    return files_state


def _collect_touched_files(before: dict[Path, tuple[int, int]], after: dict[Path, tuple[int, int]]) -> list[str]:
    touched_files: list[str] = []
    for path, after_state in after.items():
        before_state = before.get(path)
        if before_state is None or before_state != after_state:
            relative_path = path.as_posix()
            if relative_path != ".gitignore":
                touched_files.append(relative_path)
    touched_files.sort()
    return touched_files


def _build_framework_config(repo_root: Path, framework: AGENTS, add_private_config: bool, add_instructions: bool) -> None:
    match framework:
        case "copilot":
            github_copilot.build_configuration(repo_root=repo_root, add_private_config=add_private_config, add_instructions=add_instructions)
        case "cursor-agent":
            cursors.build_configuration(repo_root=repo_root, add_private_config=add_private_config, add_instructions=add_instructions)
        case "gemini":
            gemini.build_configuration(repo_root=repo_root, add_private_config=add_private_config, add_instructions=add_instructions)
        case "claude":
            claude.build_configuration(repo_root=repo_root, add_private_config=add_private_config, add_instructions=add_instructions)
        case "crush":
            crush.build_configuration(repo_root=repo_root, add_private_config=add_private_config, add_instructions=add_instructions)
        case "cline":
            cline.build_configuration(repo_root=repo_root, add_private_config=add_private_config, add_instructions=add_instructions)
        case "qwen":
            qwen_code.build_configuration(repo_root=repo_root, add_private_config=add_private_config, add_instructions=add_instructions)
        case "codex":
            codex.build_configuration(repo_root=repo_root, add_private_config=add_private_config, add_instructions=add_instructions)
        case "q":
            amazon_q.build_configuration(repo_root=repo_root, add_private_config=add_private_config, add_instructions=add_instructions)
        case "opencode":
            opencode.build_configuration(repo_root=repo_root, add_private_config=add_private_config, add_instructions=add_instructions)
        case "kilocode":
            kilocode.build_configuration(repo_root=repo_root, add_private_config=add_private_config, add_instructions=add_instructions)
        case "auggie":
            auggie.build_configuration(repo_root=repo_root, add_private_config=add_private_config, add_instructions=add_instructions)
        case "warp-cli":
            warp.build_configuration(repo_root=repo_root, add_private_config=add_private_config, add_instructions=add_instructions)
        case "droid":
            droid.build_configuration(repo_root=repo_root, add_private_config=add_private_config, add_instructions=add_instructions)
        case _:
            print(ValueError(f"Unsupported framework: {framework}"))


def add_ai_configs(
    repo_root: Path,
    frameworks: Sequence[AGENTS],
    include_common_scaffold: bool,
    add_all_touched_configs_to_gitignore: bool,
    add_vscode_task: bool,
    add_private_config: bool,
    add_instructions: bool,
) -> None:
    if len(frameworks) == 0:
        raise ValueError("At least one framework must be provided")

    started_at = perf_counter()
    print(
        f"[init-config] add_ai_configs:start frameworks={','.join(frameworks)} include_common={include_common_scaffold} add_gitignore={add_all_touched_configs_to_gitignore} add_lint_task={add_vscode_task} add_private_config={add_private_config} add_instructions={add_instructions}"
    )

    repo_root_resolved = get_repo_root(repo_root)
    if repo_root_resolved is not None:
        repo_root = repo_root_resolved  # this means you can run the command from any subdirectory of the repo.
    print(f"[init-config] repository root resolved: {repo_root}")

    should_track_touched_files = add_all_touched_configs_to_gitignore
    files_before_configuration: dict[Path, tuple[int, int]] = {}
    if should_track_touched_files:
        phase_started = perf_counter()
        files_before_configuration = _snapshot_repo_files(repo_root=repo_root)
        snapshot_before_elapsed = perf_counter() - phase_started
        total_elapsed_after_snapshot_before = perf_counter() - started_at
        print(f"[init-config] snapshot before done in {snapshot_before_elapsed:.3f}s (total {total_elapsed_after_snapshot_before:.3f}s)")
    else:
        total_elapsed_without_snapshot = perf_counter() - started_at
        print(f"[init-config] snapshot before skipped (total {total_elapsed_without_snapshot:.3f}s)")

    if include_common_scaffold:
        phase_started = perf_counter()
        print("[init-config] creating common scaffold")
        dot_ai_dir = repo_root.joinpath(".ai")
        dot_ai_dir.mkdir(parents=True, exist_ok=True)
        dot_scripts_dir = repo_root.joinpath(".scripts")
        dot_scripts_dir.mkdir(parents=True, exist_ok=True)
        generic.create_dot_scripts(repo_root=repo_root)
        common_scaffold_elapsed = perf_counter() - phase_started
        total_elapsed_after_common_scaffold = perf_counter() - started_at
        print(f"[init-config] common scaffold done in {common_scaffold_elapsed:.3f}s (total {total_elapsed_after_common_scaffold:.3f}s)")

    if add_vscode_task:
        phase_started = perf_counter()
        print("[init-config] adding VS Code lint/type-check task")
        add_lint_and_type_check_task(repo_root=repo_root)
        vscode_task_elapsed = perf_counter() - phase_started
        total_elapsed_after_vscode_task = perf_counter() - started_at
        print(f"[init-config] VS Code task update done in {vscode_task_elapsed:.3f}s (total {total_elapsed_after_vscode_task:.3f}s)")

    selected_frameworks: tuple[AGENTS, ...] = tuple(dict.fromkeys(frameworks))
    for framework in selected_frameworks:
        framework_started = perf_counter()
        print(f"[init-config] framework start: {framework}")
        _build_framework_config(repo_root=repo_root, framework=framework, add_private_config=add_private_config, add_instructions=add_instructions)
        framework_elapsed = perf_counter() - framework_started
        framework_total_elapsed = perf_counter() - started_at
        print(f"[init-config] framework done: {framework} in {framework_elapsed:.3f}s (total {framework_total_elapsed:.3f}s)")

    touched_config_files: list[str] = []
    if should_track_touched_files:
        phase_started = perf_counter()
        files_after_configuration = _snapshot_repo_files(repo_root=repo_root)
        snapshot_after_elapsed = perf_counter() - phase_started
        total_elapsed_after_snapshot_after = perf_counter() - started_at
        print(f"[init-config] snapshot after done in {snapshot_after_elapsed:.3f}s (total {total_elapsed_after_snapshot_after:.3f}s)")

        phase_started = perf_counter()
        touched_config_files = _collect_touched_files(before=files_before_configuration, after=files_after_configuration)
        touched_files_elapsed = perf_counter() - phase_started
        total_elapsed_after_touched = perf_counter() - started_at
        print(f"[init-config] touched files collected in {touched_files_elapsed:.3f}s (total {total_elapsed_after_touched:.3f}s, files={len(touched_config_files)})")
    else:
        total_elapsed_without_snapshot_after = perf_counter() - started_at
        print(f"[init-config] snapshot after skipped (total {total_elapsed_without_snapshot_after:.3f}s)")

    if should_track_touched_files:
        phase_started = perf_counter()
        print("[init-config] updating .gitignore entries")
        dot_git_ignore_path = repo_root.joinpath(".gitignore")
        if dot_git_ignore_path.exists() is False:
            dot_git_ignore_path.touch()
        generic.adjust_gitignore(repo_root=repo_root, include_default_entries=False, extra_entries=touched_config_files)
        gitignore_elapsed = perf_counter() - phase_started
        total_elapsed_after_gitignore = perf_counter() - started_at
        print(f"[init-config] .gitignore update done in {gitignore_elapsed:.3f}s (total {total_elapsed_after_gitignore:.3f}s)")

    total_elapsed = perf_counter() - started_at
    print(f"[init-config] add_ai_configs:complete total={total_elapsed:.3f}s")
