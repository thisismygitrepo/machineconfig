
"""BTM
"""
from machineconfig.utils.installer import find_move_delete_linux, get_latest_release
import crocodile.toolbox as tb
from typing import Optional


repo_url = r'https://github.com/ClementTsang/bottom'
fname = 'bottom_x86_64-unknown-linux-gnu.tar.gz'
__doc__ = """bottom is a cross-platform graphical process/system monitor with a customizable interface and a multitude of features."""


def main(version: Optional[str] = None):
    release = get_latest_release(repo_url=repo_url, exe_name="btm", version=version)
    assert isinstance(release, tb.P)
    downloaded = tb.P(release).joinpath(fname).download().ungz_untar(inplace=True)
    find_move_delete_linux(downloaded, 'btm', delete=True)


if __name__ == '__main__':
    main()
