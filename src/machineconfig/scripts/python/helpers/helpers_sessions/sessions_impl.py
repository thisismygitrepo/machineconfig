"""Pure Python implementations for sessions commands - no typer dependencies."""

# from typing import Optional
from pathlib import Path


def select_layout(layouts_json_file: str, selected_layouts_names: list[str], select_interactively: bool, subsitute_home: bool) -> list["LayoutConfig"]:
    """Select layout(s) from a layout file."""
    import json
    from machineconfig.utils.schemas.layouts.layout_types import LayoutsFile
    json_str = Path(layouts_json_file).read_text(encoding="utf-8")
    if subsitute_home:
        json_str = json_str.replace("~", str(Path.home())).replace("$HOME", str(Path.home()))
        json_str = json_str.replace("""Command": "f """, """Command": "~/.config/machineconfig/scripts/wrap_mcfg fire """)
        json_str = json_str.replace("""Command": "s """, """Command": "~/.config/machineconfig/scripts/wrap_mcfg sessions """)
    try:
        layout_file: LayoutsFile = json.loads(json_str)
    except Exception:
        print(f"Failed to parse the json file {layouts_json_file}, trying to clean the comments and giving it another shot ... ")
        from machineconfig.utils.io import remove_c_style_comments
        json_str = remove_c_style_comments(json_str)
        layout_file: LayoutsFile = json.loads(json_str)
    if len(layout_file["layouts"]) == 0:
        raise ValueError(f"No layouts found in {layouts_json_file}")
    if len(selected_layouts_names) == 0:
        if not select_interactively:
            return layout_file["layouts"]
        options = [layout["layoutName"] for layout in layout_file["layouts"]]
        from machineconfig.utils.options import choose_from_options
        selected_layouts_names = choose_from_options(multi=True, options=options, prompt="Choose a layout configuration:", tv=True, msg="Choose one option")
    print(f"Selected layout(s): {selected_layouts_names}")
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
def start_wt(layouts_names: list[str], layouts_file: Path) -> tuple[str, str | None]:
    """Start a Windows Terminal layout by name. Returns tuple of (status, message) where status is 'success' or 'error'."""
    import json
    from machineconfig.utils.schemas.layouts.layout_types import LayoutsFile
    from machineconfig.cluster.sessions_managers.wt_local import run_wt_layout
    layouts_data: LayoutsFile = json.loads(layouts_file.read_text(encoding="utf-8"))
    if len(layouts_names) == 0:
        from machineconfig.utils.options_utils.tv_options import choose_from_dict_with_preview
        layouts_names = choose_from_dict_with_preview(
            {layout["layoutName"]: json.dumps(layout, indent=4) for layout in layouts_data["layouts"]},
            extension="json",
            multi=True,
            preview_size_percent=40,
        )
        if len(layouts_names) == 0:
            return ("error", "❌ No layout selected.")

    for a_layout_name in layouts_names:
        chosen_layout = next((a_layout for a_layout in layouts_data["layouts"] if a_layout["layoutName"] == a_layout_name), None)
        if not chosen_layout:
            available_layouts = [a_layout["layoutName"] for a_layout in layouts_data["layouts"]]
            return ("error", f"❌ Layout '{a_layout_name}' not found in layouts file.\nAvailable layouts: {', '.join(available_layouts)}")
        run_wt_layout(layout_config=chosen_layout)
    return ("success", None)

def find_layout_file(layout_path: str) -> str:
    """Find layout file from a path."""
    from machineconfig.utils.path_helper import search_for_files_of_interest, match_file_name, sanitize_path
    from machineconfig.utils.options import choose_from_options
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


def run_layouts(
    layout_path: str,
    max_tabs: int,
    max_layouts: int,
    sleep_inbetween: float,
    monitor: bool,
    parallel: bool,
    kill_upon_completion: bool,
    choose: list[str],
    choose_interactively: bool,
    subsitute_home: bool,
) -> None:
    """Launch terminal sessions based on a layout configuration file."""
    layouts_selected = select_layout(layouts_json_file=layout_path, selected_layouts_names=choose, select_interactively=choose_interactively, subsitute_home=subsitute_home)

    if parallel and len(layouts_selected) > max_layouts:
        raise ValueError(f"Number of layouts {len(layouts_selected)} exceeds the maximum allowed {max_layouts}. Please adjust your layout file.")
    for a_layout in layouts_selected:
        if len(a_layout["layoutTabs"]) > max_tabs:
            raise ValueError(f"Layout '{a_layout.get('layoutName', 'Unnamed')}' has {len(a_layout['layoutTabs'])} tabs which exceeds the max of {max_tabs}.")

    import time
    import platform
    if platform.system() == "Linux" or platform.system() == "Darwin":
        from machineconfig.cluster.sessions_managers.zellij_local_manager import ZellijLocalManager
        if not parallel:
            iterable = [[item] for item in layouts_selected]
        else:
            iterable = [layouts_selected]
        for i, a_layouts in enumerate(iterable):
            manager = ZellijLocalManager(session_layouts=a_layouts)
            manager.start_all_sessions(poll_interval=2, poll_seconds=2)
            if monitor:
                manager.run_monitoring_routine(wait_ms=2000)
                if kill_upon_completion:
                    manager.kill_all_sessions()
            if i < len(layouts_selected) - 1:
                time.sleep(sleep_inbetween)
    elif platform.system() == "Windows":
        from machineconfig.cluster.sessions_managers.wt_local_manager import WTLocalManager
        if not parallel:
            iterable = [[item] for item in layouts_selected]
        else:
            iterable = [layouts_selected]
        for i, a_layouts in enumerate(iterable):
            manager = WTLocalManager(session_layouts=a_layouts)
            manager.start_all_sessions()
            if monitor:
                manager.run_monitoring_routine(wait_ms=2000)
                if kill_upon_completion:
                    manager.kill_all_sessions()
            if i < len(layouts_selected) - 1:
                time.sleep(sleep_inbetween)
    else:
        print(f"❌ Unsupported platform: {platform.system()}")




if __name__ == "__main__":
    from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig