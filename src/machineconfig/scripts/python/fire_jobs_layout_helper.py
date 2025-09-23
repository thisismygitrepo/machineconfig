from pathlib import Path
from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig, LayoutsFile
from typing import Optional, TYPE_CHECKING
from machineconfig.scripts.python.helpers.helpers4 import search_for_files_of_interest
from machineconfig.utils.options import choose_one_option
from machineconfig.utils.path import match_file_name, sanitize_path
from machineconfig.utils.path_reduced import PathExtended as PathExtended

if TYPE_CHECKING:
    from machineconfig.scripts.python.fire_jobs_args_helper import FireJobArgs


def select_layout(layouts_json_file: Path, layout_name: Optional[str]):
    import json

    layout_file: LayoutsFile = json.loads(layouts_json_file.read_text(encoding="utf-8"))
    if len(layout_file["layouts"]) == 0:
        raise ValueError(f"No layouts found in {layouts_json_file}")
    if layout_name is None:
        options = [layout["layoutName"] for layout in layout_file["layouts"]]
        from machineconfig.utils.options import choose_one_option

        layout_name = choose_one_option(options=options, prompt="Choose a layout configuration:", fzf=True)
    print(f"Selected layout: {layout_name}")
    layout_chosen = next((layout for layout in layout_file["layouts"] if layout["layoutName"] == layout_name), None)
    if layout_chosen is None:
        layout_chosen = next((layout for layout in layout_file["layouts"] if layout["layoutName"].lower() == layout_name.lower()), None)
    if layout_chosen is None:
        available_layouts = [layout["layoutName"] for layout in layout_file["layouts"]]
        raise ValueError(f"Layout '{layout_name}' not found. Available layouts: {available_layouts}")
    return layout_chosen


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
        choice_file = choose_one_option(options=files, fzf=True)
        choice_file = PathExtended(choice_file)
    else:
        choice_file = path_obj
    launch_layout(layout_config=select_layout(layouts_json_file=choice_file, layout_name=args.function))
