
from machineconfig.utils.utils import choose_one_option, P


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


option = choose_one_option(options=schemes_list, header="Choose a theme for Wezterm", fzf=True)



txt_lines = P("~/.config/wezterm/wezterm.lua").expanduser().read_text().splitlines()
res_lines = []
for line in txt_lines:
    if 'config.color_scheme = ' in line:
        res_lines.append(f"config.color_scheme = '{option}'")
    else: res_lines.append(line)

P("~/.config/wezterm/wezterm.lua").expanduser().write_text('\n'.join(res_lines))
