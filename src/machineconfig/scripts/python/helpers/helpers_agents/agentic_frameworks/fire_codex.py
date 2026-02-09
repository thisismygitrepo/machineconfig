from pathlib import Path
import shlex

from machineconfig.scripts.python.helpers.helpers_agents.fire_agents_helper_types import AI_SPEC


def fire_codex(ai_spec: AI_SPEC, prompt_path: Path, repo_root: Path) -> str:
    prompt_rel = prompt_path.relative_to(repo_root)
    safe_prompt_path = shlex.quote(str(prompt_rel))
    model_value = ai_spec["model"]
    model_arg = f"--model {shlex.quote(model_value)}" if model_value else ""
    base_cmd = f"codex exec {model_arg} - < {safe_prompt_path}".strip()

    api_key = ai_spec["api_spec"]["api_key"]
    if api_key is not None:
        api_key_env = f'export CODEX_API_KEY="{shlex.quote(api_key)}"'
        local_cmd = f"{api_key_env}\n{base_cmd}"
    else:
        local_cmd = f'echo "Warning: No CODEX_API_KEY provided, hoping it is set in the environment."\n{base_cmd}'

    match ai_spec["machine"]:
        case "local":
            cmd = f"""
{local_cmd}
"""
        case "docker":
            env_flag = f"-e CODEX_API_KEY={shlex.quote(api_key)}" if api_key is not None else ""
            safe_cmd = shlex.quote(base_cmd)
            cmd = f"""
docker run -it --rm \
  {env_flag} \
  -v "{repo_root}:/workspace/{repo_root.name}" \
  -w "/workspace/{repo_root.name}" \
  statistician/machineconfig-ai:latest \
  bash -lc {safe_cmd}
"""
    return cmd
