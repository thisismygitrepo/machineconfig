
"""wezterm installer
"""

from machineconfig.utils.installer import Installer
from typing import Optional
import platform


config = {
    "repo_url": "https://github.com/wez/wezterm/",
    "doc": "cross-platform terminal emulator",
    "filename_template_windows_amd_64": "WezTerm-windows-{}.zip",
    "filename_template_linux_amd_64": "wezterm-{}.Ubuntu22.04.deb",
    "strip_v": False,
    "exe_name": "wezterm"
}


def main(version: Optional[str]):
    self = Installer.from_dict(config)
    downloaded, version_to_be_installed = self.download(version=version)
    _= version_to_be_installed

    if platform.system() == "Windows":
        program = "winget install wez.wezterm"
    elif platform.system() == "Linux":
        # as per https://wezfurlong.org/wezterm/install/linux.html#installing-on-ubuntu-and-debian-based-systems
        program = f"""
sudo apt install -y {downloaded}
rm {downloaded}
"""
    else:
        raise NotImplementedError("unsupported platform")
    from crocodile.meta import Terminal
    Terminal().run(program, shell="powershell")
    return program


if __name__ == "__main__":
    main(version=None)
