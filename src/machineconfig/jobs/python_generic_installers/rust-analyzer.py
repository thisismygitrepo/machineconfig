
from machineconfig.utils.utils import get_latest_release
from platform import system
import crocodile.toolbox as tb

"""
VSCode and Pycharm have their own extensions from marketplace, but for other editors, we need to install this LSP manually.
"""

repo_url = tb.P(r"https://github.com/rust-lang/rust-analyzer")


def main():
    url = get_latest_release(repo_url.as_url_str(), download_n_extract=False)
    if system() == "Windows":
        url.joinpath(f"rust-analyzer-x86_64-pc-windows-msvc.gz").download().ungz(inplace=True).rename("rust-analyzer.exe").move(folder="~/.cargo/bin", overwrite=True)
    else:
        url.joinpath(f"rust-analyzer-x86_64-unknown-linux-gnu.gz").download().ungz(inplace=True).rename("rust-analyzer").move(folder="~/.cargo/bin", overwrite=True)
        # downloaded.move(folder=r"/usr/local/bin", overwrite=False)


if __name__ == '__main__':
    pass

