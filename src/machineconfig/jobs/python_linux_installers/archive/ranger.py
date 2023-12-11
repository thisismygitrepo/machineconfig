
"""
It has a funny installer that is a library of python scripts, not exe.
"""

from machineconfig.utils.installer import find_move_delete_linux, get_latest_release
import crocodile.toolbox as tb
from typing import Optional


def main(version: Optional[str] = None):
    _ = get_latest_release(repo_url=r"https://github.com/ranger/ranger", exe_name="ranger", download_n_extract=False, version=version)
    find_move_delete_linux(downloaded=tb.P("https://ranger.github.io/ranger-stable.tar.gz").download().ungz_untar(), tool_name="ranger")

    return ""


if __name__ == '__main__':
    main()
