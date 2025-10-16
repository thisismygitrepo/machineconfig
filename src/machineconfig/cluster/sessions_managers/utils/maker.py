
from types import FunctionType
from typing import Literal
from machineconfig.utils.schemas.layouts.layout_types import TabConfig, LayoutConfig
from pathlib import Path

def get_fire_command_and_artifact_files(func: FunctionType):
    from machineconfig.utils.meta import function_to_script
    py_script =  function_to_script(func)
    from machineconfig.utils.accessories import randstr
    py_script_path = Path.home().joinpath("tmp_results", "tmp_py_scripts", f"tmp_{randstr(10)}.py")
    py_script_path.parent.mkdir(parents=True, exist_ok=True)
    py_script_path.write_text(py_script, encoding="utf-8")
    command_to_run = f"uv run --project $HOME/ {py_script_path}"
    tab_config: TabConfig = {
        "command": command_to_run,
        "startDir": "$HOME",
        "tabName": func.__name__
    }
    return tab_config, py_script_path
def get_fire_command_and_artifact_files_v2(func: FunctionType):
    import inspect
    path = Path(inspect.getfile(func))
    path_relative = path.relative_to(Path.home())
    command_to_run = f"""$HOME/.local/bin/fire {path_relative} {func.__name__} """
    tab_config: TabConfig = {
        "command": command_to_run,
        "startDir": "$HOME",
        "tabName": func.__name__
    }
    return tab_config


def make_layout_from_functions(functions: list[FunctionType], tab_configs: list[TabConfig], layout_name: str, method: Literal["script", "fire"]="fire") -> LayoutConfig:
    tabs2artifacts: list[tuple[TabConfig, list[Path]]] = []
    for a_func in functions:
        match method:
            case "script":
                tab_config, artifact_files_1 = get_fire_command_and_artifact_files(a_func)
                artifact_files = [artifact_files_1]
            case "fire":
                tab_config = get_fire_command_and_artifact_files_v2(a_func)
                artifact_files = []
        tabs2artifacts.append((tab_config, artifact_files))
    list_of_tabs = [tab for tab, _ in tabs2artifacts] + tab_configs
    layout_config: LayoutConfig = {
        "layoutName": layout_name,
        "layoutTabs": list_of_tabs,
    }
    return layout_config
