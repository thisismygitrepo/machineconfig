
from types import FunctionType
from typing import Optional, Literal
from machineconfig.utils.schemas.layouts.layout_types import TabConfig, LayoutConfig
from pathlib import Path

def get_fire_tab_using_uv(func: FunctionType, import_module: bool, uv_with: Optional[list[str]], uv_project_dir: Optional[str]) -> tuple[TabConfig, Path]:
    from machineconfig.utils.meta import lambda_to_python_script
    py_script =  lambda_to_python_script(lmb=lambda: func, in_global=True, import_module=import_module)
    from machineconfig.utils.code import get_uv_command_executing_python_script
    command_to_run, py_script_path = get_uv_command_executing_python_script(python_script=py_script, uv_with=uv_with, uv_project_dir=uv_project_dir)
    tab_config: TabConfig = {
        "command": command_to_run,
        "startDir": "$HOME",
        "tabName": func.__name__
    }
    return tab_config, py_script_path
def get_fire_tab_using_fire(func: FunctionType):
    import inspect
    from machineconfig.utils.source_of_truth import CONFIG_ROOT
    import platform
    if platform.system().lower() == "windows":
        mcfgs = CONFIG_ROOT / "scripts/windows/mcfgs.ps1"
        mcfgs = f'& "{mcfgs}"'
    elif platform.system().lower() == "linux" or platform.system().lower() == "darwin":
        mcfgs = CONFIG_ROOT / "scripts/linux/mcfgs"
    else:
        raise ValueError(f"Unsupported platform: {platform.system()}")
    path = Path(inspect.getfile(func))
    path_relative = path.relative_to(Path.home())
    command_to_run = f"""{mcfgs} fire {path_relative} {func.__name__} """
    tab_config: TabConfig = {
        "command": command_to_run,
        "startDir": "$HOME",
        "tabName": func.__name__
    }
    return tab_config



def make_layout_from_functions(functions: list[FunctionType], import_module: bool, tab_configs: list[TabConfig], layout_name: str, method: Literal["script", "fire"]="fire") -> LayoutConfig:
    tabs2artifacts: list[tuple[TabConfig, list[Path]]] = []
    for a_func in functions:
        match method:
            case "script":
                tab_config, artifact_files_1 = get_fire_tab_using_uv(a_func, import_module=import_module, uv_with=None, uv_project_dir=None)
                artifact_files = [artifact_files_1]
            case "fire":
                tab_config = get_fire_tab_using_fire(a_func)
                artifact_files = []
        tabs2artifacts.append((tab_config, artifact_files))
    list_of_tabs = [tab for tab, _ in tabs2artifacts] + tab_configs
    layout_config: LayoutConfig = {
        "layoutName": layout_name,
        "layoutTabs": list_of_tabs,
    }
    return layout_config
