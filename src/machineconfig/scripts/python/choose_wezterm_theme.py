
from machineconfig.utils.utils import choose_one_option, P
from typing import Any


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
    'Nancy (terminal.sexy)'
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


def main():
    import curses
    curses.wrapper(accessory)


def accessory(stdscr: Any):
    import curses
    options = schemes_list
    current_option = 0

    while True:
        stdscr.clear()

        # Display options
        for i, option in enumerate(options):
            if i == current_option:
                stdscr.addstr(i, 0, option, curses.A_REVERSE)  # Highlighted
            else:
                stdscr.addstr(i, 0, option)

        # Get key press
        key = stdscr.getch()

        # Handle key press
        if key == curses.KEY_UP and current_option > 0:
            current_option -= 1
        elif key == curses.KEY_DOWN and current_option < len(options) - 1:
            current_option += 1
        elif key == ord('\n'):  # Enter key
            break  # Exit the loop

        # Call the callback function
        set_theme(options[current_option])
