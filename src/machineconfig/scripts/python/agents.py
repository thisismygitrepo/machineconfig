"""Utilitfrom pathlib import Path

"""

from pathlib import Path
from typing import cast, Iterable, Optional, get_args
import typer
from machineconfig.scripts.python.helpers_fire.fire_agents_helper_types import AGENTS


def _write_list_file(target: Path, files: Iterable[Path]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(str(f) for f in files), encoding="utf-8")


def create(
    context_path: Optional[Path] = typer.Option(None, help="Path to the context file"),
    keyword_search: Optional[str] = typer.Option(None, help="Keyword to search in Python files"),
    filename_pattern: Optional[str] = typer.Option(None, help="Filename pattern to match"),
    separator: str = typer.Option("\n", help="Separator for context"),
    tasks_per_prompt: int = typer.Option(13, help="Number of tasks per prompt"),
    agent: AGENTS = typer.Option(..., help=f"Agent type. One of {', '.join(get_args(AGENTS))}"),
    prompt: Optional[str] = typer.Option(None, help="Prompt prefix as string"),
    prompt_path: Optional[Path] = typer.Option(None, help="Path to prompt file"),
    job_name: str = typer.Option("AI_Agents", help="Job name"),
    keep_separate: bool = typer.Option(True, help="Keep prompt material in separate file to the context."),
    output_path: Optional[Path] = typer.Option(None, help="Path to write the layout.json file"),
    agents_dir: Optional[Path] = typer.Option(None, help="Directory to store agent files. If not provided, will be constructed automatically."),
):

    from machineconfig.scripts.python.helpers_fire.fire_agents_help_launch import prep_agent_launch, get_agents_launch_layout
    from machineconfig.scripts.python.helpers_fire.fire_agents_help_search import search_files_by_pattern, search_python_files
    from machineconfig.scripts.python.helpers_fire.fire_agents_load_balancer import chunk_prompts
    from machineconfig.utils.accessories import get_repo_root, randstr
    import json

    # validate mutual exclusive
    context_options = [context_path, keyword_search, filename_pattern]
    provided_context = [opt for opt in context_options if opt is not None]
    if len(provided_context) != 1:
        raise typer.BadParameter("Exactly one of --context-path, --keyword-search, --filename-pattern must be provided")
    
    prompt_options = [prompt, prompt_path]
    provided_prompt = [opt for opt in prompt_options if opt is not None]
    if len(provided_prompt) != 1:
        raise typer.BadParameter("Exactly one of --prompt or --prompt-path must be provided")
    
    repo_root = get_repo_root(Path.cwd())
    if repo_root is None:
        typer.echo("💥 Could not determine the repository root. Please run this script from within a git repository.")
        raise typer.Exit(1)
    typer.echo(f"Operating @ {repo_root}")
    
    search_strategy = ""
    prompt_material_path = Path("")
    
    if context_path is not None:
        search_strategy = "file_path"
        target_file_path = context_path.expanduser().resolve()
        if not target_file_path.exists() or not target_file_path.is_file():
            raise typer.BadParameter(f"Invalid file path: {target_file_path}")
        prompt_material_path = target_file_path
    elif keyword_search is not None:
        search_strategy = "keyword_search"
        matching_files = search_python_files(repo_root, keyword_search)
        if not matching_files:
            typer.echo(f"💥 No .py files found containing keyword: {keyword_search}")
            raise typer.Exit(1)
        target_file_path = repo_root / ".ai" / "target_file.txt"
        _write_list_file(target_file_path, matching_files)
        prompt_material_path = target_file_path
    elif filename_pattern is not None:
        search_strategy = "filename_pattern"
        matching_files = search_files_by_pattern(repo_root, filename_pattern)
        if not matching_files:
            typer.echo(f"💥 No files found matching pattern: {filename_pattern}")
            raise typer.Exit(1)
        target_file_path = repo_root / ".ai" / "target_file.txt"
        _write_list_file(target_file_path, matching_files)
        prompt_material_path = target_file_path
    
    if prompt_path is not None:
        prompt_prefix = prompt_path.read_text(encoding="utf-8")
    else:
        prompt_prefix = cast(str, prompt)
    agent_selected = agent
    keep_material_in_separate_file_input = keep_separate
    prompt_material_re_splitted = chunk_prompts(prompt_material_path, tasks_per_prompt=tasks_per_prompt, joiner=separator)
    if agents_dir is None: agents_dir = repo_root / ".ai" / f"tmp_prompts/{job_name}_{randstr()}"
    else:
        import shutil
        if agents_dir.exists():
            shutil.rmtree(agents_dir)
    prep_agent_launch(agents_dir=agents_dir, prompts_material=prompt_material_re_splitted, keep_material_in_separate_file=keep_material_in_separate_file_input, prompt_prefix=prompt_prefix, agent=agent_selected, job_name=job_name)
    layoutfile = get_agents_launch_layout(session_root=agents_dir)    
    regenerate_py_code = f"""
#!/usr/bin/env uv run --python 3.13 --with machineconfig
#!/usr/bin/env uv run --no-dev --project $HOME/code/machineconfig
fire_agents create --context-path "{prompt_material_path}" \\
    --{search_strategy} "{context_path or keyword_search or filename_pattern}" \\
    --prompt-path "{prompt_path or ''}" \\
    --agent "{agent_selected}" \\
    --job-name "{job_name}" \\
    --tasks-per-prompt {tasks_per_prompt} \\
    --separator "{separator}" \\
    {"--keep-separate" if keep_material_in_separate_file_input else ""}
"""
    (agents_dir / "aa_agents_relaunch.py").write_text(data=regenerate_py_code, encoding="utf-8")
    layout_output_path = output_path if output_path is not None else agents_dir / "layout.json"
    layout_output_path.parent.mkdir(parents=True, exist_ok=True)
    layout_output_path.write_text(data=json.dumps(layoutfile, indent=4), encoding="utf-8")
    typer.echo(f"Created agents in {agents_dir}")
    typer.echo(f"Ceated layout in {layout_output_path}")


def collect(
    agent_dir: Path = typer.Argument(..., help="Path to the agent directory containing the prompts folder"),
    output_path: Path = typer.Argument(..., help="Path to write the concatenated material files"),
    separator: str = typer.Option("\n", help="Separator to use when concatenating material files"),
) -> None:
    """Collect all material files from an agent directory and concatenate them."""
    if not agent_dir.exists() or not agent_dir.is_dir():
        raise typer.BadParameter(f"Agent directory does not exist or is not a directory: {agent_dir}")
    
    prompts_dir = agent_dir / "prompts"
    if not prompts_dir.exists():
        raise typer.BadParameter(f"Prompts directory not found: {prompts_dir}")
    
    material_files = []
    for agent_subdir in prompts_dir.iterdir():
        if agent_subdir.is_dir() and agent_subdir.name.startswith("agent_"):
            material_file = agent_subdir / f"{agent_subdir.name}_material.txt"
            if material_file.exists():
                material_files.append(material_file)
    
    if not material_files:
        typer.echo("No material files found in the agent directory.")
        return
    
    # Sort by agent index for consistent ordering
    material_files.sort(key=lambda x: int(x.parent.name.split("_")[-1]))
    
    # Read and concatenate all material files
    concatenated_content = []
    for material_file in material_files:
        content = material_file.read_text(encoding="utf-8")
        concatenated_content.append(content)
    
    result = separator.join(concatenated_content)
    
    # Write to output file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result, encoding="utf-8")
    typer.echo(f"Concatenated material written to {output_path}")


def template():
    template_bash = """#!/bin/bash
JOB_NAME="outpatient_mapping"
REPO_ROOT="$HOME/code/work/winter_planning/"
CONTEXT_PATH="$REPO_ROOT/data/outpatient_mapping/op_services_collected.csv"
PROMPT_PATH="$REPO_ROOT/data/outpatient_mapping/prompt"

AGENTS_DIR="$REPO_ROOT/.ai/agents/$JOB_NAME"
LAYOUT_PATH="$REPO_ROOT/.ai/agents/$JOB_NAME/layout_unbalanced.json"
LAYOUT_BALANCED_PATH="$REPO_ROOT/.ai/agents/$JOB_NAME/layout_balanced.json"

agents create --context-path $CONTEXT_PATH --tasks-per-prompt 10 --agent crush --prompt-path $PROMPT_PATH --keep-separate --output-path $LAYOUT_PATH --agents-dir $AGENTS_DIR
sessions balance-load $LAYOUT_PATH --max-thresh 6 --breaking-method moreLayouts --thresh-type number  --output-path $LAYOUT_BALANCED_PATH

sessions run $LAYOUT_BALANCED_PATH --kill-upon-completion
agents collect $AGENTS_DIR "$REPO_ROOT/.ai/agents/$JOB_NAME/collected.txt"
"""
    template_powershell = """

"""
    from platform import system
    if system() == "Linux":
        template = template_bash
    elif system() == "Windows":
        template = template_powershell
    else:
        raise typer.BadParameter(f"Unsupported OS: {system()}")

    from machineconfig.utils.accessories import get_repo_root
    repo_root = get_repo_root(Path.cwd())
    if repo_root is None:
        typer.echo("💥 Could not determine the repository root. Please run this script from within a git repository.")
        raise typer.Exit(1)
    save_path = repo_root / ".ai" / "agents" / "template_fire_agents.sh"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.write_text(template, encoding="utf-8")
    typer.echo(f"Template bash script written to {save_path}")


def main_from_parser():
    import sys
    agents_app = typer.Typer(help="🤖 AI Agents management subcommands")
    agents_app.command("create")(create)
    agents_app.command("collect")(collect)
    agents_app.command("template")(template)
    if len(sys.argv) == 1:
        agents_app(["--help"])
    else:
        agents_app()


if __name__ == "__main__":  # pragma: no cover
    pass
