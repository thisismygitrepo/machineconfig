"""Utilitfrom pathlib import Path

"""

from pathlib import Path
from typing import cast, Iterable, Optional, get_args
import typer
from machineconfig.scripts.python.helpers_fire.fire_agents_helper_types import AGENTS, MATCHINE, MODEL, PROVIDER


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
    machine: MATCHINE = typer.Option(..., help=f"Machine to run agents on. One of {', '.join(get_args(MATCHINE))}"),
    model: MODEL = typer.Option(..., help=f"Model to use (for crush agent). One of {', '.join(get_args(MODEL))}"),
    provider: PROVIDER = typer.Option(..., help=f"Provider to use (for crush agent). One of {', '.join(get_args(PROVIDER))}"),

    prompt: Optional[str] = typer.Option(None, help="Prompt prefix as string"),
    prompt_path: Optional[Path] = typer.Option(None, help="Path to prompt file"),
    job_name: str = typer.Option("AI_Agents", help="Job name"),
    separate_prompt_from_context: bool = typer.Option(True, help="Keep prompt material in separate file to the context."),
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
    keep_material_in_separate_file_input = separate_prompt_from_context
    prompt_material_re_splitted = chunk_prompts(prompt_material_path, tasks_per_prompt=tasks_per_prompt, joiner=separator)
    if agents_dir is None: agents_dir = repo_root / ".ai" / f"tmp_prompts/{job_name}_{randstr()}"
    else:
        import shutil
        if agents_dir.exists():
            shutil.rmtree(agents_dir)
    prep_agent_launch(repo_root=repo_root, agents_dir=agents_dir, prompts_material=prompt_material_re_splitted,
                      keep_material_in_separate_file=keep_material_in_separate_file_input,
                      prompt_prefix=prompt_prefix, machine=machine, agent=agent_selected, model=model, provider=provider,
                      job_name=job_name)
    layoutfile = get_agents_launch_layout(session_root=agents_dir)    
    regenerate_py_code = f"""
#!/usr/bin/env uv run --python 3.14 --with machineconfig
agents create --context-path "{prompt_material_path}" \\
    --{search_strategy} "{context_path or keyword_search or filename_pattern}" \\
    --prompt-path "{prompt_path or ''}" \\
    --agent "{agent_selected}" \\
    --machine "{machine}" \\
    --job-name "{job_name}" \\
    --tasks-per-prompt {tasks_per_prompt} \\
    --separator "{separator}" \\
    {"--separate-prompt-from-context" if keep_material_in_separate_file_input else ""}
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
    from platform import system
    import machineconfig.scripts.python.helpers_fire as module
    if system() == "Linux" or system() == "Darwin":
        template_path = Path(module.__file__).parent / "template.sh"
    elif system() == "Windows":
        template_path = Path(module.__file__).parent / "template.ps1"
    else:
        raise typer.BadParameter(f"Unsupported OS: {system()}")

    from machineconfig.utils.accessories import get_repo_root
    repo_root = get_repo_root(Path.cwd())
    if repo_root is None:
        typer.echo("💥 Could not determine the repository root. Please run this script from within a git repository.")
        raise typer.Exit(1)
    save_path = repo_root / ".ai" / "agents" / "template_fire_agents.sh"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.write_text(template_path.read_text(encoding="utf-8"), encoding="utf-8")
    typer.echo(f"Template bash script written to {save_path}")


def init_config():
    from machineconfig.scripts.python.ai.initai import add_ai_configs
    add_ai_configs(repo_root=Path.cwd())

def generate_files():
    from machineconfig.scripts.python.ai.generate_files import main
    main()

def main_from_parser():
    import sys
    agents_app = typer.Typer(help="🤖 AI Agents management subcommands")
    agents_app.command("create", no_args_is_help=True, help="Create agents layout file, ready to run.")(create)
    agents_app.command("collect", no_args_is_help=True, help="Collect all agent materials into a single file.")(collect)
    agents_app.command("make-template", no_args_is_help=False, help="Create a template for fire agents")(template)
    agents_app.command("make-config", no_args_is_help=False, help="Initialize AI configurations in the current repository")(init_config)
    agents_app.command("make-todo", no_args_is_help=False, help="Generate a markdown file listing all Python files in the repo")(generate_files)
    if len(sys.argv) == 1:
        agents_app(["--help"])
    else:
        agents_app()


if __name__ == "__main__":  # pragma: no cover
    pass
