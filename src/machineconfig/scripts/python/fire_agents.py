
"""Utility to launch multiple AI agent prompts in a Zellij session.

Improved design notes:
  * Clear separation of: input collection, prompt preparation, agent launch.
  * Configurable max agent cap (default 15) with interactive confirmation if exceeded.
  * Added type aliases + docstrings for maintainability.
  * Preserves original core behavior & command generation for each agent type.
"""

from __future__ import annotations

from pathlib import Path
import shlex
from math import ceil
from typing import Literal, TypeAlias, get_args, Iterable

from machineconfig.cluster.sessions_managers.zellij_local_manager import ZellijLocalManager


AGENTS: TypeAlias = Literal["cursor-agent", "gemini"]
TabConfig = dict[str, tuple[str, str]]  # tab name -> (cwd, command)
DEFAULT_AGENT_CAP = 15

def _search_python_files(repo_root: Path, keyword: str) -> list[Path]:
    """Return all Python files under repo_root whose text contains keyword.

    Errors reading individual files are ignored (decoded with 'ignore').
    """
    py_files = list(repo_root.rglob("*.py"))
    keyword_lower = keyword.lower()
    matches: list[Path] = []
    for f in py_files:
        try:
            if keyword_lower in f.read_text(encoding="utf-8", errors="ignore").lower():
                matches.append(f)
        except OSError:
            # Skip unreadable file
            continue
    return matches


def _write_list_file(target: Path, files: Iterable[Path]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(str(f) for f in files), encoding="utf-8")
def _chunk_prompts(prompts: list[str], max_agents: int) -> list[str]:
    prompts = [p for p in prompts if p.strip() != ""]  # drop blank entries
    if len(prompts) <= max_agents:
        return prompts
    chunk_size = ceil(len(prompts) / max_agents)
    grouped: list[str] = []
    for i in range(0, len(prompts), chunk_size):
        grouped.append("\nTargeted Locations:\n".join(prompts[i : i + chunk_size]))
    return grouped
def _confirm(message: str, default_no: bool = True) -> bool:
    suffix = "[y/N]" if default_no else "[Y/n]"
    answer = input(f"{message} {suffix} ").strip().lower()
    if answer in {"y", "yes"}:
        return True
    if not default_no and answer == "":
        return True
    return False


def launch_agents(repo_root: Path, prompts: list[str], agent: AGENTS, *, max_agents: int = DEFAULT_AGENT_CAP) -> TabConfig:
    """Create tab configuration for a set of agent prompts.

    If number of prompts exceeds max_agents, ask user for confirmation.
    (Original behavior raised an error; now interactive override.)
    """
    if not prompts:
        raise ValueError("No prompts provided")

    if len(prompts) > max_agents:
        proceed = _confirm(
            message=(
                f"You are about to launch {len(prompts)} agents which exceeds the cap ({max_agents}). Proceed?"
            )
        )
        if not proceed:
            print("Aborting per user choice.")
            return {}

    tab_config: TabConfig = {}
    tmp_dir = repo_root / ".ai" / "tmp_prompts"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    for idx, a_prompt in enumerate(prompts):
        tmp_file_path = tmp_dir / f"agent{idx}.txt"
        tmp_file_path.write_text(a_prompt, encoding="utf-8")
        match agent:
            case "gemini":
                # Need a real shell for the pipeline; otherwise '| gemini ...' is passed as args to 'cat'
                safe_path = shlex.quote(str(tmp_file_path))
                cmd = f"bash -lc 'cat {safe_path} | gemini --yolo --prompt'"
            case "cursor-agent":
                # As originally implemented
                cmd = f"cursor-agent --print --output-format text < {tmp_file_path}"
            case _:
                raise ValueError(f"Unsupported agent type: {agent}")
        tab_config[f"Agent{idx}"] = (str(repo_root), cmd)

    print(f"Launching a template with #{len(tab_config)} agents")
    return tab_config


def main():  # noqa: C901 - (complexity acceptable for CLI glue)
    repo_root = Path.cwd()
    print(f"Operating @ {repo_root}")

    file_path_input = input("Enter path to target file [press Enter to generate it from searching]: ").strip()
    if file_path_input == "":
        keyword = input("Enter keyword to search recursively for all .py files containing it: ").strip()
        if not keyword:
            print("No keyword supplied. Exiting.")
            return
        matching_files = _search_python_files(repo_root, keyword)
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
    else:
        separator = input("Enter separator [\\n]: ").strip() or "\n"
        target_file_path = Path(file_path_input).expanduser().resolve()
        if not target_file_path.exists():
            print(f"File does not exist: {target_file_path}")
            return
        source_text = target_file_path.read_text(encoding="utf-8", errors="ignore")

    prefix = input("Enter prefix prompt: ")
    raw_prompts = source_text.split(separator)
    combined_prompts = _chunk_prompts(raw_prompts, DEFAULT_AGENT_CAP)
    combined_prompts = [prefix + "\n" + p for p in combined_prompts]

    from machineconfig.utils.options import choose_one_option
    agent_selected = choose_one_option(header="Select agent type", options=get_args(AGENTS))

    tab_config = launch_agents(
        repo_root=repo_root,
        prompts=combined_prompts,
        agent=agent_selected,
        max_agents=DEFAULT_AGENT_CAP,
    )
    if not tab_config:
        return

    from machineconfig.utils.utils2 import randstr
    random_name = randstr(length=3)
    manager = ZellijLocalManager(session2zellij_tabs={"Agents": tab_config}, session_name_prefix=random_name)
    manager.start_all_sessions()
    manager.run_monitoring_routine()


if __name__ == "__main__":  # pragma: no cover
    main()
