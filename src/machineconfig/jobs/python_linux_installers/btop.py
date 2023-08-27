

from machineconfig.utils.utils import get_latest_release, find_move_delete_linux
import crocodile.toolbox as tb
from typing import Optional

url = r'https://github.com/aristocratos/btop'
fname = 'btop-x86_64-linux-musl.tbz'
__doc__ = """btop is a resource monitor for Linux, FreeBSD and MacOS."""

def main(version: Optional[str] = None):
    release = get_latest_release(url, version=version)
    downloaded = tb.P(release).joinpath(fname).download().unbz(name="btop.tar", inplace=True).untar(inplace=True)
    find_move_delete_linux(downloaded, 'btop', delete=True)


if __name__ == '__main__':
    main()
