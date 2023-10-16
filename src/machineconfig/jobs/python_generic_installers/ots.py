from machineconfig.utils.installer import find_move_delete_windows, find_move_delete_linux, get_latest_release
import crocodile.toolbox as tb
import platform
from typing import Optional


# url = "https://github.com/sniptt-official/ots"
url = "https://github.com/Luzifer/ots"
__doc__ = """A command line tool for generating and verifying one-time secrets."""


def main(version: Optional[str] = None) -> None:
    if platform.system() == "Windows":
        latest = get_latest_release(repo_url=url, exe_name="ots", file_name="ots_windows_amd64.zip", download_n_extract=False, version=version)
        if not isinstance(latest, tb.P):
            print(f"Could not find ots release for version {version}")
            return None
        downloaded = latest.joinpath("ots_windows_amd64.zip").download()
        find_move_delete_windows(downloaded=downloaded.unzip(inplace=True), tool_name="ots", delete=True, rename_to="ots.exe")
    elif platform.system() == "Linux":
        latest = get_latest_release(repo_url=url, exe_name="ots", file_name="ots_linux_amd64.tgz", download_n_extract=False, linux=True, version=version)
        if not isinstance(latest, tb.P):
            print(f"Could not find ots release for version {version}")
            return None
        downloaded = latest.joinpath("ots_linux_amd64.tar.gz").download()
        find_move_delete_linux(downloaded=downloaded.ungz_untar(inplace=True), tool_name="ots", delete=True, rename_to="ots")
    else:
        raise NotImplementedError(f"Platform {platform.system()} not supported.")


if __name__ == '__main__':
    main()
