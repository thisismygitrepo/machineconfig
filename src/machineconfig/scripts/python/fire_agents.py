"""Utility to launch multiple AI agent prompts in a Zellij session.

Improved design notes:
  * Clear separation of: input collection, prompt preparation, agent launch.
  * Configurable max agent cap (default 15) with interactive confirmation if exceeded.
  * Added type aliases + docstrings for maintainability.
  * Preserves original core behavior & command generation for each agent type.
"""

from pathlib import Path
from typing import cast, get_args, Iterable, TypeAlias, Literal
import json
import sys

from machineconfig.scripts.python.fire_agents_help_launch import prep_agent_launch, get_agents_launch_layout, AGENTS
from machineconfig.scripts.python.fire_agents_help_search import search_files_by_pattern, search_python_files
from machineconfig.scripts.python.fire_agents_load_balancer import chunk_prompts, SPLITTING_STRATEGY, DEFAULT_AGENT_CAP
from machineconfig.utils.options import choose_one_option
from machineconfig.utils.schemas.layouts.layout_types import TabConfig, LayoutConfig
from machineconfig.utils.ve import get_repo_root

SEARCH_STRATEGIES: TypeAlias = Literal["file_path", "keyword_search", "filename_pattern"]


def _write_list_file(target: Path, files: Iterable[Path]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(str(f) for f in files), encoding="utf-8")


def get_prompt_material(search_strategy: SEARCH_STRATEGIES, repo_root: Path) -> tuple[Path, str]:
    if search_strategy == "file_path":
        file_path_input = input("Enter path to target file: ").strip()
        if not file_path_input:
            print("No file path provided. Exiting.")
            sys.exit(1)
        target_file_path = Path(file_path_input).expanduser().resolve()
        if not target_file_path.exists() or not target_file_path.is_file():
            print(f"Invalid file path: {target_file_path}")
            sys.exit(1)
        separator = input("Enter separator [\\n]: ").strip() or "\n"
    elif search_strategy == "keyword_search":
        keyword = input("Enter keyword to search recursively for all .py files containing it: ").strip()
        if not keyword:
            print("No keyword supplied. Exiting.")
            sys.exit(1)
        matching_files = search_python_files(repo_root, keyword)
        if not matching_files:
            print(f"💥 No .py files found containing keyword: {keyword}")
            sys.exit(1)
        for idx, mf in enumerate(matching_files):
            print(f"{idx:>3}: {mf}")
        print(f"\nFound {len(matching_files)} .py files containing keyword: {keyword}")
        target_file_path = repo_root / ".ai" / "target_file.txt"
        _write_list_file(target_file_path, matching_files)
        separator = "\n"
    elif search_strategy == "filename_pattern":
        pattern = input("Enter filename pattern (e.g., '*.py', '*test*', 'config.*'): ").strip()
        if not pattern:
            print("No pattern supplied. Exiting.")
            sys.exit(1)
        matching_files = search_files_by_pattern(repo_root, pattern)
        if not matching_files:
            print(f"💥 No files found matching pattern: {pattern}")
            sys.exit(1)
        for idx, mf in enumerate(matching_files):
            print(f"{idx:>3}: {mf}")
        print(f"\nFound {len(matching_files)} files matching pattern: {pattern}")
        target_file_path = repo_root / ".ai" / "target_file.txt"
        _write_list_file(target_file_path, matching_files)
        separator = "\n"
    else:
        raise ValueError(f"Unknown search strategy: {search_strategy}")
    return target_file_path, separator


def main():  # noqa: C901 - (complexity acceptable for CLI glue)
    repo_root = get_repo_root(Path.cwd())
    if repo_root is None:
        print("💥 Could not determine the repository root. Please run this script from within a git repository.")
        sys.exit(1)
    print(f"Operating @ {repo_root}")

    search_strategy = cast(SEARCH_STRATEGIES, choose_one_option(header="Choose search strategy:", options=get_args(SEARCH_STRATEGIES)))
    splitting_strategy = cast(SPLITTING_STRATEGY, choose_one_option(header="Choose prompt splitting strategy:", options=get_args(SPLITTING_STRATEGY)))
    agent_selected = cast(AGENTS, choose_one_option(header="Select agent type", options=get_args(AGENTS)))
    print("Enter prefix prompt (end with Ctrl-D / Ctrl-Z):")
    prompt_prefix = "\n".join(sys.stdin.readlines())
    job_name = input("Enter job name [AI_AGENTS]: ") or "AI_Agents"
    keep_material_in_separate_file_input = input("Keep prompt material in separate file? [y/N]: ").strip().lower() == "y"

    prompt_material_path, separator = get_prompt_material(search_strategy=search_strategy, repo_root=repo_root)
    match splitting_strategy:
        case "agent_cap":
            agent_cap_input = input(f"Enter maximum number of agents/splits [default: {DEFAULT_AGENT_CAP}]: ").strip()
            agent_cap = int(agent_cap_input) if agent_cap_input else DEFAULT_AGENT_CAP
            task_rows = None
        case "task_rows":
            task_rows_input: str = input("Enter number of rows/tasks per agent [13]: ").strip() or "13"
            task_rows = int(task_rows_input)
            agent_cap = None
    prompt_material_re_splitted = chunk_prompts(prompt_material_path, splitting_strategy, agent_cap=agent_cap, task_rows=task_rows, joiner=separator)

    agents_dir = prep_agent_launch(repo_root=repo_root, prompts_material=prompt_material_re_splitted, keep_material_in_separate_file=keep_material_in_separate_file_input, prompt_prefix=prompt_prefix, agent=agent_selected, job_name=job_name)
    layoutfile = get_agents_launch_layout(session_root=agents_dir)

    regenerate_py_code = f"""
#!/usr/bin/env uv run --python 3.13 --with machineconfig
#!/usr/bin/env uv run --project $HOME/code/machineconfig

from machineconfig.scripts.python.fire_agents import *

repo_root = Path("{repo_root}")
search_strategy = "{search_strategy}"
splitting_strategy = "{splitting_strategy}"
agent_selected = "{agent_selected}"
prompt_prefix = '''{prompt_prefix}'''
job_name = "{job_name}"
keep_material_in_separate_file_input = {keep_material_in_separate_file_input}
separator = "{separator}"
prompt_material_path = Path("{prompt_material_path}")
agent_cap = {agent_cap}
task_rows = {task_rows}

prompt_material_re_splitted = chunk_prompts(prompt_material_path, splitting_strategy, agent_cap=agent_cap, task_rows=task_rows, joiner=separator)
agents_dir = prep_agent_launch(repo_root=repo_root, prompts_material=prompt_material_re_splitted, keep_material_in_separate_file=keep_material_in_separate_file_input, prompt_prefix=prompt_prefix, agent=agent_selected, job_name=job_name)
layout = get_agents_launch_layout(session_root=agents_dir)

(agents_dir / "aa_agents_relaunch.py").write_text(data=regenerate_py_code, encoding="utf-8")
(agents_dir / "layout.json").write_text(data=json.dumps(layout, indent=2), encoding="utf-8")

if len(layout["layoutTabs"]) > 25:
    print("Too many agents (>25) to launch. Skipping launch.")
    sys.exit(0)
manager = ZellijLocalManager(session_layouts=[layout])
manager.start_all_sessions()
manager.run_monitoring_routine()

"""
    (agents_dir / "aa_agents_relaunch.py").write_text(data=regenerate_py_code, encoding="utf-8")
    (agents_dir / "layout.json").write_text(data=json.dumps(layoutfile, indent=2), encoding="utf-8")

    MAX_TABS = 10
    if len(layoutfile["layouts"][0]["layoutTabs"]) > MAX_TABS:
        print(f"Too many tabs (>{MAX_TABS}) to launch. Skipping launch.")
        sys.exit(0)
    from machineconfig.cluster.sessions_managers.zellij_local_manager import ZellijLocalManager

    manager = ZellijLocalManager(session_layouts=layoutfile["layouts"])
    manager.start_all_sessions(poll_interval=2, poll_seconds=2)
    manager.run_monitoring_routine(wait_ms=2000)


def split_too_many_tabs_to_run_in_sequential_sessions(layout_tabs: list[TabConfig], every: int):
    from machineconfig.utils.utils2 import split
    from machineconfig.cluster.sessions_managers.zellij_local_manager import ZellijLocalManager
    for idx, layout_tabs_chunk in enumerate(split(layout_tabs, every=every)):
        a_layout_file: LayoutConfig = {"layoutName": f"split_{idx}", "layoutTabs": layout_tabs_chunk}
        manager = ZellijLocalManager(session_layouts=[a_layout_file])
        manager.start_all_sessions(poll_interval=2, poll_seconds=2)
        manager.run_monitoring_routine(wait_ms=2000)
        manager.kill_all_sessions()
def split_too_many_layouts_to_run_in_sequential_sessions(layouts: list[LayoutConfig], every: int):
    from machineconfig.utils.utils2 import split
    from machineconfig.cluster.sessions_managers.zellij_local_manager import ZellijLocalManager
    for _idx, layout_chunk in enumerate(split(layouts, every=every)):
        manager = ZellijLocalManager(session_layouts=layout_chunk)
        manager.start_all_sessions(poll_interval=2, poll_seconds=2)
        manager.run_monitoring_routine(wait_ms=2000)


if __name__ == "__main__":  # pragma: no cover
    main()
