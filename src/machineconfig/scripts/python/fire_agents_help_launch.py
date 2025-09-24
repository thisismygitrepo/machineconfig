from machineconfig.scripts.python.fire_agents import AGENTS, get_gemini_api_keys
from machineconfig.utils.schemas.layouts.layout_types import TabConfig
from machineconfig.utils.utils2 import randstr

import random
import shlex
from pathlib import Path

def _confirm(message: str, default_no: bool = False) -> bool:
    from rich.prompt import Confirm
    return Confirm.ask(message, default=not default_no)


def launch_agents(repo_root: Path, prompts: list[str], agent: AGENTS, *, max_agents: int) -> list[TabConfig]:
    """Create tab configuration for a set of agent prompts.

    If number of prompts exceeds max_agents, ask user for confirmation.
    (Original behavior raised an error; now interactive override.)
    """
    if not prompts:
        raise ValueError("No prompts provided")

    if len(prompts) > max_agents:
        proceed = _confirm(message=(f"You are about to launch {len(prompts)} agents which exceeds the cap ({max_agents}). Proceed?"), default_no=True)
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