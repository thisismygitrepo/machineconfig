"""fire - Fire and manage jobs."""

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
    """Main function to process fire jobs arguments."""
    from machineconfig.scripts.python.helpers.helpers_fire_command.fire_jobs_args_helper import FireJobArgs, parse_fire_args_from_context
    from machineconfig.scripts.python.helpers.helpers_fire_command.fire_jobs_impl import route

    fire_args = parse_fire_args_from_context(ctx)

    args = FireJobArgs(
        path=path,
        function=function,
        ve=ve,
        cmd=cmd,
        interactive=interactive,
        debug=debug,
        choose_function=choose_function,
        loop=loop,
        jupyter=jupyter,
        marimo=marimo,
        submit_to_cloud=submit_to_cloud,
        remote=remote,
        module=module,
        script=script,
        streamlit=streamlit,
        environment=environment,
        holdDirectory=holdDirectory,
        PathExport=PathExport,
        git_pull=git_pull,
        optimized=optimized,
        zellij_tab=zellij_tab,
        watch=watch,
    )
    try:
        route(args, fire_args)
    except SystemExit:
        raise
    except Exception as e:
        import sys
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def get_app() -> typer.Typer:
    app = typer.Typer(add_completion=False)
    app.command(context_settings={"allow_extra_args": True, "allow_interspersed_args": False})(fire)
    return app


def main() -> None:
    app = get_app()
    app()


if __name__ == "__main__":
    pass
