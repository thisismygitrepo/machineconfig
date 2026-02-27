"""CLI implementation for sessions run command."""

from pathlib import Path
import platform
from typing import Optional, Literal, cast

import typer

from machineconfig.scripts.python.helpers.helpers_sessions.sessions_impl import run_layouts, find_layout_file, select_layout
from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig, TabConfig, substitute_home


def run_cli(
    ctx: typer.Context,
    layouts_file: Optional[str],
    choose_layouts: Optional[str],
    choose_tabs: Optional[str],
    sleep_inbetween: float,
    parallel_layouts: Optional[int],
    max_tabs: int,
    max_layouts: int,
    backend: Literal["zellij", "z", "windows-terminal", "wt", "tmux", "t", "auto", "a"],
    max_parallel_tabs: Optional[int],
    poll_seconds: float,
    kill_finished_tabs: bool,
    all_file: bool,
    monitor: bool,
    kill_upon_completion: bool,
    subsitute_home: bool,
) -> None:
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
                sleep_inbetween=sleep_inbetween,
                monitor=monitor,
                parallel_layouts=parallel_layouts,
                kill_upon_completion=kill_upon_completion,
                layouts_selected=layouts_selected,
                backend=backend_resolved,
            )
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(1) from e
