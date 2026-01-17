
import typer
from typing import Annotated, Optional


def choose_zellij_session(
        name: Annotated[str | None, typer.Argument(help="Name of the Zellij session to attach to. If not provided, a list will be shown to choose from.")] = None,
        new_session: Annotated[bool, typer.Option("--new-session", "-n", help="Create a new Zellij session instead of attaching to an existing one.", show_default=True)] = False,
        kill_all: Annotated[bool, typer.Option("--kill-all", "-k", help="Kill all existing Zellij sessions before creating a new one.", show_default=True)] = False) -> None:
    """Choose a Zellij session to attach to."""
    import platform
    if platform.system().lower() == "windows":
        typer.echo("Error: Zellij is not supported on Windows.", err=True, color=True)
        raise typer.Exit()
    from machineconfig.scripts.python.helpers.helpers_terminal.terminal_impl import choose_zellij_session as impl
    action, payload = impl(name=name, new_session=new_session, kill_all=kill_all)
    if action == "error":
        typer.echo(payload, err=True, color=True)
        raise typer.Exit()
    if action == "run_script" and payload:
        from machineconfig.utils.code import exit_then_run_shell_script
        exit_then_run_shell_script(script= payload, strict=True)


def get_session_tabs() -> list[tuple[str, str]]:
    """Get all Zellij session tabs."""
    from machineconfig.scripts.python.helpers.helpers_terminal.terminal_impl import get_session_tabs as impl
    result = impl()
    print(result)
    return result


def start_wt(layouts_names: Annotated[Optional[str], typer.Option(..., "--layout", "-l", help="Layout names (comma separated) to start.")] = None,
             layout_file: Annotated[Optional[str], typer.Option(..., "--layout-file", "-f", help="Path to the layouts file.")] = None,
             dump_example: Annotated[bool, typer.Option("--dump-example", "-d", help="Dump an example layout file to the current directory.", show_default=True)] = False
             ) -> None:
    """Start a Windows Terminal layout by name."""
    if dump_example:
        import machineconfig.cluster.sessions_managers.wt_utils.examples as module
        from pathlib import Path
        raw_path = module.__file__
        if raw_path is None:
            typer.echo("Error: Could not find the example layout file.", err=True)
            raise typer.Exit(code=1)
        else:
            example_path = Path(raw_path).parent / "example_layout.json"
            current_pwd = Path.cwd()
            # copy the example file to the current directory with name example_layout.json
            from shutil import copyfile
            copyfile(example_path, current_pwd / "example_layout.json")
            typer.echo(f"Example layout file dumped to: {current_pwd / "example_layout.json"}")
            raise typer.Exit()
    import platform
    if platform.system().lower() != "windows":
        typer.echo("Error: Windows Terminal layouts can only be started on Windows systems.", err=True)
        raise typer.Exit(code=1)
    from machineconfig.scripts.python.helpers.helpers_terminal.terminal_impl import start_wt as impl
    if layouts_names is None:
        layouts_names_resolved = None
    else:
        layouts_names_resolved = [name.strip() for name in layouts_names.split(",") if name.strip()]
    status, message = impl(layouts_names=layouts_names_resolved, layout_file_str=layout_file)
    if status == "error":
        typer.echo(message= message)
        raise typer.Exit(code=1)
    # cmd = f'powershell -ExecutionPolicy Bypass -File "./{layout_name}_layout.ps1"'
    # from machineconfig.utils.code import exit_then_run_shell_script
    # exit_then_run_shell_script(cmd, strict=True)


def get_app():
    app = typer.Typer(help="🖥️ Terminal utilities", no_args_is_help=True, add_help_option=True, add_completion=False)
    app.command(name="attach-to-zellij", no_args_is_help=False, help=choose_zellij_session.__doc__, short_help="[z] Choose a Zellij session to attach to")(choose_zellij_session)
    app.command(name="z", hidden=True, no_args_is_help=False, help=choose_zellij_session.__doc__)(choose_zellij_session)

    app.command(name="start-wt", no_args_is_help=True, help=start_wt.__doc__, short_help="[w] Start a Windows Terminal layout by name.")(start_wt)
    app.command(name="w", hidden=True, no_args_is_help=True, help=start_wt.__doc__)(start_wt)

    app.command(name="get-session-tabs", no_args_is_help=False, help=get_session_tabs.__doc__, short_help="[zt] Get all Zellij session tabs.")(get_session_tabs)
    app.command(name="zt", hidden=True, no_args_is_help=False, help=get_session_tabs.__doc__)(get_session_tabs)
    return app

def main():
    app = get_app()
    app()


if __name__ == "__main__":
    main()
