

""" Cloudflared installer. Should only be installed at main computer and servers of tunnels."""
# sudo rm /etc/systemd/system/cloudfl*; before uninstall command if you want to uninstall
# you can't ssh and serve cloudflared tunnel on the same machine, make sure not to do that.

# from crocodile.meta import sys
from machineconfig.utils.installer import find_move_delete_windows, find_move_delete_linux, get_latest_release
from platform import system
from typing import Optional
import crocodile.toolbox as tb


repo_url = "https://github.com/cloudflare/cloudflared"


def main(version: Optional[str] = None) -> None:
    _ = version
    latest = get_latest_release(repo_url=repo_url, exe_name="cloudflared", download_n_extract=False)
    if not isinstance(latest, tb.P):
        print(f"Could not find cloudflared release for version {version}")
        return None
    if system() == "Windows":
        downloaded = latest.joinpath("cloudflared-windows-amd64.exe").download().with_name("cloudflared.exe", inplace=True)
        find_move_delete_windows(downloaded_file_path=downloaded)
    elif system() == "Linux":
        downloaded = latest.joinpath("cloudflared-linux-amd64").download().with_name("cloudflared", inplace=True)
        find_move_delete_linux(downloaded=downloaded, tool_name="cloudflared")


if __name__ == "__main__":
    main()
