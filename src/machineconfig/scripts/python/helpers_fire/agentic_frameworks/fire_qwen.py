
from pathlib import Path
import shlex
from machineconfig.scripts.python.helpers_fire.fire_agents_helper_types import HOST
from typing import Optional, Literal


def fire_qwen(config_dir: Optional[str], model: Literal["qwen"], provider: Literal["qwen"], machine: HOST, prompt_path: Path, repo_root: Path) -> str:
    # assert model == "qwen", "Only qwen is supported currently."
    # assert provider == "qwen", "Only qwen is supported currently."
    # model = "qwen"
    # model = "gemini-2.5-flash-lite"
    # model = None  # auto-select
    # if model is None:
    #     model_arg = ""
    # else:
    _ = provider
    # model_arg = f"--model {shlex.quote(model)}"
    # Need a real shell for the pipeline; otherwise '| gemini ...' is passed as args to 'cat'
    safe_path = shlex.quote(str(prompt_path))

    match machine:
        case "local":
            # Export the environment variable so it's available to subshells
            cmd = f"""
qwen --yolo --prompt {safe_path}
    """
        case "docker":
            assert config_dir is not None, "When using docker, config_dir must be provided."
            assert Path(config_dir).exists(), f"Provided config_dir {config_dir} does not exist."
            oauth_creds = Path(config_dir).joinpath("oauth_creds.json")
            settings = Path(config_dir).joinpath("settings.json")

            cmd = f"""
docker run -it --rm \
  -v "{repo_root}:/workspace/{repo_root.name}" \
  -v {shlex.quote(str(oauth_creds))}:/root/.qwen/oauth_creds.json \
  -v {shlex.quote(str(settings))}:/root/.qwen/settings.json \
  -w "/workspace/{repo_root.name}" \
  statistician/machineconfig:latest \
  qwen --prompt "$PATH_PROMPT"
"""
    return cmd
