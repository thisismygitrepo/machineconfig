
"""
setup file for each shell can be found in $profile. The settings.json is the config file for Terminal.
https://glitchbone.github.io/vscode-base16-term/#/3024

"""

import crocodile.toolbox as tb
# import crocodile.environment as env
from machineconfig.utils.utils import LIBRARY_ROOT
from machineconfig.utils.installer import get_latest_release
import os


def install_nerd_fonts():
    # Step 1: download the required fonts that has all the glyphs and install them.
    folder = get_latest_release(repo_url="https://github.com/ryanoasis/nerd-fonts", exe_name="NOTHING",)
    if not isinstance(folder, tb.P): raise ValueError(f"Failed to get latest release. Expected a Path object, got {folder}")
    folder = folder.joinpath("CascadiaCode.zip").download().unzip(inplace=True)
    folder.search("*Windows*").apply(lambda p: p.delete(sure=True))
    folder.search("*readme*").apply(lambda p: p.delete(sure=True))
    folder.search("*LICENSE*").apply(lambda p: p.delete(sure=True))
    file = tb.P.tmpfile(suffix=".ps1").write_text(LIBRARY_ROOT.joinpath("setup_windows/wt_and_pwsh/install_fonts.ps1").read_text().replace(r".\fonts-to-be-installed", str(folder)))
    tb.subprocess.run(rf"powershell.exe -executionpolicy Bypass -nologo -noninteractive -File {file.str}", check=True)
    folder.delete(sure=True)


def change_shell_profile():
    # Customize powershell profile such that it loads oh-my-posh and the terminal icons automatically.
    # Add arrow keys history functionality to the terminal.
    shell = "pwsh"
    profile_path = tb.Terminal().run("$profile", shell=shell).op2path()
    assert isinstance(profile_path, tb.P), f"Could not find profile path for {shell}."
    local_app_data = os.getenv("LOCALAPPDATA")
    if not isinstance(local_app_data, str):
        raise ValueError("Could not find LOCALAPPDATA environment variable.")
    theme_path = tb.P(local_app_data).joinpath(r"Programs\oh-my-posh\themes").collapseuser().as_posix().replace("~", "$env:USERPROFILE")  # organization machine with homeshare confuse H: with ~.
    txt = f"""
oh-my-posh --init --shell pwsh --config {theme_path}/jandedobbeleer.omp.json | Invoke-Expression
Import-Module -Name Terminal-Icons

# Shows navigable menu of all options when hitting Tab
Set-PSReadlineKeyHandler -Key Tab -Function MenuComplete
Set-PSReadlineKeyHandler -Key UpArrow -Function HistorySearchBackward
Set-PSReadlineKeyHandler -Key DownArrow -Function HistorySearchForward
Set-PSReadlineOption -PredictionViewStyle History
# see dynamic help with prerelease.
"""
    profile_path.modify_text(txt_search=txt, txt_alt=txt, replace_line=True, notfound_append=True)


def main():
    install_nerd_fonts()
    change_shell_profile()


if __name__ == '__main__':
    pass
