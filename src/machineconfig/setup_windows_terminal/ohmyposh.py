
import crocodile.toolbox as tb
import crocodile.environment as env
from machineconfig.utils.utils import get_latest_release

"""
setup file for each shell can be found in $profile. The settings.json is the config file for Terminal.
"""


def install():
    # Step 1: download the required fonts that has all the glyphs and install them.
    folder = get_latest_release("https://github.com/ryanoasis/nerd-fonts").joinpath("CascadiaCode.zip").download().unzip(inplace=True)
    folder.search("*Windows*").delete(sure=True)
    folder.search("*readme*").delete(sure=True)
    folder.search("*LICENSE*").delete(sure=True)
    file = tb.P.tmpfile(suffix=".ps1").write_text(tb.P(__file__).with_name("install_fonts.ps1").read_text().replace(r".\fonts-to-be-installed", str(folder)))
    tb.subprocess.run(rf"powershell.exe -executionpolicy Bypass -nologo -noninteractive -File {file.str}")

    # Step 2: Install icons
    tb.Terminal().run("Install-Module -Name Terminal-Icons -Repository PSGallery", shell="powershell")

    # Step 3: install oh-my-posh
    tb.Terminal().run('winget install --name "Oh My Posh" --Id "JanDeDobbeleer.OhMyPosh" --source winget', shell="powershell").print()

    # Step 4: change the profile of the terminal such that nerd font is chosen for your shell
    shell = {"powershell": "pwsh.exe", "Windows Powershell": "powershell.exe"}["powershell"].split(".exe")[0]
    from machineconfig.setup_windows_terminal.set_settings import TerminalSettings
    if shell == "pwsh":
        ts = TerminalSettings()
        ts.customize_powershell(nerd_font=True)
        ts.save_terminal_settings()
    else: raise NotImplementedError


def change_shell_profile():
    # Step 5: customize powershell profile such that it loads oh-my-posh and the terminal icons automatically.
    shell = {"powershell": "pwsh.exe", "Windows Powershell": "powershell.exe"}["powershell"].split(".exe")[0]
    profile_path = tb.Terminal().run("$profile", shell=shell).as_path
    theme_path = env.LocalAppData.joinpath(r"Programs\oh-my-posh\themes").collapseuser().as_posix().replace("~", "$env:USERPROFILE")  # organization machiens with homeshare confuse H: with ~.
    # makes the profile work on any machine.
    txt = f"oh-my-posh --init --shell pwsh --config {theme_path}\\jandedobbeleer.omp.json | Invoke-Expression"
    profile_path.modify_text(txt="oh-my-posh", alt=txt, newline=True, notfound_append=True)
    profile_path.modify_text(txt="Import-Module -Name Terminal-Icons", alt="Import-Module -Name Terminal-Icons", newline=True, notfound_append=True)

    # Step 6: Add arrow keys history functionality to the terminal.
    txt = """
# Shows navigable menu of all options when hitting Tab
Set-PSReadlineKeyHandler -Key Tab -Function MenuComplete
Set-PSReadlineKeyHandler -Key UpArrow -Function HistorySearchBackward
Set-PSReadlineKeyHandler -Key DownArrow -Function HistorySearchForward
Set-PSReadlineOption -PredictionViewStyle History
# see dynamic help with prerelease.
"""
    profile_path.modify_text(txt=txt, alt=txt, newline=True, notfound_append=True)


def choose(name=None):
    """run this function to interactively choose a style. Optionally, inpsect the themes of oh my posh and select one:
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
    profile.modify_text(txt=current_theme, alt=name, newline=False)


if __name__ == '__main__':
    pass
