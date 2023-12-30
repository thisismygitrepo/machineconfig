
"""cleans projects from litter files."""

from machineconfig.utils.installer import find_move_delete_linux, get_latest_release
from platform import system
from typing import Optional
import crocodile.toolbox as tb

repo_url = 'https://github.com/tbillington/kondo'


def main(version: Optional[str] = None):
    if system() == 'Windows':
        get_latest_release(repo_url=repo_url, exe_name="kondo", download_n_extract=True, file_name='kondo-x86_64-pc-windows-msvc.zip', version=version)
    elif system() == 'Linux':
        downloaded = get_latest_release(repo_url=repo_url, exe_name="kondo", download_n_extract=False, version=version)
        if isinstance(downloaded, tb.P):
            find_move_delete_linux(downloaded=downloaded.joinpath("kondo-x86_64-unknown-linux-gnu.tar.gz").download().ungz_untar(inplace=True), tool_name="kondo")
    else:
        raise NotImplementedError(f"System {system()} not supported")


if __name__ == '__main__':
    main()
