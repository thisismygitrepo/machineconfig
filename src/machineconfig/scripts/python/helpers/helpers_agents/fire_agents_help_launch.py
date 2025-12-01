
import random
import shlex
from pathlib import Path
from machineconfig.scripts.python.helpers.helpers_agents.fire_agents_helper_types import AGENTS, AGENT_NAME_FORMATTER, HOST, PROVIDER, AI_SPEC, API_SPEC


def get_api_keys(provider: PROVIDER) -> list[API_SPEC]:
    from machineconfig.utils.io import read_ini
    config = read_ini(Path.home().joinpath(f"dotfiles/creds/llm/{provider}/api_keys.ini"))
    res: list[API_SPEC] = []
    for a_section_name in list(config.sections()):
        a_section = config[a_section_name]
        if "api_key" in a_section:
            api_key = a_section["api_key"].strip()
            if api_key:
                res.append(API_SPEC(
                    api_key=api_key,
                    api_name=a_section.get("api_name", ""),
                    api_label=a_section_name,
                    api_account=a_section.get("email", "")
                ))
    print(f"Found {len(res)} {provider} API keys configured.")
    return res


def prep_agent_launch(repo_root: Path, agents_dir: Path, prompts_material: list[str], prompt_prefix: str, keep_material_in_separate_file: bool,
                      machine: HOST, model: str, provider: PROVIDER, agent: AGENTS, *, job_name: str) -> None:
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
                api_spec = api_keys[idx % len(api_keys)] if len(api_keys) > 0 else None
                if api_spec is None:
                    raise ValueError("No API keys found for Google Gemini. Please configure them in dotfiles/creds/llm/google/api_keys.ini")
                ai_spec: AI_SPEC = AI_SPEC(provider=provider, model="gemini-2.5-pro", agent=agent, machine=machine, api_spec=api_spec)
                from machineconfig.scripts.python.helpers.helpers_agents.agentic_frameworks.fire_gemini import fire_gemini
                cmd = fire_gemini(ai_spec=ai_spec, prompt_path=prompt_path, repo_root=repo_root)
            case "cursor-agent":
                api_spec = API_SPEC(api_key=None, api_name="", api_label="", api_account="")
                ai_spec: AI_SPEC = AI_SPEC(provider=provider, model=model, agent=agent, machine=machine, api_spec=api_spec)
                from machineconfig.scripts.python.helpers.helpers_agents.agentic_frameworks.fire_cursor_agents import fire_cursor
                cmd = fire_cursor(ai_spec=ai_spec, prompt_path=prompt_path)
                raise NotImplementedError("Cursor agent is not implemented yet, api key missing")
            case "crush":
                api_keys = get_api_keys(provider=provider)
                api_spec = api_keys[idx % len(api_keys)] if len(api_keys) > 0 else None
                if api_spec is None:
                    raise ValueError("No API keys found for Crush. Please configure them in dotfiles/creds/llm/crush/api_keys.ini")
                ai_spec: AI_SPEC = AI_SPEC(provider=provider, model=model, agent=agent, machine=machine, api_spec=api_spec)
                from machineconfig.scripts.python.helpers.helpers_agents.agentic_frameworks.fire_crush import fire_crush
                cmd = fire_crush(ai_spec=ai_spec, prompt_path=prompt_path, repo_root=repo_root)
            # case "q":
            #     from machineconfig.scripts.python.helpers.helpers_fire.fire_q import fire_q
            #     cmd = fire_q(api_key="", prompt_path=prompt_path, machine=machine)
            case _:
                raise ValueError(f"Unsupported agent type: {agent}")
        cmd_prefix += f"""
echo "Running with api label:   {ai_spec['api_spec']['api_label']}"
echo "Running with api acount:  {ai_spec['api_spec']['api_account']}"
echo "Running with api name:    {ai_spec['api_spec']['api_name']}"
echo "Running with api key:     {ai_spec['api_spec']['api_key']}"
"""
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

    import re
    all_dirs_under_prompts = sorted(all_dirs_under_prompts, key=lambda path: [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', path.name)])
    print(all_dirs_under_prompts)
    for a_prompt_dir in all_dirs_under_prompts:
        idx = a_prompt_dir.name.split("_")[-1]  # e.g., agent_0 -> 0
        agent_cmd_path = a_prompt_dir / AGENT_NAME_FORMATTER.format(idx=idx)
        fire_cmd = f"bash {shlex.quote(str(agent_cmd_path))}"
        tab_config.append(TabConfig(tabName=f"Agent{idx}", startDir=str(session_root.parent.parent.parent), command=fire_cmd))
    layout = LayoutConfig(layoutName="Agents", layoutTabs=tab_config)
    layouts_file: LayoutsFile = LayoutsFile(version="1.0", layouts=[layout])
    return layouts_file
