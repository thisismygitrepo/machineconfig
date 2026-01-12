from typing import Any, Literal, overload
import platform


@overload
def choose_from_dict_with_preview(options_to_preview_mapping: dict[str, Any], extension: str | None, multi: Literal[False], preview_size_percent: float) -> str | None: ...
@overload
def choose_from_dict_with_preview(options_to_preview_mapping: dict[str, Any], extension: str | None, multi: Literal[True], preview_size_percent: float) -> list[str]: ...
def choose_from_dict_with_preview(options_to_preview_mapping: dict[str, Any], extension: str | None, multi: bool, preview_size_percent: float) -> str | list[str] | None:
    if not options_to_preview_mapping:
        return [] if multi else None
    system = platform.system()
    if system == "Windows":
        from machineconfig.utils.options_utils.options_tv_windows import select_from_options
        return select_from_options(options_to_preview_mapping, extension=extension, multi=multi, preview_size_percent=preview_size_percent)
    else:
        from machineconfig.utils.options_utils.options_tv_linux import select_from_options
        return select_from_options(options_to_preview_mapping, extension=extension, multi=multi, preview_size_percent=preview_size_percent)


if __name__ == "__main__":
    demo_mapping: dict[str, str] = {
        "config.py": """from pathlib import Path

CONFIG_DIR = Path.home() / ".config"
DEBUG = True
""",
        "utils.py": """def greet(name: str) -> str:
    return f"Hello, {name}!"
""",
        "main.rs": """fn main() {
    println!("Hello, world!");
}
""",
    }
    result = choose_from_dict_with_preview(demo_mapping, extension="py", multi=True, preview_size_percent=50)
    print(f"Selected: {result}")
