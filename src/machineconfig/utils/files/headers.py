
import glob
import os
import platform
import random
from pathlib import Path
from rich import pretty
from rich.console import Console


def print_header():
    console = Console()
    pretty.install()

    # Environment Information Panel
    from rich.panel import Panel
    from rich.table import Table

    table = Table(show_header=False, show_edge=False, pad_edge=False)
    table.add_column("Label", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    table.add_row("Python Version", platform.python_version())
    table.add_row("Operating System", platform.system())
    table.add_row("Virtual Environment", os.getenv('VIRTUAL_ENV', 'None'))
    table.add_row("Running @", str(Path.cwd()))

    from machineconfig.utils.installer_utils.installer_runner import get_machineconfig_version

    console.print(Panel(table, title=f"[bold blue]✨ 🐊 Machineconfig Shell {get_machineconfig_version()} ✨ Made with 🐍 | Built with ❤️[/bold blue]", border_style="blue"))
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
            # print("\n" + "🚫 " + "-" * 70 + " 🚫")
            # print("🔍 Missing ASCII art dependencies. Install with: iwr bit.ly/cfgasciiartwindows | iex")
            # print("🚫 " + "-" * 70 + " 🚫\n")
            _default_art = Path(random.choice(glob.glob(str(Path(__file__).parent.joinpath("art", "*")))))
            print(_default_art.read_text())
    elif platform.system() in ["Linux", "Darwin"]:  # Explicitly handle both Linux and macOS
        from machineconfig.utils.installer_utils.installer_locator_utils import is_executable_in_path
        avail_cowsay = is_executable_in_path("cowsay")
        avail_lolcat = is_executable_in_path("lolcat")
        avail_boxes = is_executable_in_path("boxes")
        avail_figlet = is_executable_in_path("figlet")
        if avail_cowsay and avail_lolcat and avail_boxes and avail_figlet:
            # _dynamic_art = random.choice([True, True, True, True, False])
            # if _dynamic_art: character_or_box_color(logo=logo)
            # else:
            #     print(Path(random.choice(glob.glob(str(Path(__file__).parent.joinpath("art", "*"))))).read_text())
            character_or_box_color(logo=logo)
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
