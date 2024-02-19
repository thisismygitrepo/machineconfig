
"""wezterm installer
"""

from machineconfig.utils.installer import get_installers
from typing import Optional
import platform


def main(version: Optional[str]):
    if platform.system() == "Windows":
        program = "winget install wez.wezterm"
    elif platform.system() == "Linux":
        insts = get_installers(system=platform.system(), dev=False)
        program = ""
        for inst in insts:
            if "wezterm" in inst.name:
                # as per https://wezfurlong.org/wezterm/install/linux.html#installing-on-ubuntu-and-debian-based-systems
                downloaded, version_to_be_installed = inst.download(version=version)
                _= version_to_be_installed

                program = f"""
sudo apt install -y {downloaded}
rm {downloaded}
"""
                break
    else:
        raise NotImplementedError("unsupported platform")
    return program


if __name__ == "__main__":
    # main(version=None)
    pass
