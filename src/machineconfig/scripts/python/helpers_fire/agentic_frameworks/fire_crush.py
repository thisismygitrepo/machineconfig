
from pathlib import Path
# import shlex
from typing import Optional
from machineconfig.scripts.python.helpers_fire.fire_agents_helper_types import HOST, PROVIDER, MODEL


def fire_crush(api_key: Optional[str], model: MODEL, provider: PROVIDER, machine: HOST, prompt_path: Path, repo_root: Path) -> str:
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
            temp_config_file_local = tempfile.mkstemp(suffix=".json")[1]
            Path(temp_config_file_local).write_text(json_filled, encoding="utf-8")            
            cmd = f"""

#   -e "PATH_PROMPT=$PATH_PROMPT"
#   opencode --model "{provider}/{model}" run {prompt_path}


echo "Running prompt @ {prompt_path.relative_to(repo_root)} using Docker with Crush..."
docker run -it --rm \
  -v "{repo_root}:/workspace/{repo_root.name}" \
  -v "{temp_config_file_local}:/root/.local/share/crush/crush.json" \
  -w "/workspace/{repo_root.name}" \
  statistician/machineconfig:latest \
  bash -i -c "source ~/.bashrc && cd /workspace/{repo_root.name} && cat /root/.local/share/crush/crush.json && crush run 'Please act on contents of this prompt ./{prompt_path.relative_to(repo_root)}'"

"""
    return cmd
