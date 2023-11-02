
"""
doesn't have --version
"""

from machineconfig.utils.utils import P
from machineconfig.utils.installer import find_move_delete_windows, find_move_delete_linux, get_latest_release
from platform import system
from typing import Optional

__doc__ = f"""Text-based desktop environment inside your terminal*"""
repo_url = "https://github.com/netxs-group/vtm"


def main(version: Optional[str] = None) -> None:
    _ = version
    link = get_latest_release(repo_url=repo_url, exe_name="vtm", download_n_extract=False)
    if not isinstance(link, P):
        print(f"Could not find browsh release for version {version}")
        return None
    if system() == 'Windows':
        downloaded = link.joinpath("vtm_windows_x86_64.zip").download().unzip(inplace=True)
        find_move_delete_windows(downloaded, "vtm", delete=True)
    else:
        downloaded = link.joinpath("vtm_linux_x86_64.tar.gz").download().ungz_untar(inplace=True)
        find_move_delete_linux(downloaded, tool_name="vtm")
    return None


if __name__ == '__main__':
    main()
