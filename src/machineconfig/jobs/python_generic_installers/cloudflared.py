

""" Cloudflared installer"""

# from crocodile.meta import sys
from machineconfig.utils.utils import get_latest_release, find_move_delete_linux, find_move_delete_windows
from platform import system
from typing import Optional
import crocodile.toolbox as tb


url = "https://github.com/cloudflare/cloudflared"


def main(version: Optional[str] = None) -> None:
    _ = version
    latest = get_latest_release(url, download_n_extract=False)
    if not isinstance(latest, tb.P):
        print(f"Could not find cloudflared release for version {version}")
        return None
    if system() == "Windows":
        downloaded = latest.joinpath("cloudflared-windows-amd64.exe").download().with_name("cloudflared.exe", inplace=True)
        find_move_delete_windows(downloaded=downloaded)
    elif system() == "Linux":
        downloaded = latest.joinpath("cloudflared-linux-amd64").download().with_name("cloudflared", inplace=True)
        find_move_delete_linux(downloaded=downloaded, tool_name="cloudflared")


if __name__ == "__main__":
    main()
