

""" installer
"""

from machineconfig.utils.utils import get_latest_release, find_move_delete_linux, find_move_delete_windows
import crocodile.toolbox as tb
import platform
from typing import Optional


__doc__ = """cpufetch is a small yet fancy CPU architecture fetching tool, like neofetch but for CPUs."""

def main(version: Optional[str] = None):
    url = get_latest_release("https://github.com/Dr-Noob/cpufetch", version=version)
    if not isinstance(url, tb.P):
        print(f"Could not find browsh release for version {version}")
        return None
    if platform.system() == "Linux":
        download = url.joinpath(f"cpufetch_x86_linux").download().rename("cpufetch")
        find_move_delete_linux(downloaded=download, tool_name="cpufetch")
    elif platform.system() == "Windows":
        download = url.joinpath(f"cpufetch_x86-64_windows.exe").download().rename("cpufetch.exe")
        find_move_delete_windows(downloaded=download, tool_name="cpufetch.exe")
    else:
        raise NotImplementedError(f"Not supported OS for gitui {platform.system()}")


if __name__ == '__main__':
    main()
