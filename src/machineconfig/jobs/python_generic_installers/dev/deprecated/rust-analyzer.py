
"""
VSCode and Pycharm have their own extensions from marketplace, but for other editors, we need to install this LSP manually.
"""

from machineconfig.utils.installer import get_latest_release
from platform import system
import crocodile.toolbox as tb
from typing import Optional


repo_url = tb.P(r"https://github.com/rust-lang/rust-analyzer")
__doc__ = f"""Rust Language Server (LSP)"""


def main(version: Optional[str] = None):
    url = get_latest_release(repo_url=repo_url.as_url_str(), exe_name="rust-analyzer", download_n_extract=False, version=version)
    if not isinstance(url, tb.P): raise ValueError(f"Failed to get latest release. Expected a Path object, got {url}")
    if system() == "Windows":
        url.joinpath(f"rust-analyzer-x86_64-pc-windows-msvc.gz").download().ungz(inplace=True).with_name("rust-analyzer.exe", inplace=True).move(folder="~/.cargo/bin", overwrite=True)
    else:
        url.joinpath(f"rust-analyzer-x86_64-unknown-linux-gnu.gz").download().ungz(inplace=True).with_name("rust-analyzer", inplace=True).move(folder="~/.cargo/bin", overwrite=True)
        # downloaded.move(folder=r"/usr/local/bin", overwrite=False)


if __name__ == '__main__':
    pass
