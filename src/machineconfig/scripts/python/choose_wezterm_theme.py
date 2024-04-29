
"""
Choose a theme for Wezterm
"""

from machineconfig.utils.utils import choose_one_option, P
from typing import Any
import time


schemes_list = [
    'Pro',
    'Spiderman',
    'shades-of-purple',
    'synthwave',
    'Symfonic',
    'PaulMillr',
    'Neon',
    'LiquidCarbonTransparentInverse',
    'Laser',
    'IR_Black',
    'Hurtado',
    'Homebrew',
    'Hipster Green',
    'Firefly Traditional',
    'Elementary',
    'deep',
    'Dark Pastel',
    'Bright Lights',
    'Adventure',
    'Nancy (terminal.sexy)',
    'Bim (Gogh)',
    'BlueDolphin',
    'Borland',
    'Grass (Gogh)',
    'Greenscreen (light) (terminal.sexy)',
    'Grayscale (dark) (terminal.sexy)',
]


def main2():
    option = choose_one_option(options=schemes_list, header="Choose a theme for Wezterm", fzf=True)
    set_theme(option)


def set_theme(theme: str):
    txt_lines = P("~/.config/wezterm/wezterm.lua").expanduser().read_text().splitlines()
    res_lines = []
    for line in txt_lines:
        if 'config.color_scheme = ' in line:
            res_lines.append(f"config.color_scheme = '{theme}'")
        else: res_lines.append(line)
    P("~/.config/wezterm/wezterm.lua").expanduser().write_text('\n'.join(res_lines))
    time.sleep(0.1)


def main():
    import curses  # not availble on windows: https://docs.python.org/3/howto/curses.html
    # from curses import wrapper
    curses.wrapper(accessory)

def accessory(stdscr: Any):
    import curses
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
                stdscr.addstr(i, 0, option, curses.A_REVERSE)  # Highlighted
            else:
                stdscr.addstr(i, 0, option)

        # Display status line
        status_line = f"Option {current_option+1} of {len(options)}. Use arrow keys to navigate, Enter to select."
        stdscr.addstr(page_size, 0, status_line)

        # Get key press
        key = stdscr.getch()

        # Handle key press
        if key == curses.KEY_UP and current_option > 0:
            current_option -= 1
        elif key == curses.KEY_DOWN and current_option < len(options) - 1:
            current_option += 1
        elif key == ord('\n'):  # Enter key
            break  # Exit the loop
        set_theme(options[current_option])
