

""" installer
"""

from machineconfig.utils.utils import get_latest_release, find_move_delete_linux, find_move_delete_windows
# import crocodile.toolbox as tb
import platform
from typing import Optional


__doc__ = """gitui is a terminal ui for git written in rust."""

def main(version: Optional[str] = None) -> None:
    url = get_latest_release("https://github.com/extrawurst/gitui", version=version)
    if platform.system() == "Linux":
        download = url.joinpath(f"gitui-linux-musl.tar.gz").download().ungz_untar(inplace=True)
        find_move_delete_linux(downloaded=download, tool_name="gitui")
    elif platform.system() == "Windows":
        download = url.joinpath(f"gitui-win.tar.gz").download().ungz_untar(inplace=True)
        find_move_delete_windows(downloaded=download, tool_name="gitui.exe")
    else:
        raise Exception(f"Not supported OS for gitui {platform.system()}")


if __name__ == '__main__':
    main()
