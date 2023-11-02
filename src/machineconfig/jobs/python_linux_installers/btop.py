from machineconfig.utils.installer import find_move_delete_linux, get_latest_release
import crocodile.toolbox as tb
from typing import Optional

repo_url = r'https://github.com/aristocratos/btop'
fname = 'btop-x86_64-linux-musl.tbz'
__doc__ = """btop is a resource monitor for Linux, FreeBSD and MacOS."""


def main(version: Optional[str] = None):
    release = get_latest_release(repo_url=repo_url, exe_name="btop", version=version)
    if not isinstance(release, tb.P): raise ValueError(f"Failed to get latest release. Expected a Path object, got {release}")
    downloaded = tb.P(release).joinpath(fname).download().unbz(name="btop.tar", inplace=True).untar(inplace=True)
    find_move_delete_linux(downloaded, 'btop', delete=True)


if __name__ == '__main__':
    main()
