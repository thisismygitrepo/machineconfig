
"""cleans projects from litter files."""

from machineconfig.utils.utils import get_latest_release, find_move_delete_linux
from platform import system
from typing import Optional
import crocodile.toolbox as tb

url = 'https://github.com/tbillington/kondo'


def main(version: Optional[str] = None):
    if system() == 'Windows':
        get_latest_release(repo_url=url, exe_name="kondo", download_n_extract=True, file_name='kondo-x86_64-pc-windows-msvc.zip', version=version)
    elif system() == 'Linux':
        downloaded = get_latest_release(repo_url=url, exe_name="kondo", download_n_extract=False, version=version)
        if isinstance(downloaded, tb.P):
            find_move_delete_linux(downloaded=downloaded.joinpath("kondo-x86_64-unknown-linux-gnu.tar.gz").download().ungz_untar(inplace=True), tool_name="kondo")
    else:
        raise NotImplementedError(f"System {system()} not supported")


if __name__ == '__main__':
    main()
