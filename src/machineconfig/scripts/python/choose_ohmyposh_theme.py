
"""Oh my posh theme chooser
"""

import crocodile.toolbox as tb
from machineconfig.utils.utils import display_options
from rich import progress
from typing import Optional


descriptive_themes = ["markbull", "peru", "mojada", "festivetech", "sorin", "agnosterplus", "blueish",
                      "thecyberden", "plague", "kali", "fish", "ys", "slim", "paradox", "aliens", "atomicBit"]


print(f"{descriptive_themes=}")


def main(new_theme: Optional[str] = None):
    """This is a helper for a powershell script.
    run this function to interactively choose a style. Optionally, inpsect the themes of oh my posh and select one:
    """
    import os
    themes_path = tb.P(os.environ["POSH_THEMES_PATH"])
    # current_theme = tb.P(os.environ["POSH_THEME"]).trunk
    with progress.Progress() as prog:
        prog.add_task("Asking pwsh about its profile path ... ", total=None)
        profile = tb.Terminal().run("$profile", shell="pwsh").op2path()

    if not isinstance(profile, tb.P): raise ValueError(f"Could not find profile file. Got {profile}")
    current_theme = tb.P(tb.L(profile.read_text().split(" ")).filter(lambda x: ".omp.json" in x).list[0]).expanduser().absolute().trunk

    if new_theme == "manual":
        tb.P("https://ohmyposh.dev/docs/themes").start()  # replace ~/jan... with full path to theme. use: start $profile
        new_theme = input(f"A chrome tab with styles is opened, choose one and put its name here: [jandedobbeleer] ")
    if new_theme == "show":
        __import__("os").system("Write-Host Get-PoshThemes")
        return ""
    if new_theme is None:
        themes = themes_path.search().apply(lambda x: x.trunk)
        # print(themes)
        themes.list.sort()
        tail = ""
        tmp = display_options(msg=f"Choose a theme number from the list above: ", tail=tail,
                              options=themes.list + ["surprise me"], default="surprise me",
                              prompt=f"Recommended descriptive ones are {descriptive_themes}",
                              #   prompt="Choose A theme: ",
                              fzf=True)
        if isinstance(tmp, str): new_theme = tmp
        else: raise ValueError(f"Got {tmp} from display_options")
        if new_theme == "suprise me": new_theme = themes.sample().list[0]
    print("Current Theme:", current_theme)
    print("New theme: ", new_theme)
    profile.modify_text(txt_search=current_theme, txt_alt=new_theme, replace_line=False)


if __name__ == '__main__':
    pass
