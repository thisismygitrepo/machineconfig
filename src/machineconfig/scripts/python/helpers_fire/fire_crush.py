
from pathlib import Path
# import shlex
from typing import Optional
from machineconfig.scripts.python.helpers_fire.fire_agents_helper_types import MATCHNE


def fire_crush(api_key: Optional[str], model: str, provider: str,
               prompt_path: Path, machine: MATCHNE, repo_root: Path) -> str:
    match machine:
        case "local":
            cmd = f"""
crush run {prompt_path}
"""
        case "docker":
            assert api_key is not None, "API key is required for Crush agent in docker mode."
            json_path = Path(__file__).parent / "fire_crush.json"
            json_template = json_path.read_text(encoding="utf-8")
            json_filled = json_template.replace("{api_key}", api_key).replace("{model}", model).replace("{provider}", provider)
            import tempfile
            config_file = tempfile.mkstemp(suffix=".json")[1]
            Path(config_file).write_text(json_filled, encoding="utf-8")            
            cmd = f"""

#   -e "PATH_PROMPT=$PATH_PROMPT"
#   opencode --model "{provider}/{model}" run {prompt_path}


echo "Running prompt @ {prompt_path.relative_to(repo_root)} using Docker with Crush..."
docker run -it --rm \
  -v "{repo_root}:/workspace/{repo_root.name}" \
  -v "{config_file}:$HOME/.local/share/crush/crush.json" \
  -w "/workspace/{repo_root.name}" \
  statistician/alim-slim:latest \
  crush run {prompt_path.relative_to(repo_root)}

"""
    return cmd
