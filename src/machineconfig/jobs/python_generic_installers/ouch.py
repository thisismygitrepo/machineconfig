from machineconfig.utils.installer import find_move_delete_windows, find_move_delete_linux, get_latest_release
import crocodile.toolbox as tb
import platform
from typing import Optional


repo_url = "https://github.com/ouch-org/ouch"
__doc__ = """A cli for extracting and creating archives in unified way."""


def main(version: Optional[str] = None) -> None:
    dl = get_latest_release(repo_url=repo_url, exe_name="ouch", download_n_extract=False, version=version)
    if not isinstance(dl, tb.P):
        print(f"Could not find browsh release for version {version}")
        return None
    if platform.system() == "Windows":
        res = dl.joinpath(f"ouch-x86_64-pc-windows-msvc.zip").download().unzip(inplace=True)
        find_move_delete_windows(downloaded_file_path=res, exe_name="ouch", delete=True)
    elif platform.system() == "Linux":
        res = dl.joinpath("ouch-x86_64-unknown-linux-gnu.tar.gz").download().ungz_untar(inplace=True)
        find_move_delete_linux(downloaded=res, tool_name="ouch", delete=True)
    else:
        raise NotImplementedError(f"Platform {platform.system()} not supported.")


if __name__ == '__main__':
    main()
