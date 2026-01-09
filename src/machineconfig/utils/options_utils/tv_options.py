from typing import Any
import platform


def choose_from_dict_with_preview(options_to_preview_mapping: dict[str, Any], extension: str | None = None) -> str | None:
    """
    Interactive selection from a dict where keys are selectable options and values are previewed with syntax highlighting.
    Uses `tv` (television) as the fuzzy finder with bat for preview.
    """
    if not options_to_preview_mapping:
        return None
    system = platform.system()
    if system == "Windows":
        from machineconfig.utils.options_utils.options_tv_windows import main as _main_windows
        return _main_windows(options_to_preview_mapping, extension=extension)
    else:
        from machineconfig.utils.options_utils.options_tv_linux import main as _main_linux
        return _main_linux(options_to_preview_mapping, extension=extension)


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
    result = choose_from_dict_with_preview(demo_mapping, extension="py")
    print(f"Selected: {result}")
