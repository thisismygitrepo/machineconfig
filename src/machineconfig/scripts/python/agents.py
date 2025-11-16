"""Utilitfrom pathlib import Path

"""

from typing import cast, Optional, get_args, Annotated
import typer
from machineconfig.scripts.python.helpers_agents.fire_agents_helper_types import AGENTS, HOST, PROVIDER


def create(
    agent: Annotated[AGENTS, typer.Option(..., "--agents", "-a", help=f"Agent type. One of {', '.join(get_args(AGENTS)[:3])}")],
    host: Annotated[HOST, typer.Option(..., "--host", "-h", help=f"Machine to run agents on. One of {', '.join(get_args(HOST))}")],
    model: Annotated[str, typer.Option(..., "--model", "-m", help="Model to use (for crush agent).")],
    provider: Annotated[PROVIDER, typer.Option(..., "--provider", "-p", help=f"Provider to use (for crush agent). One of {', '.join(get_args(PROVIDER)[:3])}")],
    context_path: Annotated[Optional[str], typer.Option(..., "--context-path", "-c", help="Path to the context file/folder, defaults to .ai/todo/")] = None,
    separator: Annotated[str, typer.Option(..., "--separator", "-s", help="Separator for context")] = "\n",
    agent_load: Annotated[int, typer.Option(..., "--agent-load", "-al", help="Number of tasks per prompt")] = 13,
    prompt: Annotated[Optional[str], typer.Option(..., "--prompt", "-P", help="Prompt prefix as string")] = None,
    prompt_path: Annotated[Optional[str], typer.Option(..., "--prompt-path", "-pp", help="Path to prompt file")] = None,
    job_name: Annotated[str, typer.Option(..., "--job-name", "-j", help="Job name")] = "AI_Agents",
    separate: Annotated[bool, typer.Option(..., "--separate", "-S", help="Keep prompt material in separate file to the context.")] = True,
    output_path: Annotated[Optional[str], typer.Option(..., "--output-path", "-o", help="Path to write the layout.json file")] = None,
    agents_dir: Annotated[Optional[str], typer.Option(..., "--agents-dir", "-ad", help="Directory to store agent files. If not provided, will be constructed automatically.")] = None,
):

    from machineconfig.scripts.python.helpers_agents.fire_agents_help_launch import prep_agent_launch, get_agents_launch_layout
    from machineconfig.scripts.python.helpers_agents.fire_agents_load_balancer import chunk_prompts
    from machineconfig.utils.accessories import get_repo_root, randstr
    import json
    from pathlib import Path
    # validate mutual exclusive
    prompt_options = [prompt, prompt_path]
    provided_prompt = [opt for opt in prompt_options if opt is not None]
    if len(provided_prompt) != 1:
        raise typer.BadParameter("Exactly one of --prompt or --prompt-path must be provided")
    
    repo_root = get_repo_root(Path.cwd())
    if repo_root is None:
        typer.echo("💥 Could not determine the repository root. Please run this script from within a git repository.")
        raise typer.Exit(1)
        return
    typer.echo(f"Operating @ {repo_root}")
    
    if context_path is None:
        context_path_resolved = Path(repo_root) / ".ai" / "todo"
    else: context_path_resolved = Path(context_path).expanduser().resolve()

    if not context_path_resolved.exists():
        raise typer.BadParameter(f"Path does not exist: {context_path_resolved}")
    
    if context_path_resolved.is_file():
        prompt_material_re_splitted = chunk_prompts(context_path_resolved, tasks_per_prompt=agent_load, joiner=separator)
    elif context_path_resolved.is_dir():
        files = [f for f in context_path_resolved.rglob("*") if f.is_file()]
        if not files:
            raise typer.BadParameter(f"No files found in directory: {context_path_resolved}")
        concatenated = separator.join(f.read_text(encoding="utf-8") for f in files)
        prompt_material_re_splitted = [concatenated]
    else:
        raise typer.BadParameter(f"Path is neither file nor directory: {context_path_resolved}")
    
    if prompt_path is not None:
        prompt_prefix = Path(prompt_path).read_text(encoding="utf-8")
    else:
        prompt_prefix = cast(str, prompt)
    agent_selected = agent
    if agents_dir is None: agents_dir_obj = Path(repo_root) / ".ai" / f"tmp_prompts/{job_name}_{randstr()}"
    else:
        import shutil
        if Path(agents_dir).exists():
            shutil.rmtree(agents_dir)
        agents_dir_obj = Path(agents_dir)
    prep_agent_launch(repo_root=repo_root, agents_dir=agents_dir_obj, prompts_material=prompt_material_re_splitted,
                      keep_material_in_separate_file=separate,
                      prompt_prefix=prompt_prefix, machine=host, agent=agent_selected, model=model, provider=provider,
                      job_name=job_name)
    layoutfile = get_agents_launch_layout(session_root=agents_dir_obj)
    regenerate_py_code = f"""
#!/usr/bin/env uv run --python 3.14 --with machineconfig
agents create "{context_path_resolved}" \\
    --prompt-path "{prompt_path or ''}" \\
    --agent "{agent_selected}" \\
    --host "{host}" \\
    --job-name "{job_name}" \\
    --agent_load {agent_load} \\
    --separator "{separator}" \\
    {"--separate" if separate else ""}
"""
    (agents_dir_obj / "aa_agents_relaunch.sh").write_text(data=regenerate_py_code, encoding="utf-8")
    layout_output_path = Path(output_path) if output_path is not None else agents_dir_obj / "layout.json"
    layout_output_path.parent.mkdir(parents=True, exist_ok=True)
    layout_output_path.write_text(data=json.dumps(layoutfile, indent=4), encoding="utf-8")
    typer.echo(f"Created agents in {agents_dir_obj}")
    typer.echo(f"Ceated layout in {layout_output_path}")


def collect(
    agent_dir: Annotated[str, typer.Argument(..., help="Path to the agent directory containing the prompts folder")],
    output_path: Annotated[str, typer.Argument(..., help="Path to write the concatenated material files")],
    separator: Annotated[str, typer.Option(..., help="Separator to use when concatenating material files")] = "\n",
) -> None:
    """Collect all material files from an agent directory and concatenate them."""
    from pathlib import Path
    if not Path(agent_dir).exists() or not Path(agent_dir).is_dir():
        raise typer.BadParameter(f"Agent directory does not exist or is not a directory: {agent_dir}")
    
    prompts_dir = Path(agent_dir) / "prompts"
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
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(result, encoding="utf-8")
    typer.echo(f"Concatenated material written to {output_path}")


def make_agents_command_template():
    from platform import system
    import machineconfig.scripts.python.helpers_agents as module
    from pathlib import Path

    if system() == "Linux" or system() == "Darwin":
        template_path = Path(module.__file__).parent / "templates/template.sh"
    elif system() == "Windows":
        template_path = Path(module.__file__).parent / "templates/template.ps1"
    else:
        raise typer.BadParameter(f"Unsupported OS: {system()}")

    from machineconfig.utils.accessories import get_repo_root
    repo_root = get_repo_root(Path.cwd())
    if repo_root is None:
        typer.echo("💥 Could not determine the repository root. Please run this script from within a git repository.")
        raise typer.Exit(1)

    save_path_root = repo_root / ".ai" / "agents"

    save_path_root.mkdir(parents=True, exist_ok=True)
    save_path_root.joinpath("template_fire_agents.sh").write_text(template_path.read_text(encoding="utf-8"), encoding="utf-8")
    typer.echo(f"Template bash script written to {save_path_root}")

    from machineconfig.scripts.python.ai.utils.generate_files import make_todo_files
    make_todo_files(
        pattern=".py", repo=str(repo_root), strategy="name", output_path=str(save_path_root / "files.md"), split_every=None, split_to=None
    )

    prompt_path = Path(module.__file__).parent / "templates/prompt.txt"
    save_path_root.joinpath("prompt.txt").write_text(prompt_path.read_text(encoding="utf-8"), encoding="utf-8")
    typer.echo(f"Prompt template written to {save_path_root}")


def init_config():
    from machineconfig.scripts.python.ai.initai import add_ai_configs
    from pathlib import Path
    add_ai_configs(repo_root=Path.cwd())


def get_app():
    agents_app = typer.Typer(help="🤖 AI Agents management subcommands", no_args_is_help=True, add_help_option=False, add_completion=False)
    sep = "\n"
    agents_full_help = f"""
[c] Create agents layout file, ready to run.
{sep}
PROVIDER options: {', '.join(get_args(PROVIDER))}
{sep}
AGENT options: {', '.join(get_args(AGENTS))}
"""
    agents_app.command("create", no_args_is_help=True, help=agents_full_help)(create)
    agents_app.command("c", no_args_is_help=True, help="Create agents layout file, ready to run.", hidden=True)(create)
    agents_app.command("collect", no_args_is_help=True, help="[T] Collect all agent materials into a single file.")(collect)
    agents_app.command("T", no_args_is_help=True, help="Collect all agent materials into a single file.", hidden=True)(collect)
    agents_app.command("make-template", no_args_is_help=False, help="[t] Create a template for fire agents")(make_agents_command_template)
    agents_app.command("t", no_args_is_help=False, help="Create a template for fire agents", hidden=True)(make_agents_command_template)
    agents_app.command("make-config", no_args_is_help=False, help="[g] Initialize AI configurations in the current repository")(init_config)
    agents_app.command("g", no_args_is_help=False, help="Initialize AI configurations in the current repository", hidden=True)(init_config)
    from machineconfig.scripts.python.ai.utils.generate_files import make_todo_files
    agents_app.command("make-todo", no_args_is_help=True, help="[d] Generate a markdown file listing all Python files in the repo")(make_todo_files)
    agents_app.command("d", no_args_is_help=True, help="Generate a markdown file listing all Python files in the repo", hidden=True)(make_todo_files)
    from machineconfig.scripts.python.ai.utils.generate_files import create_symlink_command
    agents_app.command(name="make-symlinks", no_args_is_help=True, help="[s] Create symlinks to the current repo in ~/code_copies/")(create_symlink_command)
    agents_app.command(name="s", no_args_is_help=True, help="Create symlinks to the current repo in ~/code_copies/", hidden=True)(create_symlink_command)
    return agents_app


def main():
    agents_app = get_app()
    # from trogon.typer import init_tui
    # agents_app_tui = init_tui(agents_app)
    agents_app()
    # agents_app_tui()


if __name__ == "__main__":  # pragma: no cover
    pass
