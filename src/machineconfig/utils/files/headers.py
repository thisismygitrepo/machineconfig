
import glob
import os
import platform
import random
from pathlib import Path
from rich import pretty
from rich.console import Console
from rich.text import Text
from typing import Optional


def print_header():
    console = Console()
    pretty.install()
    _header = f"🐍 Python {platform.python_version()} in VE `{os.getenv('VIRTUAL_ENV')}` On {platform.system()} 🐍"
    _header = Text(_header)
    _header.stylize("bold blue")
    console.rule(_header, style="bold red", align="center")
    version = "14.5"
    _ = Text(f"✨ 🐊 Crocodile Shell {version} ✨" + f" Made with 🐍 | Built with ❤️. Running @ {Path.cwd()}")
    _.stylize("#05f8fc on #293536")
    console.print(_)
def print_logo(logo: str):
    from machineconfig.utils.files.ascii_art import font_box_color, character_color, character_or_box_color
    if platform.system() == "Windows":
        _1x = Path.home().joinpath(r"AppData/Roaming/npm/figlet").exists()
        _2x = Path.home().joinpath(r"AppData/Roaming/npm/lolcatjs").exists()
        _3x = Path.home().joinpath(r"AppData/Local/Microsoft/WindowsApps/boxes.exe").exists()
        if _1x and _2x and _3x:
            if random.choice([True, True, False]): font_box_color(logo)
            else: character_color(logo)
        else:
            print("\n" + "🚫 " + "-" * 70 + " 🚫")
            print("🔍 Missing ASCII art dependencies. Install with: iwr bit.ly/cfgasciiartwindows | iex")
            print("🚫 " + "-" * 70 + " 🚫\n")
            _default_art = Path(random.choice(glob.glob(str(Path(__file__).parent.joinpath("art", "*")))))
            print(_default_art.read_text())
    elif platform.system() in ["Linux", "Darwin"]:  # Explicitly handle both Linux and macOS
        def is_executable_in_path(executable_name: str) -> Optional[str]:
            path_dirs = os.environ['PATH'].split(os.pathsep)
            for path_dir in path_dirs:
                path_to_executable = os.path.join(path_dir, executable_name)
                if os.path.isfile(path_to_executable) and os.access(path_to_executable, os.X_OK): return path_to_executable
            return None
        avail_cowsay = is_executable_in_path("cowsay")
        avail_lolcat = is_executable_in_path("lolcat")
        avail_boxes = is_executable_in_path("boxes")
        avail_figlet = is_executable_in_path("figlet")
        if avail_cowsay and avail_lolcat and avail_boxes and avail_figlet:
            _dynamic_art = random.choice([True, True, True, True, False])
            if _dynamic_art: character_or_box_color(logo=logo)
            else: print(Path(random.choice(glob.glob(str(Path(__file__).parent.joinpath("art", "*"))))).read_text())
        else:
            print("\n" + "🚫 " + "-" * 70 + " 🚫")
            install_cmd = "devops install --group TerminalEyeCandy" if platform.system() == "Linux" else "brew install cowsay lolcat boxes figlet"
            print(f"🔍 Missing ASCII art dependencies. Install with: {install_cmd}")
            print("🚫 " + "-" * 70 + " 🚫\n")
            _default_art = Path(random.choice(glob.glob(str(Path(__file__).parent.joinpath("art", "*")))))
            print(_default_art.read_text())
    else:
        print(f"⚠️ Platform {platform.system()} not supported for ASCII art. Using default art.")
        _default_art = Path(random.choice(glob.glob(str(Path(__file__).parent.joinpath("art", "*")))))
        print(_default_art.read_text())
