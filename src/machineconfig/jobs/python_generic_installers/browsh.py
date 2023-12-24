from machineconfig.utils.installer import find_move_delete_windows, find_move_delete_linux, get_latest_release
import crocodile.toolbox as tb
import platform
from typing import Optional


__doc__ = """cpufetch is a small yet fancy CPU architecture fetching tool, like neofetch but for CPUs."""
repo_url = "https://github.com/browsh-org/browsh"


def main(version: Optional[str] = None) -> None:
    url = get_latest_release(repo_url=repo_url, exe_name="browsh", version=version)
    if not isinstance(url, tb.P):
        print(f"Could not find browsh release for version {version}")
        return None
    if platform.system() == "Linux":
        download = url.joinpath(f"browsh_{str(url[-1]).replace('v', '')}_linux_amd64").download().with_name("browsh", inplace=True, overwrite=True)
        find_move_delete_linux(downloaded=download, tool_name="cpufetch")
    elif platform.system() == "Windows":
        url = url.joinpath(f"browsh_{str(url[-1]).replace('v', '')}_windows_amd64.exe")
        print(f"Downloading {url}")
        downloaded = url.download().with_name("browsh.exe", overwrite=True, inplace=True)
        find_move_delete_windows(downloaded_file_path=downloaded, exe_name="browsh.exe")
    else:
        raise NotImplementedError(f"Not supported OS for gitui {platform.system()}")


if __name__ == '__main__':
    main()
