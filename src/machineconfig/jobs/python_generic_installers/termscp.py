
# a TUI like winscp

from machineconfig.utils.utils import get_latest_release
from platform import system
import crocodile.toolbox as tb


repo_url = tb.P(r"https://github.com/veeso/termscp")


def main():
    if system() == 'Windows':
        suffix = "x86_64-pc-windows-msvc"
        exe = get_latest_release(repo_url.as_url_str(), suffix=suffix, download_n_extract=True, delete=False)
    else:
        suffix = "x86_64-unknown-linux-gnu"
        release = get_latest_release(repo_url.as_url_str(), download_n_extract=True, delete=True, suffix=suffix, compression="tar.gz", linux=True)
    return ""


if __name__ == '__main__':
    main()
