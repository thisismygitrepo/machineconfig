
"""An evaluation context for Rust."""

from machineconfig.utils.installer import get_latest_release
from platform import system
from typing import Optional


repo_url = "https://github.com/evcxr/evcxr"


def main(version: Optional[str] = None):
    if system() == 'Windows':
        suffix = "x86_64-pc-windows-msvc"
        _ = get_latest_release(repo_url=repo_url, tool_name="evcxr", exe_name="evcxr", suffix=suffix, download_n_extract=True, delete=True, strip_v=False, compression="zip", version=version)
    else:
        suffix = "x86_64-unknown-linux-gnu"
        _ = get_latest_release(repo_url=repo_url, tool_name="evcxr", exe_name="evcxr", download_n_extract=True, delete=True, suffix=suffix, compression="tar.gz", version=version)
    return ""


if __name__ == '__main__':
    main()
