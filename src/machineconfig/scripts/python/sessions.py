"""Sessions management commands - lazy loading subcommands."""

from typing import Optional, Literal, Annotated
import typer


def balance_load(
    layout_path: Annotated[str, typer.Argument(..., help="Path to the layout.json file")],
    max_thresh: Annotated[int, typer.Option(..., "--max-threshold", "-m", help="Maximum tabs per layout")],
    thresh_type: Annotated[Literal["number", "n", "weight", "w"], typer.Option(..., "--threshold-type", "-t", help="Threshold type")],
    breaking_method: Annotated[Literal["moreLayouts", "ml", "combineTabs", "ct"], typer.Option(..., "--breaking-method", "-b", help="Breaking method")],
    output_path: Annotated[Optional[str], typer.Option(..., "--output-path", "-o", help="Path to write the adjusted layout.json file")] = None,
) -> None:
    """Adjust layout file to limit max tabs per layout, etc."""
    from machineconfig.scripts.python.helpers.helpers_sessions.utils import balance_load as impl
    impl(layout_path=layout_path, max_thresh=max_thresh, thresh_type=thresh_type, breaking_method=breaking_method, output_path=output_path)


def run(
    ctx: typer.Context,
    layouts_file: Annotated[Optional[str], typer.Option(..., "--layouts-file", "-f", help="Path to the layout.json file")] = None,
    choose: Annotated[Optional[str], typer.Option(..., "--choose", "-c", help="Comma separated names of layouts to be selected from the layout file passed")] = None,
    choose_interactively: Annotated[bool, typer.Option(..., "--choose-interactively", "-i", help="Select layouts interactively")] = False,

    sleep_inbetween: Annotated[float, typer.Option(..., "--sleep-inbetween", "-si", help="Sleep time in seconds between launching layouts")] = 1.0,
    monitor: Annotated[bool, typer.Option(..., "--monitor", "-m", help="Monitor the layout sessions for completion")] = False,
    sequential: Annotated[bool, typer.Option(..., "--sequential", "-s", help="Launch layouts sequentially")] = False,
    kill_upon_completion: Annotated[bool, typer.Option(..., "--kill-upon-completion", "-k", help="Kill session(s) upon completion (only relevant if monitor flag is set)")] = False,
    subsitute_home: Annotated[bool, typer.Option(..., "--substitute-home", "-sh", help="Substitute ~ and $HOME in layout file with actual home directory path")] = False,
    max_tabs: Annotated[int, typer.Option(..., "--max-tabs", "-mt", help="A Sanity checker that throws an error if any layout exceeds the maximum number of tabs to launch.")] = 25,
    max_layouts: Annotated[int, typer.Option(..., "--max-layouts", "-ml", help="A Sanity checker that throws an error if the total number of *parallel layouts exceeds this number.")] = 25,
    backend: Annotated[Literal["zellij", "z", "windows-terminal", "wt", "tmux", "t", "auto", "a"], typer.Option(..., "--backend", "-b", help="Backend terminal multiplexer or emulator to use")] = "auto",
) -> None:
    """Launch terminal sessions based on a layout configuration file."""
    from machineconfig.scripts.python.helpers.helpers_sessions.sessions_impl import run_layouts, find_layout_file, select_layout

    from pathlib import Path
    if layouts_file is not None:
        layouts_file_resolved = Path(find_layout_file(layout_path=layouts_file))
    else:
        layouts_file_resolved = Path.home().joinpath("dotfiles/machineconfig/layouts.json")
    if not layouts_file_resolved.exists():
        typer.echo(ctx.get_help())
        typer.echo(f"❌ Layouts file not found: {layouts_file_resolved}", err=True)
        raise typer.Exit(code=1)

    if choose is None: layouts_names_resolved: list[str] = []
    else: layouts_names_resolved = [name.strip() for name in choose.split(",") if name.strip()]
    layouts_selected = select_layout(layouts_json_file=str(layouts_file_resolved), selected_layouts_names=layouts_names_resolved,
                    select_interactively=choose_interactively,)
    if subsitute_home:
        from machineconfig.utils.schemas.layouts.layout_types import substitute_home, LayoutConfig
        layouts_modified: list["LayoutConfig"] = []
        for a_layout in layouts_selected:
            a_layout["layoutTabs"] = substitute_home(tabs=a_layout["layoutTabs"])
            layouts_modified.append(a_layout)
        layouts_selected = layouts_modified

    import platform
    backend_resolved: Literal["zellij", "windows-terminal", "tmux"]
    match backend:
        case "windows-terminal" | "wt":
            if platform.system().lower() != "windows":
                typer.echo("Error: Windows Terminal layouts can only be started on Windows systems.", err=True)
                raise typer.Exit(code=1)
            backend_resolved = "windows-terminal"
        case "tmux" | "t":
            if platform.system().lower() == "windows":
                typer.echo("Error: tmux is not supported on Windows.", err=True)
                raise typer.Exit(code=1)
            backend_resolved = "tmux"
        case "zellij" | "z":
            if platform.system().lower() == "windows":
                typer.echo("Error: Zellij is not supported on Windows.", err=True)
                raise typer.Exit(code=1)
            backend_resolved = "zellij"
        case "auto" | "a":
            if platform.system().lower() == "windows":
                backend_resolved = "windows-terminal"
            else:
                backend_resolved = "zellij"
        case _:
            typer.echo(f"Error: Unsupported backend '{backend}'.", err=True)
            raise typer.Exit(code=1)

    if not sequential and len(layouts_selected) > max_layouts:
        raise ValueError(f"Number of layouts {len(layouts_selected)} exceeds the maximum allowed {max_layouts}. Please adjust your layout file.")
    for a_layout in layouts_selected:
        if len(a_layout["layoutTabs"]) > max_tabs:
            raise ValueError(f"Layout '{a_layout.get('layoutName', 'Unnamed')}' has {len(a_layout['layoutTabs'])} tabs which exceeds the max of {max_tabs}.")

    try:
        run_layouts(
        sleep_inbetween=sleep_inbetween, monitor=monitor, sequential=sequential, kill_upon_completion=kill_upon_completion,
        layouts_selected=layouts_selected,
        backend=backend_resolved)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1) from e


def attach_to_session(
        name: Annotated[str | None, typer.Argument(help="Name of the session to attach to. If not provided, a list will be shown to choose from.")] = None,
        new_session: Annotated[bool, typer.Option("--new-session", "-n", help="Create a new session instead of attaching to an existing one.", show_default=True)] = False,
        kill_all: Annotated[bool, typer.Option("--kill-all", "-k", help="Kill all existing sessions before creating a new one.", show_default=True)] = False,
        backend: Annotated[Literal["zellij", "z", "tmux", "t", "auto", "a"], typer.Option(..., "--backend", "-b", help="Backend multiplexer to use")] = "auto",
        ) -> None:
    """Choose a session to attach to."""
    import platform
    backend_resolved: Literal["zellij", "tmux"]
    match backend:
        case "zellij" | "z":
            if platform.system().lower() == "windows":
                typer.echo("Error: Zellij is not supported on Windows.", err=True, color=True)
                raise typer.Exit()
            backend_resolved = "zellij"
        case "tmux" | "t":
            if platform.system().lower() == "windows":
                typer.echo("Error: tmux is not supported on Windows.", err=True, color=True)
                raise typer.Exit()
            backend_resolved = "tmux"
        case "auto" | "a":
            if platform.system().lower() == "windows":
                typer.echo("Error: tmux/zellij are not supported on Windows.", err=True, color=True)
                raise typer.Exit()
            backend_resolved = "zellij"
        case _:
            typer.echo(f"Error: Unsupported backend '{backend}'.", err=True, color=True)
            raise typer.Exit()
    from machineconfig.scripts.python.helpers.helpers_sessions.attach_impl import choose_session as impl
    action, payload = impl(backend=backend_resolved, name=name, new_session=new_session, kill_all=kill_all)
    if action == "error":
        typer.echo(payload, err=True, color=True)
        raise typer.Exit()
    if action == "run_script" and payload:
        from machineconfig.utils.code import exit_then_run_shell_script
        exit_then_run_shell_script(script= payload, strict=True)



def get_session_tabs() -> list[tuple[str, str]]:
    """Get all Zellij session tabs."""
    from machineconfig.scripts.python.helpers.helpers_sessions.attach_impl import get_session_tabs as impl
    result = impl()
    print(result)
    return result
def create_template(
    name: Annotated[Optional[str], typer.Argument(..., help="Name of the layout template to create")] = None,
    num_tabs: Annotated[int, typer.Option(..., "--num-tabs", "-t", help="Number of tabs to include in the template")] = 3,
) -> None:
    """Create a layout template file."""
    from machineconfig.scripts.python.helpers.helpers_sessions.utils import create_template as impl
    impl(name=name, num_tabs=num_tabs)

def create_from_function(
    num_process: Annotated[int, typer.Option(..., "--num-process", "-n", help="Number of parallel processes to run")],
    path: Annotated[str, typer.Option(..., "--path", "-p", help="Path to a Python or Shell script file or a directory containing such files")] = ".",
    function: Annotated[Optional[str], typer.Option(..., "--function", "-f", help="Function to run from the Python file. If not provided, you will be prompted to choose.")] = None,
) -> None:
    """Create a layout from a function to run in multiple processes."""
    from machineconfig.scripts.python.helpers.helpers_sessions.sessions_multiprocess import create_from_function as impl
    impl(num_process=num_process, path=path, function=function)


def get_app() -> typer.Typer:
    layouts_app = typer.Typer(help="Layouts management subcommands", no_args_is_help=True, add_help_option=True, add_completion=False)

    layouts_app.command("run", no_args_is_help=True, help=run.__doc__, short_help="[r] Run the selected layout(s)")(run)
    layouts_app.command("r", no_args_is_help=True, help=run.__doc__, hidden=True)(run)

    layouts_app.command("attach", no_args_is_help=False, help=attach_to_session.__doc__, short_help="[a] Attach to a Zellij session")(attach_to_session)
    layouts_app.command("a", no_args_is_help=False, help=attach_to_session.__doc__, hidden=True)(attach_to_session)

    layouts_app.command("create-from-function", no_args_is_help=True, short_help="[c] Create a layout from a function")(create_from_function)
    layouts_app.command("c", no_args_is_help=True, hidden=True)(create_from_function)

    layouts_app.command("balance-load", no_args_is_help=True, help=balance_load.__doc__, short_help="[b] Balance the load across sessions")(balance_load)
    layouts_app.command("b", no_args_is_help=True, help=balance_load.__doc__, hidden=True)(balance_load)

    layouts_app.command("create-template", no_args_is_help=False, help=create_template.__doc__, short_help="[t] Create a layout template file")(create_template)
    layouts_app.command("t", no_args_is_help=False, help=create_template.__doc__, hidden=True)(create_template)
    return layouts_app


def main() -> None:
    layouts_app = get_app()
    layouts_app()


if __name__ == "__main__":
    pass
