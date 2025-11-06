
from types import FunctionType
from typing import Optional, Literal
from machineconfig.utils.schemas.layouts.layout_types import TabConfig, LayoutConfig
from pathlib import Path

def get_fire_tab_using_uv(func: FunctionType, tab_weight: int, import_module: bool, uv_with: Optional[list[str]], uv_project_dir: Optional[str]) -> tuple[TabConfig, Path]:
    from machineconfig.utils.meta import lambda_to_python_script
    if func.__name__ == "<lambda>":
        py_script =  lambda_to_python_script(func,
                                             in_global=True, import_module=import_module)
    else:
        py_script =  lambda_to_python_script(lambda: func(),
                                             in_global=True, import_module=import_module)
    from machineconfig.utils.code import get_uv_command_executing_python_script
    command_to_run, py_script_path = get_uv_command_executing_python_script(python_script=py_script, uv_with=uv_with, uv_project_dir=uv_project_dir)
    tab_config: TabConfig = {
        "command": command_to_run,
        "startDir": "$HOME",
        "tabName": func.__name__,
        "tabWeight": tab_weight
    }
    return tab_config, py_script_path
def get_fire_tab_using_fire(func: FunctionType, tab_weight: int) -> TabConfig:
    import inspect
    from machineconfig.utils.source_of_truth import CONFIG_ROOT
    import platform
    if platform.system().lower() == "windows":
        wrap_mcfg = CONFIG_ROOT / "scripts/wrap_mcfg.ps1"
        wrap_mcfg = f'& "{wrap_mcfg}"'
    elif platform.system().lower() == "linux" or platform.system().lower() == "darwin":
        wrap_mcfg = CONFIG_ROOT / "scripts/wrap_mcfg"
    else:
        raise ValueError(f"Unsupported platform: {platform.system()}")
    path = Path(inspect.getfile(func))
    path_relative = path.relative_to(Path.home())
    command_to_run = f"""{wrap_mcfg} fire {path_relative} {func.__name__} """
    tab_config: TabConfig = {
        "command": command_to_run,
        "startDir": "$HOME",
        "tabName": func.__name__,
        "tabWeight": tab_weight
    }
    return tab_config



def make_layout_from_functions(functions: list[FunctionType], functions_weights: Optional[list[int]], import_module: bool, tab_configs: list[TabConfig],
                               layout_name: str, method: Literal["script", "fire"],
                               uv_with: Optional[list[str]] = None, uv_project_dir: Optional[str] = None
                               ) -> LayoutConfig:
    tabs2artifacts: list[tuple[TabConfig, list[Path]]] = []
    for a_func, tab_weight in zip(functions, functions_weights or [1]*len(functions)):
        match method:
            case "script":
                tab_config, artifact_files_1 = get_fire_tab_using_uv(a_func, tab_weight=tab_weight, import_module=import_module,
                                                                     uv_with=uv_with, uv_project_dir=uv_project_dir
                                                                     )
                artifact_files = [artifact_files_1]
            case "fire":
                tab_config = get_fire_tab_using_fire(a_func, tab_weight=tab_weight)
                artifact_files = []
        tabs2artifacts.append((tab_config, artifact_files))
    list_of_tabs = [tab for tab, _ in tabs2artifacts] + tab_configs
    layout_config: LayoutConfig = {
        "layoutName": layout_name,
        "layoutTabs": list_of_tabs,
    }
    return layout_config
