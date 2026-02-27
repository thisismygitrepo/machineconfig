from pathlib import Path
from platform import system
from typing import Any, Optional, cast, get_args
import json
import shlex
from machineconfig.utils.accessories import randstr

from machineconfig.scripts.python.helpers.helpers_agents.fire_agents_helper_types import AGENTS


def _normalize_agent_name(agent: str) -> AGENTS:
    raw = agent.strip().lower()
    normalized = "copilot" if raw == "copilit" else raw
    supported_agents = get_args(AGENTS)
    if normalized not in supported_agents:
        supported = ", ".join(supported_agents)
        raise ValueError(f"Unsupported agent '{agent}'. Supported agents: {supported}")
    return cast(AGENTS, normalized)


def _extract_yaml_options(raw_data: Any) -> tuple[dict[str, str], dict[str, str]]:
    preview_map: dict[str, str] = {}
    context_map: dict[str, str] = {}

    def _to_text(value: Any) -> str:
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False, indent=2)

    if isinstance(raw_data, dict):
        for key, value in raw_data.items():
            label = str(key)
            as_text = _to_text(value)
            preview_map[label] = as_text
            context_map[label] = as_text
    elif isinstance(raw_data, list):
        for idx, item in enumerate(raw_data):
            label = f"prompt_{idx + 1}"
            as_text = _to_text(item)
            preview_map[label] = as_text
            context_map[label] = as_text
    else:
        as_text = _to_text(raw_data)
        preview_map["prompt_1"] = as_text
        context_map["prompt_1"] = as_text

    return preview_map, context_map


def _resolve_context(context: Optional[str], context_path: Optional[str], prompts_yaml_path: Optional[str]) -> str:
    if context is not None and context_path is not None:
        raise ValueError("Provide only one of --context or --context-path")

    if context is not None:
        return context

    if context_path is not None:
        context_file = Path(context_path).expanduser().resolve()
        if not context_file.exists() or not context_file.is_file():
            raise ValueError(f"--context-path must point to an existing file: {context_file}")
        return context_file.read_text(encoding="utf-8")

    yaml_path = Path(prompts_yaml_path).expanduser().resolve() if prompts_yaml_path is not None else Path.home() / "dotfiles" / "scripts" / "prompts" / "prompts.yaml"
    if not yaml_path.exists() or not yaml_path.is_file():
        raise ValueError(f"prompts YAML file does not exist: {yaml_path}")

    from machineconfig.utils.files.read import Read
    from machineconfig.utils.options_utils.tv_options import choose_from_dict_with_preview

    yaml_data = Read.yaml(yaml_path)
    preview_map, context_map = _extract_yaml_options(yaml_data)
    if len(preview_map) == 0:
        raise ValueError(f"No prompt entries found in {yaml_path}")

    chosen_key = choose_from_dict_with_preview(options_to_preview_mapping=preview_map, extension="yaml", multi=False, preview_size_percent=45.0)
    if chosen_key is None:
        raise SystemExit(1)
    return context_map[chosen_key]


def _quote_for_shell(value: str, is_windows: bool) -> str:
    if is_windows:
        return "'" + value.replace("'", "''") + "'"
    return shlex.quote(value)


def _make_prompt_file(prompt: str, context: str) -> Path:
    prompt_file = Path.home().joinpath("tmp_results", "tmp_files", "agents", f"run_prompt_{randstr()}.txt")
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    payload = f"""Prompt:
{prompt}

Context:
{context}
"""
    prompt_file.write_text(payload, encoding="utf-8")
    return prompt_file


def _build_agent_command(agent: AGENTS, prompt_file: Path) -> str:
    is_windows = system() == "Windows"
    prompt_file_q = _quote_for_shell(str(prompt_file), is_windows=is_windows)

    if is_windows:
        prompt_content_expr = f"(Get-Content -Raw {prompt_file_q})"
    else:
        prompt_content_expr = f'"$(cat {prompt_file_q})"'

    match agent:
        case "copilot":
            return f"copilot -p {prompt_content_expr} --yolo"
        case "codex":
            if is_windows:
                return f"Get-Content -Raw {prompt_file_q} | codex exec -"
            return f"codex exec - < {prompt_file_q}"
        case "gemini":
            return f"gemini --yolo --prompt {prompt_file_q}"
        case "crush":
            return f"crush run {prompt_file_q}"
        case _:
            raise ValueError(f"Agent '{agent}' is not yet wired for direct run command. Supported: copilot, codex, gemini, crush")


def run(prompt: str, agent: str, context: Optional[str], context_path: Optional[str], prompts_yaml_path: Optional[str]) -> None:
    resolved_agent = _normalize_agent_name(agent)
    resolved_context = _resolve_context(context=context, context_path=context_path, prompts_yaml_path=prompts_yaml_path)
    prompt_file = _make_prompt_file(prompt=prompt, context=resolved_context)
    command_line = _build_agent_command(agent=resolved_agent, prompt_file=prompt_file)

    from machineconfig.utils.code import exit_then_run_shell_script
    exit_then_run_shell_script(script=command_line, strict=False)
