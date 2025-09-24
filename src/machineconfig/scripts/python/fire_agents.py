"""Utility to launch multiple AI agent prompts in a Zellij session.

Improved design notes:
  * Clear separation of: input collection, prompt preparation, agent launch.
  * Configurable max agent cap (default 15) with interactive confirmation if exceeded.
  * Added type aliases + docstrings for maintainability.
  * Preserves original core behavior & command generation for each agent type.
"""

from pathlib import Path
from typing import cast, get_args, Iterable, TypeAlias, Literal

from machineconfig.scripts.python.fire_agents_help_launch import launch_agents, AGENTS
from machineconfig.scripts.python.fire_agents_help_search import search_files_by_pattern, search_python_files
from machineconfig.scripts.python.fire_agents_load_balancer import redistribute_prompts, SPLITTING_STRATEGY
from machineconfig.cluster.sessions_managers.zellij_local_manager import ZellijLocalManager
from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig
# import time
import sys


SEARCH_STRATEGIES: TypeAlias = Literal["file_path", "keyword_search", "filename_pattern"]


def _write_list_file(target: Path, files: Iterable[Path]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(str(f) for f in files), encoding="utf-8")


def get_prompt_material(search_strategy: SEARCH_STRATEGIES, repo_root: Path) -> tuple[str, str]:
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
        prompt_material = target_file_path.read_text(encoding="utf-8", errors="ignore")
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
        target_list_file = repo_root / ".ai" / "target_file.txt"
        _write_list_file(target_list_file, matching_files)
        separator = "\n"
        prompt_material = target_list_file.read_text(encoding="utf-8", errors="ignore")
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
        target_list_file = repo_root / ".ai" / "target_file.txt"
        _write_list_file(target_list_file, matching_files)
        separator = "\n"
        prompt_material = target_list_file.read_text(encoding="utf-8", errors="ignore")        
    else:
        raise ValueError(f"Unknown search strategy: {search_strategy}")
    return prompt_material, separator


def main():  # noqa: C901 - (complexity acceptable for CLI glue)
    repo_root = Path.cwd()
    print(f"Operating @ {repo_root}")
    from machineconfig.utils.options import choose_one_option
    search_strategy = cast(SEARCH_STRATEGIES, choose_one_option(header="Choose search strategy:", options=get_args(SEARCH_STRATEGIES)))
    prompt_material, separator = get_prompt_material(search_strategy=search_strategy, repo_root=repo_root)
    splitting_strategy = cast(SPLITTING_STRATEGY, choose_one_option(header="Choose prompt splitting strategy:", options=get_args(SPLITTING_STRATEGY)))
    prompt_material_re_splitted = redistribute_prompts(prompt_material=prompt_material, separator=separator, splitting_strategy=splitting_strategy)
    agent_selected = cast(AGENTS, choose_one_option(header="Select agent type", options=get_args(AGENTS)))
    prompt_prefix = input("Enter prefix prompt: ")
    job_name = input("Enter job name ") or "AI_Agents"
    keep_material_in_separate_file_input = input("Keep prompt material in separate file? [y/N]: ").strip().lower() == "y"
    tab_config = launch_agents(repo_root=repo_root, prompts_material=prompt_material_re_splitted, keep_material_in_separate_file=keep_material_in_separate_file_input, prompt_prefix=prompt_prefix, agent=agent_selected, max_agents=25, job_name=job_name)
    if not tab_config:
        return
    from machineconfig.utils.utils2 import randstr
    random_name = randstr(length=3)
    manager = ZellijLocalManager(session_layouts=[LayoutConfig(layoutName="Agents", layoutTabs=tab_config)], session_name_prefix=random_name)
    manager.start_all_sessions()
    manager.run_monitoring_routine()


if __name__ == "__main__":  # pragma: no cover
    main()
