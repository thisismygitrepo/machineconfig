"""Pure Python implementations for sessions commands - no typer dependencies."""

from pathlib import Path
from typing import Literal

from machineconfig.cluster.sessions_managers.zellij.zellij_utils.monitoring_types import StartResult


def select_layout(layouts_json_file: str, selected_layouts_names: list[str], select_interactively: bool) -> list["LayoutConfig"]:
    """Select layout(s) from a layout file."""
    import json
    from machineconfig.utils.schemas.layouts.layout_types import LayoutsFile
    json_str = Path(layouts_json_file).read_text(encoding="utf-8")
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
        # options = [layout["layoutName"] for layout in layout_file["layouts"]]
        # from machineconfig.utils.options import choose_from_options
        # selected_layouts_names = choose_from_options(multi=True, options=options, prompt="Choose a layout configuration:", tv=True, msg="Choose one option")
        from machineconfig.utils.options_utils.tv_options import choose_from_dict_with_preview
        selected_layouts_names = choose_from_dict_with_preview(
            {layout["layoutName"]: json.dumps(layout, indent=4) for layout in layout_file["layouts"]},
            extension="json",
            multi=True,
            preview_size_percent=40,
        )

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
    sleep_inbetween: float,
    monitor: bool,
    parallel_layouts: int | None,
    kill_upon_completion: bool,
    backend: Literal["zellij", "windows-terminal", "tmux"],
    layouts_selected: list["LayoutConfig"],
) -> None:
    """Launch terminal sessions based on a layout configuration file."""
    import time
    monitor_requested = monitor
    monitor = monitor or (parallel_layouts is not None)
    if parallel_layouts is not None and not monitor_requested:
        print("Note: --parallel-layouts implies --monitor; waiting for each batch to finish before launching the next one.")
    if parallel_layouts is not None and parallel_layouts <= 0:
        raise ValueError("parallel_layouts must be a positive integer when provided")

    if parallel_layouts is None:
        iterable: list[list["LayoutConfig"]] = [layouts_selected]
    else:
        iterable = [layouts_selected[index:index + parallel_layouts] for index in range(0, len(layouts_selected), parallel_layouts)]

    def raise_on_failed_start(start_results: dict[str, StartResult], backend_name: str) -> None:
        failures = {name: result for name, result in start_results.items() if not result.get("success", False)}
        if failures:
            details = "; ".join(f"{name}: {result.get('error', 'unknown error')}" for name, result in failures.items())
            raise ValueError(f"{backend_name} session start failure(s): {details}")
    match backend:
        case "zellij":
            from machineconfig.cluster.sessions_managers.zellij.zellij_local_manager import ZellijLocalManager
            for i, a_layouts in enumerate(iterable):
                manager = ZellijLocalManager(session_layouts=a_layouts)
                start_results = manager.start_all_sessions(poll_interval=2, poll_seconds=10)
                raise_on_failed_start(start_results, "Zellij")
                if monitor:
                    manager.run_monitoring_routine(wait_ms=2000)
                    if kill_upon_completion:
                        manager.kill_all_sessions()
                if i < len(iterable) - 1:
                    time.sleep(sleep_inbetween)
        case "windows-terminal":
            from machineconfig.cluster.sessions_managers.windows_terminal.wt_local_manager import WTLocalManager
            for i, a_layouts in enumerate(iterable):
                manager = WTLocalManager(session_layouts=a_layouts, session_name_prefix=None)
                start_results = manager.start_all_sessions()
                raise_on_failed_start(start_results, "Windows Terminal")
                if monitor:
                    manager.run_monitoring_routine(wait_ms=2000)
                    if kill_upon_completion:
                        manager.kill_all_sessions()
                if i < len(iterable) - 1:
                    time.sleep(sleep_inbetween)
        case "tmux":
            from machineconfig.cluster.sessions_managers.tmux.tmux_local_manager import TmuxLocalManager
            for i, a_layouts in enumerate(iterable):
                manager = TmuxLocalManager(session_layouts=a_layouts, session_name_prefix=None)
                start_results = manager.start_all_sessions()
                raise_on_failed_start(start_results, "tmux")
                if monitor:
                    manager.run_monitoring_routine(wait_ms=2000)
                    if kill_upon_completion:
                        manager.kill_all_sessions()
                if i < len(iterable) - 1:
                    time.sleep(sleep_inbetween)
        case _:
            raise ValueError(f"Unsupported backend: {backend}")


if __name__ == "__main__":
    from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig
    _ = LayoutConfig
