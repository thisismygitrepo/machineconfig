"""
Choose a theme for Wezterm
"""

from machineconfig.utils.options import choose_from_options
from machineconfig.utils.path_extended import PathExtended
from typing import Any
import time
from rich.panel import Panel
from rich.console import Console
import curses

console = Console()


schemes_list = [
    "Pro",
    "Spiderman",
    "shades-of-purple",
    "synthwave",
    "Symfonic",
    "PaulMillr",
    "Neon",
    "LiquidCarbonTransparentInverse",
    "Laser",
    "IR_Black",
    "Hurtado",
    "Homebrew",
    "Hipster Green",
    "Firefly Traditional",
    "Elementary",
    "deep",
    "Dark Pastel",
    "Bright Lights",
    "Adventure",
    "Nancy (terminal.sexy)",
    "Bim (Gogh)",
    "BlueDolphin",
    "Borland",
    "Grass (Gogh)",
    "Greenscreen (light) (terminal.sexy)",
    "Grayscale (dark) (terminal.sexy)",
]


def main2():
    console.print(Panel("🎨 WezTerm Theme Selector", title_align="left", border_style="green"))
    option = choose_from_options(multi=False, options=schemes_list, header="Choose a theme for Wezterm", tv=True, msg="Use arrow keys to navigate, Enter to select a theme")
    set_theme(option)
    print(f"✅ Theme set to: {option}")


def set_theme(theme: str):
    print(f"🔄 Setting WezTerm theme to: {theme}")
    txt_lines = PathExtended.home().joinpath(".config/wezterm/wezterm.lua").expanduser().read_text(encoding="utf-8").splitlines()
    res_lines = []
    for line in txt_lines:
        if "config.color_scheme = " in line:
            res_lines.append(f"config.color_scheme = '{theme}'")
        else:
            res_lines.append(line)
    PathExtended.home().joinpath(".config/wezterm/wezterm.lua").expanduser().write_text("\n".join(res_lines), encoding="utf-8")
    time.sleep(0.1)
    print("💾 Configuration saved")


def main():
    console.print(Panel("🎨 WezTerm Theme Selector - Interactive Mode", title_align="left", border_style="blue"))
    print("""
📝 Use arrow keys to navigate, Enter to select a theme
""")
    curses.wrapper(accessory)
    console.print(Panel("✅ Theme selection completed", title_align="left", border_style="green"))


def accessory(stdscr: Any):
    options = schemes_list
    current_option = 0
    page_size = stdscr.getmaxyx()[0] - 1  # curses.LINES - 1  # Number of lines in the terminal, -1 for status line

    while True:
        stdscr.clear()

        # Calculate start and end indices for options
        start_index = (current_option // page_size) * page_size
        end_index = start_index + page_size

        # Display options
        for i, option in enumerate(options[start_index:end_index]):
            if start_index + i == current_option:
                stdscr.addstr(i, 0, f"➤ {option}", curses.A_REVERSE)  # Highlighted with arrow
            else:
                stdscr.addstr(i, 0, f"  {option}")

        # Display status line
        status_line = f"🔍 Theme {current_option + 1}/{len(options)} | ↑/↓: Navigate | Enter: Select"
        stdscr.addstr(page_size, 0, status_line)

        # Get key press
        key = stdscr.getch()

        # Handle key press
        if key == curses.KEY_UP and current_option > 0:
            current_option -= 1
        elif key == curses.KEY_DOWN and current_option < len(options) - 1:
            current_option += 1
        elif key == ord("\n"):  # Enter key
            break  # Exit the loop
        set_theme(options[current_option])
