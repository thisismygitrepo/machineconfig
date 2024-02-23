
"""wezterm installer
"""

from machineconfig.utils.installer import Installer
from typing import Optional
import platform

wezterm = {
        "repo_url": "CUSTOM",
        "doc": "cross-platform terminal emulator",
        "filename_template_windows_amd_64": "WezTerm-windows-{}.zip",
        "filename_template_linux_amd_64": "wezterm-{}.Ubuntu22.04.deb",
        "strip_v": False,
        "exe_name": "wezterm"
    }


def main(version: Optional[str]):
    if platform.system() == "Windows":
        program = "winget install wez.wezterm"
    elif platform.system() == "Linux":
        inst = Installer.from_dict(d=wezterm, name="wezterm")
        program = ""
        # as per https://wezfurlong.org/wezterm/install/linux.html#installing-on-ubuntu-and-debian-based-systems
        downloaded, version_to_be_installed = inst.download(version=version)
        _= version_to_be_installed

        program = f"""
sudo apt install -y {downloaded}
rm {downloaded}
"""
    else:
        raise NotImplementedError("unsupported platform")
    return program


if __name__ == "__main__":
    # main(version=None)
    pass
