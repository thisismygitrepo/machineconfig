
from pathlib import Path
import shlex
from machineconfig.scripts.python.helpers_agents.fire_agents_helper_types import AI_SPEC


def fire_qwen(ai_spec: AI_SPEC, prompt_path: Path, repo_root: Path, config_dir: str | None) -> str:
    _ = ai_spec["provider"]
    safe_path = shlex.quote(str(prompt_path))
    match ai_spec["machine"]:
        case "local":
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
  statistician/machineconfig-ai:latest \
  qwen --prompt "$PATH_PROMPT"
"""
    return cmd
