from pathlib import Path
from platform import system
from typing import Optional, cast
import shlex
from machineconfig.utils.accessories import randstr

from machineconfig.scripts.python.helpers.helpers_agents.agents_run_context import (
    PROMPTS_WHERE,
    edit_prompts_yaml,
    ensure_prompts_yaml_exists,
    prompts_yaml_format_explanation,
    resolve_context,
    resolve_prompts_yaml_paths,
)
from machineconfig.scripts.python.helpers.helpers_agents.fire_agents_helper_types import AGENTS

def _quote_for_shell(value: str, is_windows: bool) -> str:
    if is_windows:
        return "'" + value.replace("'", "''") + "'"
    return shlex.quote(value)


def _make_prompt_file(prompt: str, context: str) -> Path:
    prompt_file = Path.home().joinpath("tmp_results", "tmp_files", "agents", f"run_prompt_{randstr()}.md")
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    payload = f"""# Context
{context}

# Prompt
{prompt}
"""
    prompt_file.write_text(payload, encoding="utf-8")
    return prompt_file


def _print_prompt_file_preview(prompt_file: Path) -> None:
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax

    payload = prompt_file.read_text(encoding="utf-8")
    console = Console()
    console.print(
        Panel(
            Syntax(code=payload, lexer="markdown", word_wrap=True),
            title=f"📄 Prompt file @ {prompt_file}",
            subtitle="Prompt + context sent to agent",
        ),
    )


def _make_create_helper_payload(
    user_prompt: str,
    output_path: Optional[str],
) -> str:
    output_target = output_path if output_path is not None else "./.ai/<helper_name>.sh"
    return f"""You are generating a helper shell script for this repository.

Goal:
- Create a real `.sh` helper file under `./.ai/` that helps user to run `agents create` big command.
- Mark the helper executable (for example `chmod +x`).
- Run the helper script after creating it.

User request:
{user_prompt}

Output path target:
{output_target}


Implementation constraints:
- Please run `agents create --help` by yourself to understand the command line interface.
- When user is not mentioning e.g. model, host, etc, then do not make assumptions. Just let the function use its defaults.
- use default values from `agents_create` where applicable, but adapt as needed to fit the user prompt.
- the signature of function clearly explains which kwargs have defaults and which ones must be passed.

"""


def build_agent_command(agent: AGENTS, prompt_file: Path) -> str:
    is_windows = system() == "Windows"
    prompt_file_q = _quote_for_shell(str(prompt_file), is_windows=is_windows)
    agent_cli = cast(str, agent)

    if is_windows:
        prompt_content_expr = f"(Get-Content -Raw {prompt_file_q})"
    else:
        prompt_content_expr = f'"$(cat {prompt_file_q})"'

    match agent:
        case "copilot":
            return f"{agent_cli} -p {prompt_content_expr} --yolo"
        case "codex":
            if is_windows:
                return f"Get-Content -Raw {prompt_file_q} | {agent_cli} exec -"
            return f"{agent_cli} exec - < {prompt_file_q}"
        case "gemini":
            return f"{agent_cli} --yolo --prompt {prompt_file_q}"
        case "crush":
            return f"{agent_cli} run {prompt_file_q}"
        case "claude":
            return f"{agent_cli} -p {prompt_content_expr}"
        case "qwen":
            return f"{agent_cli} --yolo --prompt {prompt_file_q}"
        case "q":
            return f"{agent_cli} chat {prompt_content_expr}"
        case "opencode":
            return f"{agent_cli} run {prompt_content_expr}"
        case "kilocode":
            return f"{agent_cli} {prompt_content_expr}"
        case "cline":
            return f"{agent_cli} --yolo {prompt_content_expr}"
        case "auggie":
            return f"{agent_cli} --print {prompt_content_expr}"
        case "warp-cli":
            return f"{agent_cli} agent run --prompt {prompt_content_expr}"
        case "droid":
            return f"{agent_cli} exec -f {prompt_file_q}"
        case "cursor-agent":
            return f"{agent_cli} -p {prompt_content_expr} --output-format text"


def run(
    prompt: Optional[str],
    agent: AGENTS,
    context: Optional[str],
    context_path: Optional[str],
    prompts_yaml_path: Optional[str],
    context_name: Optional[str],
    where: PROMPTS_WHERE,
    edit: bool,
    show_prompts_yaml_format: bool,
) -> None:
    yaml_locations = resolve_prompts_yaml_paths(prompts_yaml_path=prompts_yaml_path, where=where)
    created_yaml_paths: list[Path] = []
    for location_name, yaml_path in yaml_locations:
        # Keep previous behavior: always scaffold the default private path when available.
        should_create = prompts_yaml_path is not None or location_name == "private"
        if should_create and ensure_prompts_yaml_exists(yaml_path=yaml_path):
            created_yaml_paths.append(yaml_path)
    if len(created_yaml_paths) > 0:
        import typer
        for created_yaml_path in created_yaml_paths:
            typer.echo(f"Created prompts YAML template at: {created_yaml_path}")
    if edit:
        editable_locations = [(name, path) for name, path in yaml_locations if path.exists() and path.is_file()]
        for _, yaml_path in editable_locations:
            edit_prompts_yaml(yaml_path=yaml_path)
    if show_prompts_yaml_format:
        import typer
        typer.echo(prompts_yaml_format_explanation(yaml_paths=yaml_locations))
    has_explicit_context = context is not None or context_path is not None or context_name is not None
    if (edit or show_prompts_yaml_format) and prompt is None and not has_explicit_context:
        return
    resolved_context = resolve_context(context=context, context_path=context_path, prompts_yaml_path=prompts_yaml_path, context_name=context_name, where=where)
    prompt_text = prompt if prompt is not None else ""
    prompt_file = _make_prompt_file(prompt=prompt_text, context=resolved_context)
    _print_prompt_file_preview(prompt_file=prompt_file)
    command_line = build_agent_command(agent=agent, prompt_file=prompt_file)

    from machineconfig.utils.code import exit_then_run_shell_script
    exit_then_run_shell_script(script=command_line, strict=False)


def create_helper(prompt: str, agent: AGENTS, output_path: Optional[str], show_payload: bool = False) -> None:
    from machineconfig.utils.accessories import get_repo_root

    repo_root = get_repo_root(Path.cwd())
    if repo_root is None:
        raise ValueError("Could not determine repository root from current working directory")

    agents_module_path = repo_root / "src" / "machineconfig" / "scripts" / "python" / "agents.py"
    if not agents_module_path.exists() or not agents_module_path.is_file():
        raise ValueError(f"Could not locate agents module file: {agents_module_path}")

    generated_prompt = _make_create_helper_payload(
        user_prompt=prompt,
        output_path=output_path,
    )

    prompt_file = _make_prompt_file(prompt=generated_prompt, context="")
    if show_payload:
        _print_prompt_file_preview(prompt_file=prompt_file)
    command_line = build_agent_command(agent=agent, prompt_file=prompt_file)

    from machineconfig.utils.code import exit_then_run_shell_script

    exit_then_run_shell_script(script=command_line, strict=False)
