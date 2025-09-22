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
from machineconfig.cluster.sessions_managers.layout_types import TabConfig, LayoutConfig
from machineconfig.utils.utils2 import randstr
import random
# import time

AGENTS: TypeAlias = Literal[
    "cursor-agent", "gemini", "crush", "q", "onlyPrepPromptFiles"
    # warp terminal
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


def _search_python_files(repo_root: Path, keyword: str) -> list[Path]:
    """Return all Python files under repo_root whose text contains keyword.

    Notes:
      - Skips any paths that reside under a directory named ".venv" at any depth.
      - Errors reading individual files are ignored (decoded with 'ignore').
    """
    py_files = list(repo_root.rglob("*.py"))
    keyword_lower = keyword.lower()
    matches: list[Path] = []
    for f in py_files:
        # Skip anything under a .venv directory anywhere in the path
        if any(part == ".venv" for part in f.parts):
            continue
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
    print(f"Chunking {len(prompts)} prompts into groups for up to {max_agents} agents because it exceeds the cap.")
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


def launch_agents(repo_root: Path, prompts: list[str], agent: AGENTS, *, max_agents: int = DEFAULT_AGENT_CAP) -> list[TabConfig]:
    """Create tab configuration for a set of agent prompts.

    If number of prompts exceeds max_agents, ask user for confirmation.
    (Original behavior raised an error; now interactive override.)
    """
    if not prompts:
        raise ValueError("No prompts provided")

    if len(prompts) > max_agents:
        proceed = _confirm(message=(f"You are about to launch {len(prompts)} agents which exceeds the cap ({max_agents}). Proceed?"))
        if not proceed:
            print("Aborting per user choice.")
            return []

    tab_config: list[TabConfig] = []
    tmp_dir = repo_root / ".ai" / f"tmp_prompts/{randstr()}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    for idx, a_prompt in enumerate(prompts):
        prompt_path = tmp_dir / f"agent{idx}_prompt.txt"
        prompt_path.write_text(a_prompt, encoding="utf-8")
        cmd_path = tmp_dir / f"agent{idx}_cmd.sh"
        match agent:
            case "gemini":
                # model = "gemini-2.5-pro"
                # model = "gemini-2.5-flash-lite"
                model = None  # auto-select
                if model is None:
                    model_arg = ""
                else:
                    model_arg = f"--model {shlex.quote(model)}"
                # Need a real shell for the pipeline; otherwise '| gemini ...' is passed as args to 'cat'
                safe_path = shlex.quote(str(prompt_path))
                api_keys = get_gemini_api_keys()
                api_key = api_keys[idx % len(api_keys)] if api_keys else ""
                # Export the environment variable so it's available to subshells
                cmd = f"""
export GEMINI_API_KEY={shlex.quote(api_key)}
echo "Using Gemini API key $GEMINI_API_KEY"
cat {prompt_path}
GEMINI_API_KEY={shlex.quote(api_key)} bash -lc 'cat {safe_path} | gemini {model_arg} --yolo --prompt'
"""
            case "cursor-agent":
                # As originally implemented
                cmd = f"""

cursor-agent --print --output-format text < {prompt_path}

"""
            case "crush":
                cmd = f"""
# cat {prompt_path} | crush run
crush run {prompt_path}
"""
            case "q":
                cmd = f"""
q chat --no-interactive --trust-all-tools {prompt_path}
"""
            case "onlyPrepPromptFiles":
                cmd = f"""
echo "Prepared prompt file at {prompt_path}"
"""
            case _:
                raise ValueError(f"Unsupported agent type: {agent}")
        random_sleep_time = random.uniform(0, 5)
        cmd_prefix = f"""
echo "Sleeping for {random_sleep_time:.2f} seconds to stagger agent startups..."
sleep {random_sleep_time:.2f}
echo "Launching `{agent}` with prompt from {prompt_path}"
echo "Launching `{agent}` with command from {cmd_path}"
echo "--------START OF AGENT OUTPUT--------"
sleep 0.1
"""
        cmd_postfix = """
sleep 0.1
echo "---------END OF AGENT OUTPUT---------"
"""
        cmd_path.write_text(cmd_prefix + cmd + cmd_postfix, encoding="utf-8")
        fire_cmd = f"bash {shlex.quote(str(cmd_path))}"
        tab_config.append(TabConfig(tabName=f"Agent{idx}", startDir=str(repo_root), command=fire_cmd))

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
        target_file_path = Path(file_path_input).expanduser().resolve()
        if not target_file_path.exists() or not target_file_path.is_file():
            print(f"Invalid file path: {target_file_path}")
            return
        separator = input("Enter separator [\\n]: ").strip() or "\n"
        if not target_file_path.exists():
            print(f"File does not exist: {target_file_path}")
            return
        source_text = target_file_path.read_text(encoding="utf-8", errors="ignore")

    raw_prompts = source_text.split(separator)
    print(f"Loaded {len(raw_prompts)} raw prompts from source.")
    prefix = input("Enter prefix prompt: ")
    combined_prompts = _chunk_prompts(raw_prompts, DEFAULT_AGENT_CAP)
    combined_prompts = [prefix + "\n" + p for p in combined_prompts]

    from machineconfig.utils.options import choose_one_option

    agent_selected = choose_one_option(header="Select agent type", options=get_args(AGENTS))

    tab_config = launch_agents(repo_root=repo_root, prompts=combined_prompts, agent=agent_selected, max_agents=DEFAULT_AGENT_CAP)
    if not tab_config:
        return

    from machineconfig.utils.utils2 import randstr

    random_name = randstr(length=3)
    manager = ZellijLocalManager(session_layouts=[LayoutConfig(layoutName="Agents", layoutTabs=tab_config)], session_name_prefix=random_name)
    manager.start_all_sessions()
    manager.run_monitoring_routine()


if __name__ == "__main__":  # pragma: no cover
    main()
