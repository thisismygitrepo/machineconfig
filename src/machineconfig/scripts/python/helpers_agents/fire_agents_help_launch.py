
import random
import shlex
from pathlib import Path
from machineconfig.scripts.python.helpers_agents.fire_agents_helper_types import AGENTS, AGENT_NAME_FORMATTER, HOST, PROVIDER, MODEL


def get_api_keys(provider: PROVIDER) -> list[str]:
    from machineconfig.utils.io import read_ini
    config = read_ini(Path.home().joinpath(f"dotfiles/creds/llm/{provider}/api_keys.ini"))
    res: list[str] = []
    for a_section_name in list(config.sections()):
        a_section = config[a_section_name]
        if "api_key" in a_section:
            api_key = a_section["api_key"].strip()
            if api_key:
                res.append(api_key)
    print(f"Found {len(res)} {provider} API keys configured.")
    return res


def prep_agent_launch(repo_root: Path, agents_dir: Path, prompts_material: list[str], prompt_prefix: str, keep_material_in_separate_file: bool,
                      machine: HOST, model: MODEL, provider: PROVIDER, agent: AGENTS, *, job_name: str) -> None:
    agents_dir.mkdir(parents=True, exist_ok=True)
    prompt_folder = agents_dir / "prompts"
    prompt_folder.mkdir(parents=True, exist_ok=True)

    for idx, a_prompt_material in enumerate(prompts_material):
        prompt_root = prompt_folder / f"agent_{idx}"
        prompt_root.mkdir(parents=True, exist_ok=True)
        prompt_path = prompt_root / f"agent_{idx}_prompt.txt"
        if keep_material_in_separate_file:
            prompt_material_path = prompt_root / f"agent_{idx}_material.txt"
            prompt_material_path.write_text(a_prompt_material, encoding="utf-8")
            prompt_path.write_text(prompt_prefix + f"""\nPlease only look @ {prompt_material_path.relative_to(repo_root)}. You don't need to do any other work beside the content of this material file.""", encoding="utf-8")
        else:
            prompt_material_path = prompt_path
            prompt_path.write_text(prompt_prefix + """\nPlease only look @ the following:\n""" + a_prompt_material, encoding="utf-8")

        agent_cmd_launch_path = prompt_root / AGENT_NAME_FORMATTER.format(idx=idx)  # e.g., agent_0_cmd.sh
        random_sleep_time = random.uniform(0, 5)
        cmd_prefix = f"""#!/usr/bin/env bash

echo "Using machine: {machine}, model: {model}, provider: {provider}, and agent: {agent}"
echo "{job_name}-{idx} CMD {agent_cmd_launch_path}"
echo "{job_name}-{idx} PROMPT {prompt_path}"
echo "{job_name}-{idx} CONTEXT {prompt_material_path}"
echo "Starting agent {agent} in 5 seconds... Press Ctrl+C to cancel."
# sleep 5
# timeout 3 copilot --banner

export FIRE_AGENTS_AGENT_NAME="{agent}"
export FIRE_AGENTS_JOB_NAME="{job_name}"
export FIRE_AGENTS_PROMPT_FILE="{prompt_path}"
export FIRE_AGENTS_MATERIAL_FILE="{prompt_material_path}"
export FIRE_AGENTS_AGENT_LAUNCHER="{agent_cmd_launch_path}"

echo "Sleeping for {random_sleep_time:.2f} seconds to stagger agent startups..."
sleep {random_sleep_time:.2f}
echo "--------START OF AGENT OUTPUT--------"
sleep 0.1

"""
        match agent:
            case "gemini":
                assert provider == "google", "Gemini agent only works with google provider."
                api_keys = get_api_keys(provider="google")
                api_key = api_keys[idx % len(api_keys)] if len(api_keys) > 0 else None
                from machineconfig.scripts.python.helpers_agents.agentic_frameworks.fire_gemini import fire_gemini
                cmd = fire_gemini(api_key=api_key, prompt_path=prompt_path, machine=machine, model="gemini-2.5-pro", provider="google", repo_root=repo_root)
            case "cursor-agent":
                from machineconfig.scripts.python.helpers_agents.agentic_frameworks.fire_cursor_agents import fire_cursor
                cmd = fire_cursor(prompt_path=prompt_path, machine=machine, api_key=None)
                raise NotImplementedError("Cursor agent is not implemented yet, api key missing")
            case "crush":
                from machineconfig.scripts.python.helpers_agents.agentic_frameworks.fire_crush import fire_crush
                api_keys = get_api_keys(provider=provider)
                api_key = api_keys[idx % len(api_keys)] if len(api_keys) > 0 else None
                cmd = fire_crush(api_key=api_key, prompt_path=prompt_path, machine=machine, repo_root=repo_root, model=model, provider=provider)
            # case "q":
            #     from machineconfig.scripts.python.helpers_fire.fire_q import fire_q
            #     cmd = fire_q(api_key="", prompt_path=prompt_path, machine=machine)
            case _:
                raise ValueError(f"Unsupported agent type: {agent}")

        cmd_postfix = """
sleep 0.1
echo "---------END OF AGENT OUTPUT---------"
"""
        agent_cmd_launch_path.write_text(cmd_prefix + cmd + cmd_postfix, encoding="utf-8")
    return None


def get_agents_launch_layout(session_root: Path):
    from machineconfig.utils.schemas.layouts.layout_types import TabConfig, LayoutConfig, LayoutsFile

    tab_config: list[TabConfig] = []
    prompt_root = session_root / "prompts"
    all_dirs_under_prompts = [d for d in prompt_root.iterdir() if d.is_dir()]
    for a_prompt_dir in all_dirs_under_prompts:
        idx = a_prompt_dir.name.split("_")[-1]  # e.g., agent_0 -> 0
        agent_cmd_path = a_prompt_dir / AGENT_NAME_FORMATTER.format(idx=idx)
        fire_cmd = f"bash {shlex.quote(str(agent_cmd_path))}"
        tab_config.append(TabConfig(tabName=f"Agent{idx}", startDir=str(session_root.parent.parent.parent), command=fire_cmd))
    layout = LayoutConfig(layoutName="Agents", layoutTabs=tab_config)
    layouts_file: LayoutsFile = LayoutsFile(version="1.0", layouts=[layout])
    return layouts_file
