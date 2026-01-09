from typing import Any, Literal, overload
import platform


@overload
def choose_from_dict_with_preview(options_to_preview_mapping: dict[str, Any], extension: str | None, multi: Literal[False]) -> str | None: ...
@overload
def choose_from_dict_with_preview(options_to_preview_mapping: dict[str, Any], extension: str | None, multi: Literal[True]) -> list[str]: ...
@overload
def choose_from_dict_with_preview(options_to_preview_mapping: dict[str, Any]) -> str | None: ...
def choose_from_dict_with_preview(options_to_preview_mapping: dict[str, Any], extension: str | None = None, multi: bool = False) -> str | list[str] | None:
    """
    Interactive selection from a dict where keys are selectable options and values are previewed with syntax highlighting.
    Uses `tv` (television) as the fuzzy finder with bat for preview.
    """
    if not options_to_preview_mapping:
        return [] if multi else None
    system = platform.system()
    if system == "Windows":
        from machineconfig.utils.options_utils.options_tv_windows import main as _main_windows
        return _main_windows(options_to_preview_mapping, extension=extension, multi=multi)
    else:
        from machineconfig.utils.options_utils.options_tv_linux import main as _main_linux
        return _main_linux(options_to_preview_mapping, extension=extension, multi=multi)


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
    result = choose_from_dict_with_preview(demo_mapping, extension="py", multi=True)
    print(f"Selected: {result}")
