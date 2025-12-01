"""Fast-loading CLI entry point using lazy imports.

Submodules are only imported when their commands are actually invoked, not at startup.
This makes `mcfg --help` much faster by avoiding loading heavy dependencies.
"""
from typing import Optional, Annotated
import typer


def fire(
    ctx: typer.Context,
    path: Annotated[str, typer.Argument(help="Path to the Python file to run")] = ".",
    function: Annotated[Optional[str], typer.Argument(help="Function to run")] = None,
    ve: Annotated[str, typer.Option("--ve", "-v", help="Virtual environment name")] = "",
    cmd: Annotated[bool, typer.Option("--cmd", "-B", help="Create a cmd fire command to launch the job asynchronously")] = False,
    interactive: Annotated[bool, typer.Option("--interactive", "-i", help="Whether to run the job interactively using IPython")] = False,
    debug: Annotated[bool, typer.Option("--debug", "-d", help="Enable debug mode")] = False,
    choose_function: Annotated[bool, typer.Option("--choose-function", "-c", help="Choose function interactively")] = False,
    loop: Annotated[bool, typer.Option("--loop", "-l", help="Infinite recursion (runs again after completion/interruption)")] = False,
    jupyter: Annotated[bool, typer.Option("--jupyter", "-j", help="Open in a jupyter notebook")] = False,
    marimo: Annotated[bool, typer.Option("--marimo", "-M", help="Open in a marimo notebook")] = False,
    module: Annotated[bool, typer.Option("--module", "-m", help="Launch the main file")] = False,
    script: Annotated[bool, typer.Option("--script", "-s", help="Launch as a script without fire")] = False,
    optimized: Annotated[bool, typer.Option("--optimized", "-O", help="Run the optimized version of the function")] = False,
    zellij_tab: Annotated[Optional[str], typer.Option("--zellij-tab", "-z", help="Open in a new zellij tab")] = None,
    submit_to_cloud: Annotated[bool, typer.Option("--submit-to-cloud", "-C", help="Submit to cloud compute")] = False,
    remote: Annotated[bool, typer.Option("--remote", "-r", help="Launch on a remote machine")] = False,
    streamlit: Annotated[bool, typer.Option("--streamlit", "-S", help="Run as streamlit app")] = False,
    environment: Annotated[str, typer.Option("--environment", "-E", help="Choose ip, localhost, hostname or arbitrary url")] = "",
    holdDirectory: Annotated[bool, typer.Option("--holdDirectory", "-D", help="Hold current directory and avoid cd'ing to the script directory")] = False,
    PathExport: Annotated[bool, typer.Option("--PathExport", "-P", help="Augment the PYTHONPATH with repo root")] = False,
    git_pull: Annotated[bool, typer.Option("--git-pull", "-g", help="Start by pulling the git repo")] = False,
    watch: Annotated[bool, typer.Option("--watch", "-w", help="Watch the file for changes")] = False,
) -> None:
    """Fire and manage jobs."""
    from machineconfig.scripts.python.fire_jobs import fire as fire_impl
    fire_impl(ctx=ctx, path=path, function=function, ve=ve, cmd=cmd, interactive=interactive, debug=debug,
              choose_function=choose_function, loop=loop, jupyter=jupyter, marimo=marimo, module=module,
              script=script, optimized=optimized, zellij_tab=zellij_tab, submit_to_cloud=submit_to_cloud,
              remote=remote, streamlit=streamlit, environment=environment, holdDirectory=holdDirectory,
              PathExport=PathExport, git_pull=git_pull, watch=watch)


def ftpx(
    source: Annotated[str, typer.Argument(help="Source path (machine:path)")],
    target: Annotated[str, typer.Argument(help="Target path (machine:path)")],
    recursive: Annotated[bool, typer.Option("--recursive", "-r", help="Send recursively.")] = False,
    zipFirst: Annotated[bool, typer.Option("--zipFirst", "-z", help="Zip before sending.")] = False,
    cloud: Annotated[bool, typer.Option("--cloud", "-c", help="Transfer through the cloud.")] = False,
    overwrite_existing: Annotated[bool, typer.Option("--overwrite-existing", "-o", help="Overwrite existing files on remote when sending from local to remote.")] = False,
) -> None:
    """File transfer utility though SSH."""
    from machineconfig.scripts.python.ftpx import ftpx as ftpx_impl
    ftpx_impl(source=source, target=target, recursive=recursive, zipFirst=zipFirst, cloud=cloud, overwrite_existing=overwrite_existing)


def croshell(
    path: Annotated[Optional[str], typer.Argument(help="path of file to read.")] = None,
    project_path: Annotated[Optional[str], typer.Option("--project", "-p", help="specify uv project to use")] = None,
    uv_with: Annotated[Optional[str], typer.Option("--uv-with", "-w", help="specify uv with packages to use")] = None,
    marimo: Annotated[bool, typer.Option("--marimo", "-m", help="open the notebook using marimo if available")] = False,
    jupyter: Annotated[bool, typer.Option("--jupyter", "-j", help="run in jupyter interactive console")] = False,
    vscode: Annotated[bool, typer.Option("--vscode", "-c", help="open the script in vscode")] = False,
    visidata: Annotated[bool, typer.Option("--visidata", "-v", help="open data file in visidata")] = False,
    python: Annotated[bool, typer.Option("--python", "-P", help="flag to use python over IPython.")] = False,
    profile: Annotated[Optional[str], typer.Option("--profile", "-r", help="ipython profile to use, defaults to default profile.")] = None,
) -> None:
    """Cross-shell command execution."""
    from machineconfig.scripts.python.croshell import croshell as croshell_impl
    croshell_impl(path=path, project_path=project_path, uv_with=uv_with, marimo=marimo, jupyter=jupyter, vscode=vscode, visidata=visidata, python=python, profile=profile)


def devops(ctx: typer.Context) -> None:
    """[d] DevOps related commands."""
    from machineconfig.scripts.python.devops import get_app
    get_app()(ctx.args, standalone_mode=not ctx.args)


def cloud(ctx: typer.Context) -> None:
    """[c] Cloud management commands."""
    from machineconfig.scripts.python.cloud import get_app
    get_app()(ctx.args, standalone_mode=not ctx.args)


def sessions(ctx: typer.Context) -> None:
    """[s] Session and layout management."""
    from machineconfig.scripts.python.sessions import get_app
    get_app()(ctx.args, standalone_mode=not ctx.args)


def agents(ctx: typer.Context) -> None:
    """[a] 🤖 AI Agents management commands."""
    from machineconfig.scripts.python.agents import get_app
    get_app()(ctx.args, standalone_mode=not ctx.args)


def utils(ctx: typer.Context) -> None:
    """[u] Utility commands."""
    from machineconfig.scripts.python.utils import get_app
    get_app()(ctx.args, standalone_mode=not ctx.args)


def terminal(ctx: typer.Context) -> None:
    """[t] Terminal management commands."""
    from machineconfig.scripts.python.terminal import get_app
    get_app()(ctx.args, standalone_mode=not ctx.args)


def get_app() -> typer.Typer:
    app = typer.Typer(help="MachineConfig CLI - Manage your machine configurations and workflows", no_args_is_help=True, add_help_option=True, add_completion=False)

    ctx_settings: dict[str, object] = {"allow_extra_args": True, "allow_interspersed_args": True, "ignore_unknown_options": True, "help_option_names": []}

    app.command(name="devops", help="[d] DevOps related commands", context_settings=ctx_settings)(devops)
    app.command(name="d", hidden=True, context_settings=ctx_settings)(devops)
    app.command(name="cloud", help="[c] Cloud management commands", context_settings=ctx_settings)(cloud)
    app.command(name="c", hidden=True, context_settings=ctx_settings)(cloud)
    app.command(name="sessions", help="[s] Session and layout management", context_settings=ctx_settings)(sessions)
    app.command(name="s", hidden=True, context_settings=ctx_settings)(sessions)
    app.command(name="agents", help="[a] 🤖 AI Agents management commands", context_settings=ctx_settings)(agents)
    app.command(name="a", hidden=True, context_settings=ctx_settings)(agents)
    app.command(name="utils", help="[u] Utility commands", context_settings=ctx_settings)(utils)
    app.command(name="u", hidden=True, context_settings=ctx_settings)(utils)
    app.command(name="terminal", help="[t] Terminal management commands", context_settings=ctx_settings)(terminal)
    app.command(name="t", hidden=True, context_settings=ctx_settings)(terminal)

    app.command(name="fire", help="[f] Fire and manage jobs", no_args_is_help=False, context_settings={"allow_extra_args": True, "allow_interspersed_args": False})(fire)
    app.command(name="f", hidden=True, no_args_is_help=False, context_settings={"allow_extra_args": True, "allow_interspersed_args": False})(fire)
    app.command("ftpx", no_args_is_help=True, help="[ff] File transfer utility though SSH")(ftpx)
    app.command("ff", no_args_is_help=True, hidden=True)(ftpx)
    app.command("croshell", no_args_is_help=False, help="[r] Cross-shell command execution")(croshell)
    app.command("r", no_args_is_help=False, hidden=True)(croshell)

    return app


def main() -> None:
    app = get_app()
    app()


if __name__ == "__main__":
    main()
