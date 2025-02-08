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

    # Check for installed fonts and remove them from folder
    check_font_script = '''
        param($fontName)
        $installedFonts = (New-Object System.Drawing.Text.InstalledFontCollection).Families
        return $installedFonts | Where-Object { $_.Name -eq $fontName } | Select-Object -First 1
    '''
    # Process each font file in the folder
    for font_file in folder.search("*.ttf"):
        # Extract font name from filename (remove extension and any variants like 'Bold', 'Italic')
        font_name = font_file.stem.split('-')[0]
        # Check if font is installed
        result = subprocess.run([
            'powershell.exe',
            '-ExecutionPolicy', 'Bypass',
            '-Command', check_font_script,
            '-fontName', font_name
        ], capture_output=True, text=True, check=True)
        # If font is installed, delete the file
        if result.stdout.strip():
            font_file.delete(sure=True)

    # Install remaining fonts
    if list(folder.search("*.ttf")):
        file = P.tmpfile(suffix=".ps1").write_text(LIBRARY_ROOT.joinpath("setup_windows/wt_and_pwsh/install_fonts.ps1").read_text().replace(r".\fonts-to-be-installed", str(folder)))
        subprocess.run(rf"powershell.exe -executionpolicy Bypass -nologo -noninteractive -File {file.to_str()}", check=True)

    folder.delete(sure=True)


def main():
    install_nerd_fonts()


if __name__ == '__main__':
    pass
