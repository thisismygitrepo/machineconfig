

""" installer
"""

from machineconfig.utils.utils import get_latest_release, find_move_delete_windows, find_move_delete_linux
import crocodile.toolbox as tb
import platform
from typing import Optional


url = "https://github.com/ouch-org/ouch"
__doc__ = """A cli for extracting and creating archives in unified way."""


def main(version: Optional[str] = None) -> None:
    dl = get_latest_release(url, download_n_extract=False, version=version)
    if platform.system() == "Windows":
        res = dl.joinpath(f"ouch-x86_64-pc-windows-msvc.zip").download().unzip(inplace=True)
        find_move_delete_windows(downloaded=res, tool_name="ouch", delete=True)
    elif platform.system() == "Linux":
        res = dl.joinpath("ouch-x86_64-unknown-linux-gnu.tar.gz").download().ungz_untar(inplace=True)
        find_move_delete_linux(downloaded=res, tool_name="ouch",  delete=True)
    else:
        raise NotImplementedError(f"Platform {platform.system()} not supported.")


if __name__ == '__main__':
    main()
