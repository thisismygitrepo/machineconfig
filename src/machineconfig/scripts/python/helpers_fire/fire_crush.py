
from pathlib import Path
import shlex
from machineconfig.scripts.python.helpers_fire.fire_agents_helper_types import MATCHNE


def fire_crush(api_key: str, prompt_path: Path, machine: MATCHNE) -> str:
    safe_path = shlex.quote(str(prompt_path))
    
    match machine:
        case "local":
            cmd = f"""
crush run {safe_path}
"""
        case "docker":
            cmd = f"""
crush run {safe_path}
"""
    return cmd
