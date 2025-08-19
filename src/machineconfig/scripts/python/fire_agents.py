

from pathlib import Path
# from machineconfig.cluster.sessions_managers.zellij_local import run_zellij_layout
from machineconfig.cluster.sessions_managers.zellij_local_manager import ZellijLocalManager


def launch_agents(repo_root: Path, prompts: list[str]):
    tab_config: dict[str, tuple[str, str]] = {}
    for idx, a_prompt in enumerate(prompts):
        tmp_file_path = repo_root.joinpath(f".ai/tmp_prompts/agent{idx}.txt")
        tmp_file_path.parent.mkdir(parents=True, exist_ok=True)
        Path(tmp_file_path).write_text(a_prompt)
        tab_config[f"Agent{idx}"] = (str(repo_root), f"cursor-agent --print --output-format text < .ai/tmp_prompts/agent{idx}.txt")
    if len(tab_config) > 15:
        raise RuntimeError(f"Too many agents (#{len(tab_config)}), please cut them down to 15 or less")
    print(f"Launching a template with #{len(tab_config)} agents")
    return tab_config


def main():
    repo_root = Path.cwd()
    print(f"Operating @ {repo_root}")
    file_path = input("Enter path to target file [press Enter to generate it from searching]: ")
    if file_path == "":
        keyword = input("Enter keyword to search recursively for all .py files containing it. ")
        py_files = list(repo_root.rglob("*.py"))
        matching_files = [
            f for f in py_files
            if keyword in f.read_text(encoding='utf-8', errors='ignore')
        ]
        if not matching_files:
            print(f"💥 No .py files found containing keyword: {keyword}")
            return
        print(f"Found {len(matching_files)} .py files containing keyword: {keyword}")
        file_path = repo_root.joinpath(".ai", "target_file.txt")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("\n".join(str(f) for f in matching_files), encoding='utf-8')
        separator = "\n"
    else:
        separator = input("Enter separator [\\n]: ") or "\n"

    err_file = Path(file_path).expanduser().absolute().read_text(encoding='utf-8', errors='ignore')
    prefix = input("Enter prefix prompt: ")
    prompts = [item for item in err_file.split(separator)]
    # Dynamically choose chunk size so we end up with <= 15 combined prompts.
    # If we already have 15 or fewer, keep them as-is.
    if len(prompts) <= 15:
        combined_prompts = prompts
    else:
        # Compute minimal chunk size so that number_of_chunks <= 15.
        # number_of_chunks = ceil(len(prompts)/chunk_size) <= 15
        # => chunk_size >= len(prompts)/15 -> choose ceil(len/15)
        from math import ceil
        chunk_size = ceil(len(prompts) / 15)
        combined_prompts: list[str] = []
        for i in range(0, len(prompts), chunk_size):
            combined_prompts.append("\nTargeted Locations:\n".join(prompts[i:i+chunk_size]))
    combined_prompts = [prefix + "\n" + item for item in combined_prompts]
    tab_config = launch_agents(repo_root=repo_root, prompts=combined_prompts)
    from machineconfig.utils.utils2 import randstr
    random_name = randstr(length=3)
    manager = ZellijLocalManager(session2zellij_tabs={"Agents": tab_config}, session_name_prefix=random_name)
    manager.start_all_sessions()
    manager.run_monitoring_routine()


if __name__ == "__main__":
    main()
