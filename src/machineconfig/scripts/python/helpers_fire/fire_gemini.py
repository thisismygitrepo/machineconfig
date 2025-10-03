
from pathlib import Path
import shlex
from machineconfig.scripts.python.helpers_fire.fire_agents_helper_types import MATCHNE
from typing import Optional


def fire_gemini(api_key: Optional[str], prompt_path: Path, machine: MATCHNE) -> str:
    model = "gemini-2.5-pro"
    # model = "gemini-2.5-flash-lite"
    # model = None  # auto-select
    # if model is None:
    #     model_arg = ""
    # else:
    model_arg = f"--model {shlex.quote(model)}"
    # Need a real shell for the pipeline; otherwise '| gemini ...' is passed as args to 'cat'
    safe_path = shlex.quote(str(prompt_path))

    match machine:
        case "local":
            # Export the environment variable so it's available to subshells
            cmd = f"""
export GEMINI_API_KEY={shlex.quote(api_key)}
echo "Using Gemini API key $GEMINI_API_KEY"
gemini {model_arg} --yolo --prompt {safe_path}
    """
        case "docker":
            cmd = """
docker run -it --rm \
  -e GEMINI_API_KEY="$GEMINI_API_KEY" \
  -v "/home/alex/code/machineconfig:/workspace/machineconfig" \
  -w "/workspace/machineconfig" \
  gemini-cli:latest \
  gemini --prompt "$PATH_PROMPT"
"""
    return cmd
            