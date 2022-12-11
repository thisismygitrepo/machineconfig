

import crocodile.toolbox as tb


def main(name=None):
    """This is a helper for a powershell script.
    run this function to interactively choose a style. Optionally, inpsect the themes of oh my posh and select one:
    """
    import os
    themes_path = tb.P(os.environ["POSH_THEMES_PATH"])
    # current_theme = tb.P(os.environ["POSH_THEME"]).trunk
    profile = tb.Terminal().run("$profile", shell="pwsh").as_path
    current_theme = tb.P(tb.L(profile.read_text().split(" ")).filter(lambda x: ".omp.json" in x)[0]).expanduser().absolute().trunk

    if name == "manual":
        tb.P("https://ohmyposh.dev/docs/themes").start()  # replace ~/jan... with full path to theme. use: start $profile
        name = input(f"A chrome tab with styles is opened, choose one and put its name here: [jandedobbeleer] ")
    if name == "show":
        __import__("os").system("Write-Host Get-PoshThemes")
        return ""
    if name is None:
        themes = themes_path.search().apply(lambda x: x.trunk)
        themes.print()
        theme_num = input(f"Choose a theme number from the list above: [suprise me] ")
        if theme_num == "": name = themes.sample()[0]
        else: name = themes[int(theme_num)]
    print("Current Theme:", current_theme)
    print("New theme: ", name)
    profile.modify_text(txt_search=current_theme, txt_alt=name, replace_line=False)


if __name__ == '__main__':
    pass
