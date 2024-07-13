
"""
Installers do not add runtime files to the machine, hence this script.
"""

# from pathlib import Path
from machineconfig.utils.installer import Installer, LINUX_INSTALL_PATH, WINDOWS_INSTALL_PATH
from typing import Optional
import platform


config_dict = {
        "repo_url": "https://github.com/helix-editor/helix",
        "doc": "Helix is a post-modern modal text editor.",
        "filename_template_windows_amd_64": "helix-{}-x86_64-windows.zip",
        "filename_template_linux_amd_64": "helix-{}-x86_64-linux.tar.xz",
        "strip_v": False,
        "exe_name": "hx"
    }


def main(version: Optional[str]):
    inst = Installer.from_dict(d=config_dict, name="hx")
    downloaded, _version_to_be_installed = inst.download(version=version)
    hx_file_search = downloaded.search("hx", folders=False, files=True, r=True)
    assert len(hx_file_search) == 1
    hx_file = hx_file_search.list[0]
    contrib = hx_file.parent / "contrib"
    runtime = contrib.parent / "runtime"
    assert runtime.exists()
    assert contrib.exists()
    if platform.system() == "Linux":
        hx_file.move(folder=LINUX_INSTALL_PATH)
        contrib.move(folder="~/.config/helix")
        runtime.move(folder="~/.config/helix")
    elif platform.system() == "Windows":
        hx_file.move(folder=WINDOWS_INSTALL_PATH)
        contrib.move(folder="~/.config/helix")
        runtime.move(folder="~/.config/helix")


if __name__ == "__main__":
    main(version=None)
