
# a TUI like winscp

from machineconfig.utils.utils import get_latest_release
from platform import system
import crocodile.toolbox as tb
from typing import Optional


repo_url = tb.P(r"https://github.com/veeso/termscp")
__doc__ = """A TUI like winscp"""

def main(version: Optional[str] = None):
    if system() == 'Windows':
        suffix = "x86_64-pc-windows-msvc"
        _exe = get_latest_release(repo_url.as_url_str(), suffix=suffix, download_n_extract=True, delete=False, version=version)
    else:
        suffix = "x86_64-unknown-linux-gnu"
        _release = get_latest_release(repo_url.as_url_str(), download_n_extract=True, delete=True, suffix=suffix, compression="tar.gz", linux=True, version=version)
    return ""


if __name__ == '__main__':
    main()
