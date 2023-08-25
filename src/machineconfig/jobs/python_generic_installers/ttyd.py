

""" installer
"""

from machineconfig.utils.utils import get_latest_release, find_move_delete_linux, find_move_delete_windows
import platform
from typing import Optional
from crocodile.toolbox import P


url = "https://github.com/tsl0922/ttyd"
__doc__ = """ttyd shares your terminal on the web."""


def main(version: Optional[str] = None) -> None:
    if platform.system() == "Windows":
        release = get_latest_release(url, version=version, download_n_extract=False, linux=False)
        if not isinstance(release, P):
            print(f"Could not find browsh release for version {version}")
            return None
        find_move_delete_windows(downloaded=release.joinpath("ttyd.win32.exe").download().with_name("ttyd.exe", inplace=True), tool_name="ttyd.exe")
    elif platform.system() == "Linux":
        release = get_latest_release(url, version=version, download_n_extract=False, linux=True)
        if not isinstance(release, P):
            print(f"Could not find browsh release for version {version}")
            return None
        find_move_delete_linux(release.joinpath("ttyd.x86_64").download().with_name("ttyd", inplace=True), tool_name="ttyd")
    return None


if __name__ == '__main__':
    main()

