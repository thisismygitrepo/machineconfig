"""Utilitfrom pathlib import Path
from typing import cast, get_args, Iterable, Optional, TypeAlias, Literal
import json
import typer

from machineconfig.scripts.python.fire_agents_help_launch import prep_agent_launch, get_agents_launch_layout, AGENTS
from machineconfig.scripts.python.fire_agents_help_search import search_files_by_pattern, search_python_files
from machineconfig.scripts.python.fire_agents_load_balancer import chunk_prompts
from machineconfig.utils.accessories import get_repo_rootch multiple AI agent prompts in a Zellij session.

Improved design notes:
  * Clear separation of: input collection, prompt preparation, agent launch.
  * Configurable max agent cap (default 15) with interactive confirmation if exceeded.
  * Added type aliases + docstrings for maintainability.
  * Preserves original core behavior & command generation for each agent type.
"""

from pathlib import Path
from typing import cast, Iterable, Optional, TypeAlias, Literal, get_args
import json
import time
import typer

from machineconfig.scripts.python.fire_agents_help_launch import prep_agent_launch, get_agents_launch_layout, AGENTS
from machineconfig.scripts.python.fire_agents_help_search import search_files_by_pattern, search_python_files
from machineconfig.scripts.python.fire_agents_load_balancer import chunk_prompts
from machineconfig.utils.schemas.layouts.layout_types import LayoutsFile
from machineconfig.utils.accessories import get_repo_root

SEARCH_STRATEGIES: TypeAlias = Literal["file_path", "keyword_search", "filename_pattern"]

app = typer.Typer()


def _write_list_file(target: Path, files: Iterable[Path]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(str(f) for f in files), encoding="utf-8")


@app.command()
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
):
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
    agents_dir = prep_agent_launch(repo_root=repo_root, prompts_material=prompt_material_re_splitted, keep_material_in_separate_file=keep_material_in_separate_file_input, prompt_prefix=prompt_prefix, agent=agent_selected, job_name=job_name)
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
    layout_output_path.write_text(data=json.dumps(layoutfile, indent=4), encoding="utf-8")
    typer.echo(f"Created agents in {agents_dir}")


@app.command()
def run(layout_path: Path = typer.Argument(..., help="Path to the layout.json file"),
        max_tabs: int = typer.Option(6, help="Maximum number of tabs to launch"),
        sleep_between_layouts: float = typer.Option(1.0, help="Sleep time in seconds between launching layouts")):
    layoutfile: LayoutsFile = json.loads(layout_path.read_text())
    if len(layoutfile["layouts"][0]["layoutTabs"]) > max_tabs:
        typer.echo(f"Too many tabs (>{max_tabs}) to launch. Skipping launch.")
        raise typer.Exit(0)
    from machineconfig.cluster.sessions_managers.zellij_local_manager import ZellijLocalManager
    for i, a_layouts in enumerate(layoutfile["layouts"]):
        manager = ZellijLocalManager(session_layouts=[a_layouts])
        manager.start_all_sessions(poll_interval=2, poll_seconds=2)
        manager.run_monitoring_routine(wait_ms=2000)
        if i < len(layoutfile["layouts"]) - 1:  # Don't sleep after the last layout
            time.sleep(sleep_between_layouts)


@app.command(help="Adjust layout file to limit max tabs per layout, etc.")
def load_balance(layout_path: Path = typer.Argument(..., help="Path to the layout.json file"),
           max_thresh: int = typer.Option(..., help="Maximum tabs per layout"),
           thresh_type: Literal['number', 'weight'] = typer.Option(..., help="Threshold type"),
           breaking_method: Literal['moreLayouts', 'combineTabs'] = typer.Option(..., help="Breaking method"),
           output_path: Optional[Path] = typer.Option(None, help="Path to write the adjusted layout.json file")):
    layoutfile: LayoutsFile = json.loads(layout_path.read_text())
    layout_configs = layoutfile["layouts"]
    from machineconfig.cluster.sessions_managers.utils.load_balancer import limit_tab_num
    new_layouts = limit_tab_num(layout_configs=layout_configs, max_thresh=max_thresh, threshold_type=thresh_type, breaking_method=breaking_method)
    layoutfile["layouts"] = new_layouts
    target_file = output_path if output_path is not None else layout_path.parent / f'{layout_path.stem}_adjusted_{max_thresh}_{thresh_type}_{breaking_method}.json'
    target_file.write_text(data=json.dumps(layoutfile, indent=4), encoding="utf-8")
    typer.echo(f"Adjusted layout saved to {target_file}")


if __name__ == "__main__":  # pragma: no cover
    app()
