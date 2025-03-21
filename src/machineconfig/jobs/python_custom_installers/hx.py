
"""
Installers do not add runtime files to the machine, hence this script.
"""

from crocodile.file_management import P
from machineconfig.utils.installer import Installer, WINDOWS_INSTALL_PATH, LINUX_INSTALL_PATH
from typing import Optional
import platform


config_dict = {
        "repo_url": "CUSTOM",
        "doc": "Helix is a post-modern modal text editor.",
        "filename_template_windows_amd_64": "helix-{}-x86_64-windows.zip",
        "filename_template_linux_amd_64": "helix-{}-x86_64-linux.tar.xz",
        "strip_v": False,
        "exe_name": "hx"
    }


def main(version: Optional[str]):
    config_dict_copy = config_dict.copy()
    config_dict_copy["repo_url"] = "https://github.com/helix-editor/helix"
    inst = Installer.from_dict(d=config_dict_copy, name="hx")
    downloaded, _version_to_be_installed = inst.download(version=version)
    if platform.system() == "Windows":
        hx_file_search = downloaded.search("hx.exe", folders=False, files=True, r=True)
    else:
        hx_file_search = downloaded.search("hx", folders=False, files=True, r=True)        
    assert len(hx_file_search) == 1
    hx_file = hx_file_search.list[0]
    contrib = hx_file.parent / "contrib"
    runtime = contrib.parent / "runtime"
    assert runtime.exists()
    assert contrib.exists()
    P.home().joinpath(".config/helix/runtime").delete(sure=True)
    P.home().joinpath(".config/helix/contrib").delete(sure=True)
    if platform.system() == "Linux":
        hx_file.move(folder=LINUX_INSTALL_PATH, overwrite=True)  # to be added later
        contrib.move(folder="~/.config/helix", overwrite=True)
        runtime.move(folder="~/.config/helix", overwrite=True)
    elif platform.system() == "Windows":
        hx_file.move(folder=WINDOWS_INSTALL_PATH, overwrite=True)
        contrib.move(folder="~/.config/helix", overwrite=True)
        runtime.move(folder="~/.config/helix", overwrite=True)
    else:
        print("Unsupported OS")
    downloaded.delete(sure=True)

    # if platform.system() == "Linux":
    #     inst.install(version=version)  # because we can't normally move hx (without privliage) # hx_file.move(folder=LINUX_INSTALL_PATH)
    return ""


if __name__ == "__main__":
    main(version=None)
