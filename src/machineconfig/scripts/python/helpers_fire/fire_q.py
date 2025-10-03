
from pathlib import Path
import shlex
from machineconfig.scripts.python.helpers_fire.fire_agents_helper_types import MATCHINE


def fire_q(api_key: str, prompt_path: Path, machine: MATCHINE) -> str:
    safe_path = shlex.quote(str(prompt_path))
    
    match machine:
        case "local":
            cmd = f"""
q chat --no-interactive --trust-all-tools {safe_path}
"""
        case "docker":
            cmd = f"""
q chat --no-interactive --trust-all-tools {safe_path}
"""
    return cmd
