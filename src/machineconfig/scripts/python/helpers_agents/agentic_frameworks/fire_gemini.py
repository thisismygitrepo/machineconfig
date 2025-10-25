
from pathlib import Path
import shlex
from machineconfig.scripts.python.helpers_agents.fire_agents_helper_types import AI_SPEC


def fire_gemini(ai_spec: AI_SPEC, prompt_path: Path, repo_root: Path) -> str:
    _ = ai_spec["provider"]
    # model = "gemini-2.5-flash-lite"
    # model = None  # auto-select
    # if model is None:
    #     model_arg = ""
    # else:
    model_arg = f"--model {shlex.quote(ai_spec['model'])}"
    # Need a real shell for the pipeline; otherwise '| gemini ...' is passed as args to 'cat'
    safe_path = shlex.quote(str(prompt_path))

    match ai_spec["machine"]:
        case "local":
            # Export the environment variable so it's available to subshells
            if ai_spec["api_key"] is not None:
                define_api_key = f"""export GEMINI_API_KEY="{shlex.quote(ai_spec['api_key'])}" """
            else:
                define_api_key = "echo 'Warning: No GEMINI_API_KEY provided, hoping it is set in the environment.'"
            cmd = f"""
{define_api_key}
echo "Using Gemini API key $GEMINI_API_KEY"
gemini {model_arg} --yolo --prompt {safe_path}
"""
            

        case "docker":
            assert ai_spec["api_key"] is not None, "When using docker, api_key must be provided."
            cmd = f"""
docker run -it --rm \
  -e GEMINI_API_KEY="{ai_spec['api_key']}" \
  -v "{repo_root}:/workspace/{repo_root.name}" \
  -w "/workspace/{repo_root.name}" \
  statistician/machineconfig-ai:latest  \
  gemini --prompt "$PATH_PROMPT"
"""
    return cmd
