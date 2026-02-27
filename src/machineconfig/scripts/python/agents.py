"""Agents management commands - lazy loading subcommands."""

from typing import Optional, get_args, Annotated, Literal
import typer
from machineconfig.scripts.python.helpers.helpers_agents.fire_agents_helper_types import AGENTS, HOST, PROVIDER


def agents_create(
    agent:        Annotated[AGENTS, typer.Option(..., "--agent", "-a", help="Agent type.")],
    model:        Annotated[str, typer.Option(..., "--model", "-m", help="Model to use.")],
    provider:     Annotated[Optional[PROVIDER], typer.Option(..., "--provider", "-v", help="Provider to use (if agent support many)")] = None,
    host:         Annotated[HOST, typer.Option(..., "--host", "-h", help=f"Machine to run agents on. One of {', '.join(get_args(HOST))}")] = "local",
    context:      Annotated[Optional[str], typer.Option(..., "--context", "-c", help="Context as a direct string. Mutually exclusive with --context-path.")] = None,
    context_path: Annotated[Optional[str], typer.Option(..., "--context-path", "-C", help="Path to the context file/folder, defaults to .ai/todo/")] = None,
    separator:    Annotated[str, typer.Option(..., "--separator", "-s", help="Separator for context")] = "\n",
    agent_load:   Annotated[int, typer.Option(..., "--agent-load", "-l", help="Number of tasks per prompt")] = 13,
    prompt:       Annotated[Optional[str], typer.Option(..., "--prompt", "-p", help="Prompt prefix as string")] = None,
    prompt_path:  Annotated[Optional[str], typer.Option(..., "--prompt-path", "-P", help="Path to prompt file")] = None,
    job_name:     Annotated[str, typer.Option(..., "--job-name", "-n", help="Job name")] = "AI_Agents",
    join_prompt_and_context:     Annotated[bool, typer.Option(..., "--joined-prompt-context", "-j", help="Join prompt file to the context.")] = False,
    output_path:  Annotated[Optional[str], typer.Option(..., "--output-path", "-o", help="Path to write the layout.json file")] = None,
    agents_dir:   Annotated[Optional[str], typer.Option(..., "--agents-dir", "-d", help="Directory to store agent files. If not provided, will be constructed automatically.")] = None,
) -> None:
    """Create agents layout file, ready to run."""
    from machineconfig.scripts.python.helpers.helpers_agents.agents_impl import agents_create as impl
    try:
        impl(agent=agent, host=host, model=model, provider=provider, context=context, context_path=context_path, separator=separator, agent_load=agent_load, prompt=prompt, prompt_path=prompt_path, job_name=job_name, join_prompt_and_context=join_prompt_and_context, output_path=output_path, agents_dir=agents_dir)
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e
    except RuntimeError as e:
        typer.echo(str(e))
        raise typer.Exit(1) from e
    
def collect(
    agent_dir: Annotated[str, typer.Argument(..., help="Path to the agent directory containing the prompts folder")],
    output_path: Annotated[str, typer.Argument(..., help="Path to write the concatenated material files")],
    separator: Annotated[str, typer.Option(..., help="Separator to use when concatenating material files")] = "\n",
    pattern: Annotated[Optional[str], typer.Option(..., help="Pattern to match material files (e.g., 'res.txt')")] = None,
) -> None:
    """Collect all material files from an agent directory and concatenate them."""
    from machineconfig.scripts.python.helpers.helpers_agents.agents_impl import collect as impl
    try:
        impl(agent_dir=agent_dir, output_path=output_path, separator=separator, pattern=pattern)
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e


def make_agents_command_template() -> None:
    """Create a template for fire agents."""
    from machineconfig.scripts.python.helpers.helpers_agents.agents_impl import make_agents_command_template as impl
    try:
        impl()
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e
    except RuntimeError as e:
        typer.echo(str(e))
        raise typer.Exit(1) from e


def init_config(
    root: Annotated[str, typer.Option(..., "--root", "-r", help="Root directory of the repository to initialize AI configs in. Defaults to current directory.")],
    agents: Annotated[str, typer.Option("--agent", "-a", help=f"AI agents to configure (comma-separated), default is all of them. {','.join(get_args(AGENTS))}")] = "",

    add_config: Annotated[bool, typer.Option("--add-config", "-c", help="Create private agent config files/directories")] = True,
    add_instructions: Annotated[bool, typer.Option("--add-instructions", "-i", help="Create agent instructions files (e.g. AGENTS.md)")] = True,
    add_scripts: Annotated[bool, typer.Option("--include-scripts", "-s", help="Create shared .ai/.scripts scaffold")] = False,
    add_vscode_tasks: Annotated[bool, typer.Option("--add-vscode-tasks", "-l",help="Add VS Code lint/type-check task only")]= False,

    add_to_gitignore: Annotated[bool, typer.Option("--add-gitignore", "-g", help="Track all files touched by init-config and add them to .gitignore")] = False,
) -> None:
    """Initialize AI configurations in the current repository."""
    from machineconfig.scripts.python.helpers.helpers_agents.agents_impl import init_config as impl

    try:
        from typing import cast
        if agents:
            frameworks__ = tuple(agent.strip() for agent in agents.split(",") if agent.strip())
            resolved: tuple[AGENTS, ...] = cast(tuple[AGENTS, ...], frameworks__)
        else:
            resolved = cast(tuple[AGENTS, ...], get_args(AGENTS))

        impl(
            root=root, frameworks=resolved,
            include_common=add_scripts,
            add_all_configs_to_gitignore=add_to_gitignore,
            add_lint_task=add_vscode_tasks,
            add_config=add_config,
            add_instructions=add_instructions,
        )
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e


def make_todo_files(
    pattern: Annotated[str, typer.Argument(help="Pattern or keyword to match files by")] = ".py",
    repo: Annotated[str, typer.Argument(help="Repository path. Can be any directory within a git repository.")] = ".",
    strategy: Annotated[Literal["name", "keywords"], typer.Option("-s", "--strategy", help="Strategy to filter files: 'name' for filename matching, 'keywords' for content matching")] = "name",
    exclude_init: Annotated[bool, typer.Option("-x", "--exclude-init", help="Exclude __init__.py files from the checklist")] = True,
    include_line_count: Annotated[bool, typer.Option("-l", "--line-count", help="Include line count column in the output")] = False,
    output_path: Annotated[str, typer.Option("-o", "--output-path", help="Base path for output files relative to repo root")] = ".ai/todo/files",
    format_type: Annotated[Literal["csv", "md", "txt"], typer.Option("-f", "--format", help="Output format: csv, md (markdown), or txt")] = "md",
    split_every: Annotated[Optional[int], typer.Option("--split-every", "-e", help="Split output into multiple files, each containing at most this many results")] = None,
    split_to: Annotated[Optional[int], typer.Option("--split-to", "-t", help="Split output into exactly this many files")] = None,
) -> None:
    """Generate checklist with Python and shell script files in the repository filtered by pattern."""
    from machineconfig.scripts.python.ai.utils.generate_files import make_todo_files as impl
    impl(pattern=pattern, repo=repo, strategy=strategy, exclude_init=exclude_init, include_line_count=include_line_count, output_path=output_path, format_type=format_type, split_every=split_every, split_to=split_to)


def create_symlink_command(
    num: Annotated[int, typer.Argument(help="Number of symlinks to create (1-5).")] = 5,
) -> None:
    """Create symlinks to repo_root at ~/code_copies/${repo_name}_copy_{i}."""
    from machineconfig.scripts.python.ai.utils.generate_files import create_symlink_command as impl
    impl(num=num)


def run(
    prompt: Annotated[Optional[str], typer.Argument(help="Prompt text (optional positional argument). If omitted, an empty prompt is used.")] = None,
    agent: Annotated[AGENTS, typer.Option(..., "--agent", "-a", help="Agent to launch.")] = "copilot",
    context: Annotated[Optional[str], typer.Option(..., "--context", "-c", help="Context string. Mutually exclusive with --context-path.")] = None,
    context_path: Annotated[Optional[str], typer.Option(..., "--context-path", "-C", help="Path to a context file. Mutually exclusive with --context.")] = None,
    context_yaml_path: Annotated[Optional[str], typer.Option(..., "--context-yaml-path", "-y", help="YAML file used for interactive context selection fallback. Auto-created with commented template if missing.")] = None,
    context_name: Annotated[Optional[str], typer.Option(..., "--context-name", "-n", help="YAML section key (supports dot-path, e.g. 'team.backend'). Used with --context-yaml-path or default context YAML.")] = None,
    where: Annotated[Literal["all", "a", "private", "p", "public", "b", "library", "l", "custom", "c"], typer.Option(..., "--where", "-w", help="Where to look for context YAML files when --context-yaml-path is not provided.")] = "all",
    show_prompts_yaml_format: Annotated[bool, typer.Option(..., "--show-format", "-Y", help="Show prompts YAML format guidance and resolved file path. If no prompt/context input is provided, exits after showing it.")] = False,
    edit: Annotated[bool, typer.Option(..., "--edit", "-e", help="Open prompts YAML in an editor (hx preferred, nano fallback). If no prompt/context input is provided, exits after editing.")] = False,
) -> None:
    """Run one prompt via selected agent."""
    from machineconfig.scripts.python.helpers.helpers_agents.agents_run_impl import run as impl
    try:
        impl(prompt=prompt, agent=agent, context=context, context_path=context_path, prompts_yaml_path=context_yaml_path, context_name=context_name, where=where, edit=edit, show_prompts_yaml_format=show_prompts_yaml_format)
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e


def create_helper(
    prompt: Annotated[str, typer.Argument(help="Prompt describing the helper script. You may override the runtime agent with `target-agent: <agent>` (or `--agent <agent>` in prompt text). If omitted, runtime agent defaults to this command's `--agent`.")],
    agent: Annotated[AGENTS, typer.Option(..., "--agent", "-a", help="External generator agent to launch. It writes the helper script and is also the default runtime `agents create --agent` unless prompt text overrides it.")],
    output_path: Annotated[Optional[str], typer.Option(..., "--output-path", "-o", help="Optional target path the generated helper script should be written to.")] = None,
    show_payload: Annotated[bool, typer.Option(..., "--show-payload", "-s", help="Render the full prompt/context payload sent to the external generator using rich Markdown syntax.")] = False,
) -> None:
    """Generate a helper script via an external generator agent; runtime `agents create --agent` is optional in prompt and otherwise defaults to this command's `--agent`."""
    from machineconfig.scripts.python.helpers.helpers_agents.agents_run_impl import create_helper as impl
    try:
        impl(prompt=prompt, agent=agent, output_path=output_path, show_payload=show_payload)
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e


def get_app() -> typer.Typer:
    agents_app = typer.Typer(help="🤖 AI Agents management subcommands", no_args_is_help=True, add_help_option=True, add_completion=False)
    sep = "\n"
    agents_full_help = f"""
<c> Create agents layout file, ready to run.
{sep}
PROVIDER options: {', '.join(get_args(PROVIDER))}
{sep}
AGENT options: {', '.join(get_args(AGENTS))}
"""
    agents_create.__doc__ = agents_full_help
    agents_app.command("create", no_args_is_help=True, help=agents_create.__doc__, short_help="<c> Create agents layout file, ready to run.")(agents_create)
    agents_app.command("c", no_args_is_help=True, help=agents_create.__doc__, hidden=True)(agents_create)
    agents_app.command(
        name="create-helper",
        no_args_is_help=True,
        help=create_helper.__doc__,
        short_help="<h> Ask one agent to write helper script; runtime agent can be overridden in prompt",
    )(create_helper)
    agents_app.command(name="h", no_args_is_help=True, help=create_helper.__doc__, hidden=True)(create_helper)
    agents_app.command("collect", no_args_is_help=True, help=collect.__doc__, short_help="<T> Collect all agent materials into a single file.")(collect)
    agents_app.command("T", no_args_is_help=True, help=collect.__doc__, hidden=True)(collect)
    agents_app.command("make-template", no_args_is_help=False, help=make_agents_command_template.__doc__, short_help="<t> Create a template for fire agents")(make_agents_command_template)
    agents_app.command("t", no_args_is_help=False, help=make_agents_command_template.__doc__, hidden=True)(make_agents_command_template)
    agents_app.command("make-config", no_args_is_help=True, help=init_config.__doc__, short_help="<g> Initialize AI configurations in the current repository")(init_config)
    agents_app.command("g", no_args_is_help=True, help=init_config.__doc__, hidden=True)(init_config)
    agents_app.command("make-todo", no_args_is_help=True, short_help="<d> Generate a markdown file listing all Python files in the repo")(make_todo_files)
    agents_app.command("d", no_args_is_help=True, hidden=True)(make_todo_files)
    agents_app.command(name="make-symlinks", no_args_is_help=True, short_help="<s> Create symlinks to the current repo in ~/code_copies/")(create_symlink_command)
    agents_app.command(name="s", no_args_is_help=True, hidden=True)(create_symlink_command)
    agents_app.command(name="run-prompt", no_args_is_help=True, short_help="<r> Run one prompt via selected agent")(run)
    agents_app.command(name="r", no_args_is_help=True, hidden=True)(run)
    return agents_app


def main() -> None:
    agents_app = get_app()
    agents_app()


if __name__ == "__main__":
    main()
