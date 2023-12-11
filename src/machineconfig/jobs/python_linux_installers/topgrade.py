from machineconfig.utils.installer import get_latest_release
import crocodile.toolbox as tb
from typing import Optional


__doc__ = """Keeping your system up to date usually involves invoking multiple package managers"""
repo_url = tb.P(r"https://github.com/topgrade-rs/topgrade")


def main(version: Optional[str] = None):
    _ = get_latest_release(repo_url=repo_url.as_url_str(), exe_name="topgrade", suffix='x86_64-unknown-linux-gnu', compression='tar.gz', strip_v=False, download_n_extract=True, version=version)


if __name__ == '__main__':
    main()
