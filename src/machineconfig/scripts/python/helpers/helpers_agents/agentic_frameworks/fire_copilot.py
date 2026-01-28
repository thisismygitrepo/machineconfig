from pathlib import Path
import shlex

from machineconfig.scripts.python.helpers.helpers_agents.fire_agents_helper_types import AI_SPEC


def fire_copilot(ai_spec: AI_SPEC, prompt_path: Path, repo_root: Path) -> str:
    prompt_rel = prompt_path.relative_to(repo_root)
    safe_prompt_path = shlex.quote(str(prompt_rel))
    model_value = ai_spec["model"]
    model_arg = f"--model {shlex.quote(model_value)}" if model_value else ""
    base_cmd = f"""copilot -p "$(cat {safe_prompt_path})" {model_arg} --allow-all-tools"""
    match ai_spec["machine"]:
        case "local":
            cmd = f"""
{base_cmd}
"""
        case "docker":
            safe_cmd = shlex.quote(base_cmd)
            cmd = f"""
docker run -it --rm \
  -v "{repo_root}:/workspace/{repo_root.name}" \
  -w "/workspace/{repo_root.name}" \
  statistician/machineconfig-ai:latest \
  bash -lc {safe_cmd}
"""
    return cmd
