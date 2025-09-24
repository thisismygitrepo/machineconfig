"""Utility to launch multiple AI agent prompts in a Zellij session.

Improved design notes:
  * Clear separation of: input collection, prompt preparation, agent launch.
  * Configurable max agent cap (default 15) with interactive confirmation if exceeded.
  * Added type aliases + docstrings for maintainability.
  * Preserves original core behavior & command generation for each agent type.
"""

from __future__ import annotations

from pathlib import Path
from math import ceil
from typing import Literal, TypeAlias, get_args, Iterable

from machineconfig.cluster.sessions_managers.zellij_local_manager import ZellijLocalManager
from machineconfig.scripts.python.fire_agents_help_launch import launch_agents
from machineconfig.scripts.python.fire_agents_help_search import search_files_by_pattern, search_python_files
from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig
# import time

AGENTS: TypeAlias = Literal[
    "cursor-agent", "gemini", "crush", "q", "onlyPrepPromptFiles"
    # warp terminal
]

SPLITTING_STRATEGY: TypeAlias = Literal[
    "agent_cap",  # User decides number of agents, rows/tasks determined automatically
    "task_rows"   # User decides number of rows/tasks, number of agents determined automatically
]

DEFAULT_AGENT_CAP = 6


def get_gemini_api_keys() -> list[str]:
    from machineconfig.utils.utils2 import read_ini

    config = read_ini(Path.home().joinpath("dotfiles/creds/llm/gemini/api_keys.ini"))
    res: list[str] = []
    for a_section_name in list(config.sections()):
        a_section = config[a_section_name]
        if "api_key" in a_section:
            api_key = a_section["api_key"].strip()
            if api_key:
                res.append(api_key)
    # res = [v for k, v in config.items("api_keys") if k.startswith("key") and v.strip() != ""]
    print(f"Found {len(res)} Gemini API keys configured.")
    return res


def _write_list_file(target: Path, files: Iterable[Path]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(str(f) for f in files), encoding="utf-8")


def _chunk_prompts(prompts: list[str], strategy: SPLITTING_STRATEGY, *, agent_cap: int | None, task_rows: int | None) -> list[str]:
    """Chunk prompts based on splitting strategy.
    
    Args:
        prompts: List of prompts to chunk
        strategy: Either 'agent_cap' or 'task_rows'  
        agent_cap: Maximum number of agents (used with 'agent_cap' strategy)
        task_rows: Number of rows/tasks per agent (used with 'task_rows' strategy)
    """
    prompts = [p for p in prompts if p.strip() != ""]  # drop blank entries
    
    if strategy == "agent_cap":
        if agent_cap is None:
            raise ValueError("agent_cap must be provided when using 'agent_cap' strategy")
        
        if len(prompts) <= agent_cap:
            return prompts
        
        print(f"Chunking {len(prompts)} prompts into groups for up to {agent_cap} agents because it exceeds the cap.")
        chunk_size = ceil(len(prompts) / agent_cap)
        grouped: list[str] = []
        for i in range(0, len(prompts), chunk_size):
            grouped.append("\nTargeted Locations:\n".join(prompts[i : i + chunk_size]))
        return grouped
    
    elif strategy == "task_rows":
        if task_rows is None:
            raise ValueError("task_rows must be provided when using 'task_rows' strategy")
        
        if task_rows >= len(prompts):
            return prompts
            
        print(f"Chunking {len(prompts)} prompts into groups of {task_rows} rows/tasks each.")
        grouped: list[str] = []
        for i in range(0, len(prompts), task_rows):
            grouped.append("\nTargeted Locations:\n".join(prompts[i : i + task_rows]))
        return grouped
    
    else:
        raise ValueError(f"Unknown splitting strategy: {strategy}")



def main():  # noqa: C901 - (complexity acceptable for CLI glue)
    repo_root = Path.cwd()
    print(f"Operating @ {repo_root}")

    from machineconfig.utils.options import choose_one_option

    # Prompt user to choose search strategy
    search_strategies = ["file_path", "keyword_search", "filename_pattern"]
    search_strategy = choose_one_option(
        header="Choose search strategy:",
        options=search_strategies
    )

    # Execute chosen search strategy
    if search_strategy == "file_path":
        file_path_input = input("Enter path to target file: ").strip()
        if not file_path_input:
            print("No file path provided. Exiting.")
            return
        target_file_path = Path(file_path_input).expanduser().resolve()
        if not target_file_path.exists() or not target_file_path.is_file():
            print(f"Invalid file path: {target_file_path}")
            return
        separator = input("Enter separator [\\n]: ").strip() or "\n"
        source_text = target_file_path.read_text(encoding="utf-8", errors="ignore")
        
    elif search_strategy == "keyword_search":
        keyword = input("Enter keyword to search recursively for all .py files containing it: ").strip()
        if not keyword:
            print("No keyword supplied. Exiting.")
            return
        matching_files = search_python_files(repo_root, keyword)
        if not matching_files:
            print(f"💥 No .py files found containing keyword: {keyword}")
            return
        for idx, mf in enumerate(matching_files):
            print(f"{idx:>3}: {mf}")
        print(f"\nFound {len(matching_files)} .py files containing keyword: {keyword}")
        target_list_file = repo_root / ".ai" / "target_file.txt"
        _write_list_file(target_list_file, matching_files)
        separator = "\n"
        source_text = target_list_file.read_text(encoding="utf-8", errors="ignore")
        
    elif search_strategy == "filename_pattern":
        pattern = input("Enter filename pattern (e.g., '*.py', '*test*', 'config.*'): ").strip()
        if not pattern:
            print("No pattern supplied. Exiting.")
            return
        matching_files = search_files_by_pattern(repo_root, pattern)
        if not matching_files:
            print(f"💥 No files found matching pattern: {pattern}")
            return
        for idx, mf in enumerate(matching_files):
            print(f"{idx:>3}: {mf}")
        print(f"\nFound {len(matching_files)} files matching pattern: {pattern}")
        target_list_file = repo_root / ".ai" / "target_file.txt"
        _write_list_file(target_list_file, matching_files)
        separator = "\n"
        source_text = target_list_file.read_text(encoding="utf-8", errors="ignore")        
    else:
        raise ValueError(f"Unknown search strategy: {search_strategy}")
    raw_prompts = source_text.split(separator)
    print(f"Loaded {len(raw_prompts)} raw prompts from source.")
    prefix = input("Enter prefix prompt: ")
    # Prompt user for splitting strategy
    splitting_strategy = choose_one_option(header="Select splitting strategy", options=get_args(SPLITTING_STRATEGY))    
    # Get parameters based on strategy
    if splitting_strategy == "agent_cap":
        agent_cap_input = input(f"Enter maximum number of agents/splits [default: {DEFAULT_AGENT_CAP}]: ").strip()
        agent_cap = int(agent_cap_input) if agent_cap_input else DEFAULT_AGENT_CAP
        combined_prompts = _chunk_prompts(raw_prompts, splitting_strategy, agent_cap=agent_cap, task_rows=None)
        max_agents_for_launch = agent_cap
    elif splitting_strategy == "task_rows":
        task_rows_input = input("Enter number of rows/tasks per agent: ").strip()
        if not task_rows_input:
            print("Number of rows/tasks is required for this strategy.")
            return
        task_rows = int(task_rows_input)
        combined_prompts = _chunk_prompts(raw_prompts, splitting_strategy, agent_cap=None, task_rows=task_rows)
        max_agents_for_launch = len(combined_prompts)  # Number of agents determined by chunking
    else:
        raise ValueError(f"Unknown splitting strategy: {splitting_strategy}")
    combined_prompts = [prefix + "\n" + p for p in combined_prompts]
    agent_selected = choose_one_option(header="Select agent type", options=get_args(AGENTS))
    tab_config = launch_agents(repo_root=repo_root, prompts=combined_prompts, agent=agent_selected, max_agents=max_agents_for_launch)
    if not tab_config:
        return
    from machineconfig.utils.utils2 import randstr
    random_name = randstr(length=3)
    manager = ZellijLocalManager(session_layouts=[LayoutConfig(layoutName="Agents", layoutTabs=tab_config)], session_name_prefix=random_name)
    manager.start_all_sessions()
    manager.run_monitoring_routine()


if __name__ == "__main__":  # pragma: no cover
    main()
