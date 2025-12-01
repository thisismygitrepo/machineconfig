

from typing import Optional, Annotated
import typer


def create_from_function(
        num_process: Annotated[int, typer.Option(..., "--num-process", "-n", help="Number of parallel processes to run")],
        path: Annotated[str, typer.Option(..., "--path", "-p", help="Path to a Python or Shell script file or a directory containing such files")] = ".",
        function: Annotated[Optional[str], typer.Option(..., "--function", "-f", help="Function to run from the Python file. If not provided, you will be prompted to choose.")] = None,
):
    from machineconfig.utils.ve import get_ve_path_and_ipython_profile
    from machineconfig.utils.options import choose_from_options
    from machineconfig.utils.path_helper import match_file_name, sanitize_path
    from machineconfig.utils.accessories import get_repo_root
    from pathlib import Path

    path_obj = sanitize_path(path)
    if not path_obj.exists():
        suffixes = {".py"}
        choice_file = match_file_name(sub_string=path, search_root=Path.cwd(), suffixes=suffixes)
    elif path_obj.is_dir():
        from machineconfig.utils.path_helper import search_for_files_of_interest
        print(f"🔍 Searching recursively for Python, PowerShell and Shell scripts in directory `{path_obj}`")
        files = search_for_files_of_interest(path_obj, suffixes={".py", ".sh", ".ps1"})
        print(f"🔍 Got #{len(files)} results.")
        choice_file = choose_from_options(multi=False, options=files, tv=True, msg="Choose one option")
        choice_file = Path(choice_file)
    else:
        choice_file = path_obj


    repo_root = get_repo_root(Path(choice_file))
    print(f"💾 Selected file: {choice_file}.\nRepo root: {repo_root}")
    ve_root_from_file, ipy_profile = get_ve_path_and_ipython_profile(choice_file)
    if ipy_profile is None:
        ipy_profile = "default"
    # if ve_root_from_file is None:
    #     raise ValueError(f"Could not determine virtual environment for file {choice_file}. Please ensure it is within a recognized project structure.")
    # _activate_ve_line = get_ve_activate_line(ve_root=ve_root_from_file)
    if ve_root_from_file is not None:
        start_dir = Path(ve_root_from_file).parent
    else:
        start_dir = Path.cwd()

    # =========================  choosing function to run
    if function is None or function.strip() == "":
        from machineconfig.scripts.python.helpers.helpers_fire_command.fire_jobs_route_helper import choose_function_or_lines
        choice_function, choice_file, _kwargs_dict = choose_function_or_lines(choice_file, kwargs_dict={})
    else:
        choice_function = function

    from machineconfig.cluster.sessions_managers.zellij_local import run_zellij_layout
    from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig
    layout: LayoutConfig = {"layoutName": "fireNprocess", "layoutTabs": []}
    for an_arg in range(num_process):
        layout["layoutTabs"].append({
            "tabName": f"tab{an_arg}",
            "startDir": str(start_dir),
            "command": f"uv run python -m fire {choice_file} {choice_function} --idx={an_arg} --idx_max={num_process}"
            })
    print(layout)
    run_zellij_layout(layout_config=layout)

