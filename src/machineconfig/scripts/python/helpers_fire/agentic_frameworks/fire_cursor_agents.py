

from pathlib import Path
# import shlex
from machineconfig.scripts.python.helpers_fire.fire_agents_helper_types import HOST
from typing import Optional

def fire_cursor(api_key: Optional[str], prompt_path: Path, machine: HOST) -> str:
    match machine:
        case "local":
            # Export the environment variable so it's available to subshells
            cmd = f"""

cursor-agent --print --output-format text {prompt_path}

"""
        case "docker":
            cmd = f"""

cursor-agent --print --output-format text {prompt_path}

"""
    return cmd