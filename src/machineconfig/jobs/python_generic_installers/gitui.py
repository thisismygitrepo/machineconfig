from machineconfig.utils.installer import find_move_delete_windows, find_move_delete_linux, get_latest_release
import crocodile.toolbox as tb
import platform
from typing import Optional


__doc__ = """gitui is a terminal ui for git written in rust."""
repo_url = "https://github.com/extrawurst/gitui"


def main(version: Optional[str] = None) -> None:
    url = get_latest_release(repo_url=repo_url, exe_name="gitui", version=version)
    if not isinstance(url, tb.P):
        print(f"Could not find browsh release for version {version}")
        return None
    if platform.system() == "Linux":
        download = url.joinpath(f"gitui-linux-musl.tar.gz").download().ungz_untar(inplace=True)
        find_move_delete_linux(downloaded=download, tool_name="gitui")
    elif platform.system() == "Windows":
        download = url.joinpath(f"gitui-win.tar.gz").download().ungz_untar(inplace=True)
        find_move_delete_windows(downloaded_file_path=download, exe_name="gitui.exe")
    else:
        raise NotImplementedError(f"Not supported OS for gitui {platform.system()}")


if __name__ == '__main__':
    main()
