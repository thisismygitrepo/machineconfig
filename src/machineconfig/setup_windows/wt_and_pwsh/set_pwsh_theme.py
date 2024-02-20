
"""
setup file for each shell can be found in $profile. The settings.json is the config file for Terminal.
https://glitchbone.github.io/vscode-base16-term/#/3024

"""


# # import crocodile.environment as env
from crocodile.file_management import P
# from crocodile.meta import Terminal
from machineconfig.utils.utils import LIBRARY_ROOT
from machineconfig.utils.installer import Installer
# import os
import subprocess


nerd_fonts = {
    "repo_url": "https://github.com/ryanoasis/nerd-fonts",
    "doc": "Nerd Fonts is a project that patches developer targeted fonts with a high number of glyphs (icons)",
    "filename_template_windows_amd_64": "CascadiaCode.zip",
    "filename_template_linux_amd_64": "CascadiaCode.zip",
    "strip_v": False,
    "exe_name": "nerd_fonts"
}


def install_nerd_fonts():
    # Step 1: download the required fonts that has all the glyphs and install them.
    folder, _version_to_be_installed = Installer.from_dict(d=nerd_fonts, name="nerd_fonts").download(version=None)
    folder.search("*Windows*").apply(lambda p: p.delete(sure=True))
    folder.search("*readme*").apply(lambda p: p.delete(sure=True))
    folder.search("*LICENSE*").apply(lambda p: p.delete(sure=True))
    file = P.tmpfile(suffix=".ps1").write_text(LIBRARY_ROOT.joinpath("setup_windows/wt_and_pwsh/install_fonts.ps1").read_text().replace(r".\fonts-to-be-installed", str(folder)))
    subprocess.run(rf"powershell.exe -executionpolicy Bypass -nologo -noninteractive -File {file.str}", check=True)
    folder.delete(sure=True)


def main():
    install_nerd_fonts()


if __name__ == '__main__':
    pass
