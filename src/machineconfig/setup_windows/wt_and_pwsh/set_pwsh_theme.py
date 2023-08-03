
import crocodile.toolbox as tb
import crocodile.environment as env
from machineconfig.utils.utils import get_latest_release, LIBRARY_ROOT

"""
setup file for each shell can be found in $profile. The settings.json is the config file for Terminal.
"""


def install_nerd_fonts():
    # Step 1: download the required fonts that has all the glyphs and install them.
    folder = get_latest_release("https://github.com/ryanoasis/nerd-fonts").joinpath("CascadiaCode.zip").download().unzip(inplace=True)
    folder.search("*Windows*").delete(sure=True)
    folder.search("*readme*").delete(sure=True)
    folder.search("*LICENSE*").delete(sure=True)
    file = tb.P.tmpfile(suffix=".ps1").write_text(LIBRARY_ROOT.joinpath("setup_windows/wt_and_pwsh/install_fonts.ps1").read_text().replace(r".\fonts-to-be-installed", str(folder)))
    tb.subprocess.run(rf"powershell.exe -executionpolicy Bypass -nologo -noninteractive -File {file.str}")


def change_shell_profile():
    # Customize powershell profile such that it loads oh-my-posh and the terminal icons automatically.
    # Add arrow keys history functionality to the terminal.

    shell = {"powershell": "pwsh.exe", "Windows Powershell": "powershell.exe"}["powershell"].split(".exe")[0]
    profile_path = tb.Terminal().run("$profile", shell=shell).op2path()
    theme_path = env.LocalAppData.joinpath(r"Programs\oh-my-posh\themes").collapseuser().as_posix().replace("~", "$env:USERPROFILE")  # organization machine with homeshare confuse H: with ~.
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
