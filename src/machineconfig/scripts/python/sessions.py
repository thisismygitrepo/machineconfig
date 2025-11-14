
from typing import Optional, Literal, Annotated
import typer


def balance_load(layout_path: Annotated[str, typer.Argument(..., help="Path to the layout.json file")],
           max_thresh: Annotated[int, typer.Option(..., "--max-threshold", "-m", help="Maximum tabs per layout")],
           thresh_type: Annotated[Literal['number', 'n', 'weight', 'w'], typer.Option(..., "--threshold-type", "-t", help="Threshold type")],
           breaking_method: Annotated[Literal['moreLayouts', 'ml', 'combineTabs', 'ct'], typer.Option(..., "--breaking-method", "-b", help="Breaking method")],
           output_path: Annotated[Optional[str], typer.Option(..., "--output-path", "-o", help="Path to write the adjusted layout.json file")] = None):
    """Adjust layout file to limit max tabs per layout, etc."""
    thresh_type_resolved: dict[str, Literal['number', 'weight']] = {
        'number': 'number',
        'n': 'number',
        'weight': 'weight',
        'w': 'weight'
    }
    breaking_method_resolved: dict[str, Literal['moreLayouts', 'combineTabs']] = {
        'moreLayouts': 'moreLayouts',
        'ml': 'moreLayouts',
        'combineTabs': 'combineTabs',
        'ct': 'combineTabs'
    }
    from pathlib import Path
    layout_path_obj = Path(layout_path).expanduser().absolute()

    from machineconfig.utils.schemas.layouts.layout_types import LayoutsFile
    import json
    layoutfile: LayoutsFile = json.loads(layout_path_obj.read_text())
    layout_configs = layoutfile["layouts"]
    from machineconfig.cluster.sessions_managers.utils.load_balancer import limit_tab_num
    new_layouts = limit_tab_num(layout_configs=layout_configs, max_thresh=max_thresh, threshold_type=thresh_type_resolved[thresh_type], breaking_method=breaking_method_resolved[breaking_method])
    layoutfile["layouts"] = new_layouts
    target_file = Path(output_path) if output_path is not None else layout_path_obj.parent / f'{layout_path_obj.stem}_adjusted_{max_thresh}_{thresh_type}_{breaking_method}.json'
    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_text(data=json.dumps(layoutfile, indent=4), encoding="utf-8")
    typer.echo(f"Adjusted layout saved to {target_file}")


def select_layout(layouts_json_file: str, selected_layouts_names: Optional[list[str]], select_interactively: bool,
                  subsitute_home: bool
                  ) -> list["LayoutConfig"]:
    import json
    from machineconfig.utils.options import choose_from_options
    from machineconfig.utils.schemas.layouts.layout_types import LayoutsFile
    from pathlib import Path
    json_str = Path(layouts_json_file).read_text(encoding="utf-8")
    if subsitute_home:
        json_str = json_str.replace("~", str(Path.home())).replace("$HOME", str(Path.home()))
        json_str = json_str.replace("""Command": "f """, """Command": "~/.config/machineconfig/scripts/wrap_mcfg fire """)
        json_str = json_str.replace("""Command": "s """, """Command": "~/.config/machineconfig/scripts/wrap_mcfg sessions """)

    layout_file: LayoutsFile = json.loads(json_str)
    if len(layout_file["layouts"]) == 0:
        raise ValueError(f"No layouts found in {layouts_json_file}")
    if selected_layouts_names is None:  # choose all, or interactively
        if not select_interactively:
            return layout_file["layouts"]
        options = [layout["layoutName"] for layout in layout_file["layouts"]]
        from machineconfig.utils.options import choose_from_options
        selected_layouts_names = choose_from_options(multi=True, options=options, prompt="Choose a layout configuration:", tv=True, msg="Choose one option")
    print(f"Selected layout(s): {selected_layouts_names}")
    # Extract the configs from the names:
    layouts_chosen: list[LayoutConfig] = []
    for name in selected_layouts_names:
        layout_chosen = next((layout for layout in layout_file["layouts"] if layout["layoutName"] == name), None)
        if layout_chosen is None:
            layout_chosen = next((layout for layout in layout_file["layouts"] if layout["layoutName"].lower() == name.lower()), None)
        if layout_chosen is None:
            available_layouts = [layout["layoutName"] for layout in layout_file["layouts"]]
            raise ValueError(f"Layout '{name}' not found. Available layouts: {available_layouts}")
        layouts_chosen.append(layout_chosen)
    return layouts_chosen


def find_layout_file(layout_path: str, ) -> str:
    from machineconfig.utils.path_helper import search_for_files_of_interest
    from machineconfig.utils.options import choose_from_options
    from machineconfig.utils.path_helper import match_file_name, sanitize_path
    from pathlib import Path
    path_obj = sanitize_path(layout_path)
    if not path_obj.exists():
        choice_file = match_file_name(sub_string=layout_path, search_root=Path.cwd(), suffixes={".json"})
    elif path_obj.is_dir():
        print(f"🔍 Searching recursively for Python, PowerShell and Shell scripts in directory `{path_obj}`")
        files = search_for_files_of_interest(path_obj, suffixes={".py", ".sh", ".ps1"})
        print(f"🔍 Got #{len(files)} results.")
        choice_file = choose_from_options(multi=False, options=files, tv=True, msg="Choose one option")
        choice_file = Path(choice_file).expanduser().absolute()
    else:
        choice_file = path_obj
    return str(choice_file)


def run(ctx: typer.Context,
           layout_path: Annotated[Optional[str], typer.Argument(..., help="Path to the layout.json file")] = None,
        max_tabs: Annotated[int, typer.Option(..., "--max-tabs", "-mt", help="A Sanity checker that throws an error if any layout exceeds the maximum number of tabs to launch.")] = 10,
        max_layouts: Annotated[int, typer.Option(..., "--max-layouts", "-ml", help="A Sanity checker that throws an error if the total number of *parallel layouts exceeds this number.")] = 10,
        sleep_inbetween: Annotated[float, typer.Option(..., "--sleep-inbetween", "-si", help="Sleep time in seconds between launching layouts")] = 1.0,
        monitor: Annotated[bool, typer.Option(..., "--monitor", "-m", help="Monitor the layout sessions for completion")] = False,
        parallel: Annotated[bool, typer.Option(..., "--parallel", "-p", help="Launch multiple layouts in parallel")] = False,
        kill_upon_completion: Annotated[bool, typer.Option(..., "--kill-upon-completion", "-k", help="Kill session(s) upon completion (only relevant if monitor flag is set)")] = False,
        choose: Annotated[Optional[str], typer.Option(..., "--choose", "-c", help="Comma separated names of layouts to be selected from the layout file passed")] = None,
        choose_interactively: Annotated[bool, typer.Option(..., "--choose-interactively", "-i", help="Select layouts interactively")] = False,
        subsitute_home: Annotated[bool, typer.Option(..., "--substitute-home", "-sh", help="Substitute ~ and $HOME in layout file with actual home directory path")] = False,
        ):
    """
    Launch terminal sessions based on a layout configuration file.
    """
    if layout_path is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()
    layout_path_resolved = find_layout_file(layout_path=layout_path)
    layouts_selected = select_layout(layouts_json_file=layout_path_resolved, selected_layouts_names=choose.split(",") if choose else None, select_interactively=choose_interactively, subsitute_home=subsitute_home)

    # ============= Basic sanity checks =============
    if parallel and len(layouts_selected) > max_layouts:
        raise ValueError(f"Number of layouts {len(layouts_selected)} exceeds the maximum allowed {max_layouts}. Please adjust your layout file.")
    for a_layout in layouts_selected:
        if len(a_layout["layoutTabs"]) > max_tabs:
            typer.echo(f"Layout '{a_layout.get('layoutName', 'Unnamed')}' has {len(a_layout['layoutTabs'])} tabs which exceeds the max of {max_tabs}.")
            confirm = typer.confirm("Do you want to proceed with launching this layout?", default=False)
            if not confirm:
                typer.echo("Aborting launch.")
                raise typer.Exit(0)
    import time
    import platform
    if platform.system() == "Linux" or platform.system() == "Darwin":
        from machineconfig.cluster.sessions_managers.zellij_local_manager import ZellijLocalManager
        if not parallel: iterable = [[item] for item in layouts_selected]
        else: iterable = [layouts_selected]
        for i, a_layouts in enumerate(iterable):
            manager = ZellijLocalManager(session_layouts=a_layouts)
            manager.start_all_sessions(poll_interval=2, poll_seconds=2)
            if monitor:
                manager.run_monitoring_routine(wait_ms=2000)
                if kill_upon_completion:
                    manager.kill_all_sessions()
            if i < len(layouts_selected) - 1:  # Don't sleep after the last layout
                time.sleep(sleep_inbetween)
    elif platform.system() == "Windows":
        from machineconfig.cluster.sessions_managers.wt_local_manager import WTLocalManager
        if not parallel: iterable = [[item] for item in layouts_selected]
        else: iterable = [layouts_selected]
        for i, a_layouts in enumerate(iterable):
            manager = WTLocalManager(session_layouts=a_layouts)
            manager.start_all_sessions()
            if monitor:
                manager.run_monitoring_routine(wait_ms=2000)
                if kill_upon_completion:
                    manager.kill_all_sessions()
            if i < len(layouts_selected) - 1:  # Don't sleep after the last layout
                time.sleep(sleep_inbetween)
    else:
        print(f"❌ Unsupported platform: {platform.system()}")


def create_template(name: Annotated[Optional[str], typer.Argument(..., help="Name of the layout template to create")] = None,
                    num_tabs: Annotated[int, typer.Option(..., "--num-tabs", "-t", help="Number of tabs to include in the template")] = 3,
                    ):
    """Create a layout template file."""
    from machineconfig.utils.schemas.layouts.layout_types import LayoutsFile, TabConfig
    from pathlib import Path
    tabs: list[TabConfig] = []
    for i in range(1, num_tabs + 1):
        tab: TabConfig = {
            "tabName": f"Tab{i}",
            "startDir": "~/" + str(Path.cwd().relative_to(Path.home())),
            "command": "bash",
        }
        tabs.append(tab)
    layouts: list[LayoutConfig] = [
        {
            "layoutName": f"{Path.cwd().name}Layout",
            "layoutTabs": tabs,
        }
    ]
    file: LayoutsFile = {
        "$schema": "https://bit.ly/cfglayout",  # type: ignore
        "version": "0.1",
        "layouts": layouts
    }
    import json
    json_string = json.dumps(file, indent=4)
    if name is None:
        layout_path = Path.cwd() / "layout.json"
    else:
        layout_path = Path.cwd() / (name.replace(".json", "") + ".json")
    layout_path.parent.mkdir(parents=True, exist_ok=True)
    if layout_path.exists():
        print(f"❌ File {layout_path} already exists. Aborting to avoid overwriting.")
        return
    layout_path.write_text(json_string, encoding="utf-8")
    print(f"✅ Created layout template at {layout_path}")


def get_app():
    layouts_app = typer.Typer(help="Layouts management subcommands", no_args_is_help=True, add_help_option=False, add_completion=False)
    from machineconfig.scripts.python.helpers_sessions.sessions_multiprocess import create_from_function

    layouts_app.command("create-from-function", no_args_is_help=True, help="[c] Create a layout from a function")(create_from_function)
    layouts_app.command("c", no_args_is_help=True, help="Create a layout from a function", hidden=True)(create_from_function)

    layouts_app.command("run", no_args_is_help=True, help="[r] Run the selected layout(s)")(run)
    layouts_app.command("r", no_args_is_help=True, help="Run the selected layout(s)", hidden=True)(run)

    layouts_app.command("balance-load", no_args_is_help=True, help="[b] Balance the load across sessions")(balance_load)
    layouts_app.command("b", no_args_is_help=True, help="Balance the load across sessions", hidden=True)(balance_load)

    layouts_app.command("create-template", no_args_is_help=False, help="[t] Create a layout template file")(create_template)
    layouts_app.command("t", no_args_is_help=False, help="Create a layout template file", hidden=True)(create_template)
    return layouts_app


def main():
    layouts_app = get_app()
    layouts_app()


if __name__ == "__main__":
    from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig
