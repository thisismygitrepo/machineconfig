

from pathlib import Path
# import shlex
from machineconfig.scripts.python.helpers_agents.fire_agents_helper_types import AI_SPEC

def fire_cursor(ai_spec: AI_SPEC, prompt_path: Path) -> str:
    match ai_spec["machine"]:
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