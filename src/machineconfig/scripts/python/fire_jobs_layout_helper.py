from pathlib import Path
from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig, LayoutsFile
from typing import Optional, TYPE_CHECKING
from machineconfig.scripts.python.helpers.helpers4 import search_for_files_of_interest
from machineconfig.utils.options import choose_from_options
from machineconfig.utils.path_helper import match_file_name, sanitize_path
from machineconfig.utils.path_extended import PathExtended as PathExtended

if TYPE_CHECKING:
    from machineconfig.scripts.python.fire_jobs_args_helper import FireJobArgs


def select_layout(layouts_json_file: Path, layouts_name: Optional[list[str]]) -> list[LayoutConfig]:
    import json
    layout_file: LayoutsFile = json.loads(layouts_json_file.read_text(encoding="utf-8"))
    if len(layout_file["layouts"]) == 0:
        raise ValueError(f"No layouts found in {layouts_json_file}")
    if layouts_name is None:
        options = [layout["layoutName"] for layout in layout_file["layouts"]]
        from machineconfig.utils.options import choose_from_options
        layouts_name = choose_from_options(multi=True, options=options, prompt="Choose a layout configuration:", fzf=True, msg="Choose one option")
    print(f"Selected layout(s): {layouts_name}")
    # layout_chosen = next((layout for layout in layout_file["layouts"] if layout["layoutName"] == layouts_name), None)
    # if layout_chosen is None:
        # layout_chosen = next((layout for layout in layout_file["layouts"] if layout["layoutName"].lower() == layouts_name.lower()), None)
    # if layout_chosen is None:
        # available_layouts = [layout["layoutName"] for layout in layout_file["layouts"]]
        # raise ValueError(f"Layout '{layouts_name}' not found. Available layouts: {available_layouts}")
    layouts_chosen: list[LayoutConfig] = []
    for name in layouts_name:
        layout_chosen = next((layout for layout in layout_file["layouts"] if layout["layoutName"] == name), None)
        if layout_chosen is None:
            layout_chosen = next((layout for layout in layout_file["layouts"] if layout["layoutName"].lower() == name.lower()), None)
        if layout_chosen is None:
            available_layouts = [layout["layoutName"] for layout in layout_file["layouts"]]
            raise ValueError(f"Layout '{name}' not found. Available layouts: {available_layouts}")
        layouts_chosen.append(layout_chosen)
    return layouts_chosen


def launch_layout(layout_config: LayoutConfig) -> Optional[Exception]:
    import platform
    if platform.system() == "Linux" or platform.system() == "Darwin":
        print("🧑‍💻 Launching layout using Zellij terminal multiplexer...")
        from machineconfig.cluster.sessions_managers.zellij_local import run_zellij_layout
        run_zellij_layout(layout_config=layout_config)
    elif platform.system() == "Windows":
        print("🧑‍💻 Launching layout using Windows Terminal...")
        from machineconfig.cluster.sessions_managers.wt_local import run_wt_layout

        run_wt_layout(layout_config=layout_config)
    else:
        print(f"❌ Unsupported platform: {platform.system()}")
    return None


def handle_layout_args(args: "FireJobArgs") -> None:
    # args.function = args.path
    # args.path = "layout.json"
    path_obj = sanitize_path(args.path)
    if not path_obj.exists():
        choice_file = match_file_name(sub_string=args.path, search_root=PathExtended.cwd(), suffixes={".json"})
    elif path_obj.is_dir():
        print(f"🔍 Searching recursively for Python, PowerShell and Shell scripts in directory `{path_obj}`")
        files = search_for_files_of_interest(path_obj)
        print(f"🔍 Got #{len(files)} results.")
        choice_file = choose_from_options(multi=False, options=files, fzf=True, msg="Choose one option")
        choice_file = PathExtended(choice_file)
    else:
        choice_file = path_obj
    if args.function is None: layouts_name = None
    else: layouts_name = args.function.split(",")
    for a_layout_config in select_layout(layouts_json_file=choice_file, layouts_name=layouts_name):
        launch_layout(layout_config=a_layout_config)
