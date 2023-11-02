
"""qr code file transfer"""

from platform import system
from machineconfig.utils.installer import find_move_delete_windows, find_move_delete_linux, get_latest_release
import crocodile.toolbox as tb
from typing import Optional


repo_url = "https://github.com/claudiodangelis/qrcp"


def main(version: Optional[str] = None):
    # =================================================== python's qr code to create qrcode on terminal from simple text.
    tb.Terminal().run("pip install qrcode", shell="pwsh")

    # =================================================== Go's qrcp to allow file transfer between computer and phone.
    url = get_latest_release(repo_url=repo_url, exe_name="qrcp", download_n_extract=False, version=version)
    if not isinstance(url, tb.P): raise ValueError(f"Expected a pathlib.Path object, got {type(url)}")
    if system() == "Windows":
        downloaded = url.joinpath(f"qrcp_{url[-1].str.replace('v', '')}_Windows_x86_64.tar.gz").download().ungz_untar(inplace=True)
        find_move_delete_windows(downloaded, "qrcp")
    else:
        downloaded = url.joinpath(f"qrcp_{url[-1].str.replace('v', '')}_linux_x86_64.tar.gz").download().ungz_untar(inplace=True)
        find_move_delete_linux(downloaded, "qrcp")


if __name__ == '__main__':
    main()
