"""Sessions management commands - lazy loading subcommands."""

from typing import Optional, Literal, Annotated, cast
import typer


def balance_load(
    layout_path: Annotated[str, typer.Argument(..., help="Path to the layout.json file")],
    max_thresh: Annotated[int, typer.Option(..., "--max-threshold", "-m", help="Maximum tabs per layout")],
    thresh_type: Annotated[Literal["number", "n", "weight", "w"], typer.Option(..., "--threshold-type", "-t", help="Threshold type")] = "number",
    breaking_method: Annotated[Literal["moreLayouts", "ml", "combineTabs", "ct"], typer.Option(..., "--breaking-method", "-b", help="Breaking method")] = "moreLayouts",
    output_path: Annotated[Optional[str], typer.Option(..., "--output-path", "-o", help="Path to write the adjusted layout.json file")] = None,
) -> None:
    """Adjust layout file to limit max tabs per layout, etc."""
    from machineconfig.scripts.python.helpers.helpers_sessions.utils import balance_load as impl
    impl(layout_path=layout_path, max_thresh=max_thresh, thresh_type=thresh_type, breaking_method=breaking_method, output_path=output_path)


def run(
    ctx: typer.Context,
    layouts_file: Annotated[Optional[str], typer.Option(..., "--layouts-file", "-f", help="Path to the layout.json file")] = None,
    choose_layouts: Annotated[Optional[str], typer.Option(..., "--choose-layouts", "-c", help="Comma separated layout names. Pass empty string to select layouts interactively.")] = None,
    choose_tabs: Annotated[Optional[str], typer.Option(..., "--choose-tabs", "-t", help="Comma separated tab names. Pass empty string to select tabs interactively from all layouts.")] = None,
    sleep_inbetween: Annotated[float, typer.Option(..., "--sleep-inbetween", "-S", help="Sleep time in seconds between launching layouts")] = 1.0,
    monitor: Annotated[bool, typer.Option(..., "--monitor", "-m", help="Monitor the layout sessions for completion (implied by --parallel-layouts)")] = False,
    parallel_layouts: Annotated[Optional[int], typer.Option(..., "--parallel-layouts", "-p", help="Maximum number of layouts to launch per monitored batch. 1 behaves like sequential mode.")] = None,
    kill_upon_completion: Annotated[bool, typer.Option(..., "--kill-upon-completion", "-k", help="Kill session(s) upon completion (only relevant if --monitor or --parallel-layouts is set)")] = False,
    subsitute_home: Annotated[bool, typer.Option(..., "--substitute-home", "-H", help="Substitute ~ and $HOME in layout file with actual home directory path")] = False,
    max_tabs: Annotated[int, typer.Option(..., "--max-tabs-per-layout", "-T", help="A Sanity checker that throws an error if any layout exceeds the maximum number of tabs to launch.")] = 25,
    max_layouts: Annotated[int, typer.Option(..., "--max-parallel-layouts", "-P", help="A Sanity checker that throws an error if the total number of *parallel layouts exceeds this number.")] = 25,
    backend: Annotated[Literal["zellij", "z", "windows-terminal", "wt", "tmux", "t", "auto", "a"], typer.Option(..., "--backend", "-b", help="Backend terminal multiplexer or emulator to use")] = "auto",
    max_parallel_tabs: Annotated[Optional[int], typer.Option("--max-parallel-tabs", help="Enable dynamic tab scheduling and cap active tabs to this value.")] = None,
    kill_finished_tabs: Annotated[bool, typer.Option("--kill-finished-tabs", help="Dynamic mode only: close each tab once its command is finished.")] = False,
    poll_seconds: Annotated[float, typer.Option("--poll-seconds", help="Dynamic mode only: polling interval in seconds used to detect finished tabs.")] = 2.0,
    all_file: Annotated[bool, typer.Option("--all-file", help="Dynamic mode only: merge tabs from all layouts in the file into one dynamic run.")] = False,
) -> None:
    """Launch terminal sessions based on a layout configuration file.

    Pass --max-parallel-tabs to enable dynamic tab scheduling.
    """
    from machineconfig.scripts.python.helpers.helpers_sessions.sessions_impl import run_layouts, find_layout_file, select_layout
    from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig, TabConfig, substitute_home
    from pathlib import Path
    if layouts_file is not None:
        layouts_file_resolved = Path(find_layout_file(layout_path=layouts_file))
    else:
        layouts_file_resolved = Path.home().joinpath("dotfiles/machineconfig/layouts.json")
    if not layouts_file_resolved.exists():
        typer.echo(ctx.get_help())
        typer.echo(f"❌ Layouts file not found: {layouts_file_resolved}", err=True)
        raise typer.Exit(code=1)

    dynamic_all_file_mode = max_parallel_tabs is not None and all_file
    if dynamic_all_file_mode:
        if choose_layouts is not None:
            print("Note: --choose-layouts is ignored when --all-file is set in dynamic mode.")
        if choose_tabs is not None:
            print("Note: --choose-tabs is ignored when --all-file is set in dynamic mode.")
        layouts_names_resolved = []
        choose_layouts_interactively = False
    elif choose_layouts is None:
        layouts_names_resolved = []
        choose_layouts_interactively = False
    elif choose_layouts == "":
        layouts_names_resolved = []
        choose_layouts_interactively = True
    else:
        layouts_names_resolved = [name.strip() for name in choose_layouts.split(",") if name.strip()]
        choose_layouts_interactively = False

    layouts_selected: list[LayoutConfig] = select_layout(
        layouts_json_file=str(layouts_file_resolved),
        selected_layouts_names=layouts_names_resolved,
        select_interactively=choose_layouts_interactively,
    )

    if choose_tabs is not None and not dynamic_all_file_mode:
        all_layouts: list[LayoutConfig] = select_layout(
            layouts_json_file=str(layouts_file_resolved),
            selected_layouts_names=[],
            select_interactively=False,
        )
        allowed_layout_names = {layout["layoutName"] for layout in layouts_selected}
        flat_tab_refs: list[tuple[str, int, TabConfig]] = []
        for layout in all_layouts:
            for tab_index, tab in enumerate(layout["layoutTabs"]):
                flat_tab_refs.append((layout["layoutName"], tab_index, tab))

        selected_tab_refs: set[tuple[str, int]] = set()
        if choose_tabs == "":
            import json
            from machineconfig.utils.options_utils.tv_options import choose_from_dict_with_preview

            options_to_preview_mapping: dict[str, str] = {}
            key_to_ref: dict[str, tuple[str, int]] = {}
            for layout_name, tab_index, tab in flat_tab_refs:
                option_key = f"{layout_name}::{tab.get('tabName', f'tab#{tab_index + 1}')}[{tab_index}]"
                options_to_preview_mapping[option_key] = json.dumps({"layoutName": layout_name, "tabIndex": tab_index, "tab": tab}, indent=4)
                key_to_ref[option_key] = (layout_name, tab_index)
            chosen_keys = choose_from_dict_with_preview(options_to_preview_mapping=options_to_preview_mapping, extension="json", multi=True, preview_size_percent=40)
            selected_tab_refs = {key_to_ref[key] for key in chosen_keys}
        else:
            tab_tokens = [token.strip() for token in choose_tabs.split(",") if token.strip()]
            for token in tab_tokens:
                if "::" in token:
                    layout_name_token, tab_name_token = token.split("::", 1)
                    token_matches = {
                        (layout_name, tab_index)
                        for layout_name, tab_index, tab in flat_tab_refs
                        if layout_name == layout_name_token and tab.get("tabName", "") == tab_name_token
                    }
                else:
                    token_matches = {
                        (layout_name, tab_index)
                        for layout_name, tab_index, tab in flat_tab_refs
                        if tab.get("tabName", "") == token
                    }
                if len(token_matches) == 0:
                    raise ValueError(f"Tab selector '{token}' matched no tabs.")
                selected_tab_refs.update(token_matches)

        merged_tabs = [
            tab
            for layout_name, tab_index, tab in flat_tab_refs
            if layout_name in allowed_layout_names and (layout_name, tab_index) in selected_tab_refs
        ]
        if len(merged_tabs) == 0:
            raise ValueError("No tabs were selected in the chosen layouts.")
        custom_layout: LayoutConfig = {"layoutName": "custom-tabs", "layoutTabs": merged_tabs}
        layouts_selected = [custom_layout]

    if dynamic_all_file_mode:
        merged_tabs = [tab for layout in layouts_selected for tab in layout["layoutTabs"]]
        if len(merged_tabs) == 0:
            raise ValueError("No tabs found across all layouts in the selected file.")
        dynamic_layout: LayoutConfig = {"layoutName": "all-layouts-dynamic", "layoutTabs": merged_tabs}
        layouts_selected = [dynamic_layout]

    if all_file and max_parallel_tabs is None:
        raise ValueError("--all-file is only supported with --max-parallel-tabs.")

    if subsitute_home:
        layouts_modified: list[LayoutConfig] = []
        for a_layout in layouts_selected:
            layout_modified: LayoutConfig = {
                "layoutName": a_layout["layoutName"],
                "layoutTabs": substitute_home(tabs=a_layout["layoutTabs"]),
            }
            layouts_modified.append(layout_modified)
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
    try:
        if max_parallel_tabs is not None:
            from machineconfig.scripts.python.helpers.helpers_sessions.sessions_dynamic import run_dynamic as run_dynamic_impl

            if parallel_layouts is not None:
                raise ValueError("--parallel-layouts is not supported with --max-parallel-tabs dynamic mode.")
            if backend in {"windows-terminal", "wt"}:
                raise ValueError("Dynamic mode does not support windows-terminal; use --backend zellij, tmux, or auto.")
            if len(layouts_selected) != 1:
                raise ValueError(
                    f"Dynamic mode expects exactly one selected layout. Got {len(layouts_selected)}. "
                    "Select one layout with --choose-layouts or pass --all-file."
                )
            if monitor:
                print("Note: --monitor is implicit in dynamic mode.")
            if kill_upon_completion:
                print("Note: --kill-upon-completion is ignored in dynamic mode; use --kill-finished-tabs instead.")

            dynamic_backend = cast(Literal["zellij", "z", "tmux", "t", "auto", "a"], backend)
            run_dynamic_impl(
                layout=layouts_selected[0],
                max_parallel_tabs=max_parallel_tabs,
                kill_finished_tabs=kill_finished_tabs,
                backend=dynamic_backend,
                poll_seconds=poll_seconds,
            )
        else:
            if parallel_layouts is not None and parallel_layouts <= 0:
                raise ValueError("--parallel-layouts must be a positive integer.")
            if parallel_layouts is None and len(layouts_selected) > max_layouts:
                raise ValueError(f"Number of layouts {len(layouts_selected)} exceeds the maximum allowed {max_layouts}. Please adjust your layout file.")
            if parallel_layouts is not None and parallel_layouts > max_layouts:
                raise ValueError(f"--parallel-layouts value {parallel_layouts} exceeds --max-parallel-layouts limit {max_layouts}.")
            for a_layout in layouts_selected:
                if len(a_layout["layoutTabs"]) > max_tabs:
                    raise ValueError(f"Layout '{a_layout.get('layoutName', 'Unnamed')}' has {len(a_layout['layoutTabs'])} tabs which exceeds the max of {max_tabs}.")

            run_layouts(
                sleep_inbetween=sleep_inbetween, monitor=monitor, parallel_layouts=parallel_layouts, kill_upon_completion=kill_upon_completion,
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

    layouts_app.command("run", no_args_is_help=True, help=run.__doc__, short_help="<r> Run the selected layout(s)")(run)
    layouts_app.command("r", no_args_is_help=True, help=run.__doc__, hidden=True)(run)

    layouts_app.command("attach", no_args_is_help=False, help=attach_to_session.__doc__, short_help="<a> Attach to a Zellij session")(attach_to_session)
    layouts_app.command("a", no_args_is_help=False, help=attach_to_session.__doc__, hidden=True)(attach_to_session)

    layouts_app.command("create-from-function", no_args_is_help=True, short_help="<c> Create a layout from a function")(create_from_function)
    layouts_app.command("c", no_args_is_help=True, hidden=True)(create_from_function)

    layouts_app.command("balance-load", no_args_is_help=True, help=balance_load.__doc__, short_help="<b> Balance the load across sessions")(balance_load)
    layouts_app.command("b", no_args_is_help=True, help=balance_load.__doc__, hidden=True)(balance_load)

    layouts_app.command("create-template", no_args_is_help=False, help=create_template.__doc__, short_help="<t> Create a layout template file")(create_template)
    layouts_app.command("t", no_args_is_help=False, help=create_template.__doc__, hidden=True)(create_template)
    return layouts_app


def main() -> None:
    layouts_app = get_app()
    layouts_app()


if __name__ == "__main__":
    pass
