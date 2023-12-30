
"""i
"""

from machineconfig.utils.installer import get_latest_release
from platform import system
from typing import Optional


repo_url = "https://github.com/watchexec/watchexec"
__doc__ = """Executes commands in response to file modifications."""


def main(version: Optional[str] = None) -> None:
    if system() == 'Windows':
        suffix = "x86_64-pc-windows-msvc"
        _ = get_latest_release(repo_url=repo_url, exe_name="watchexec", suffix=suffix, download_n_extract=True, delete=False, strip_v=True, compression="zip", version=version)
    else:
        suffix = "x86_64-unknown-linux-musl"
        # suffix = "watchexec-1.23.0-x86_64-unknown-linux-gnu.tar.xz"
        _ = get_latest_release(repo_url=repo_url, exe_name="watchexec", download_n_extract=True, delete=True, suffix=suffix, compression="tar.xz", version=version, strip_v=True)
    return None


if __name__ == '__main__':
    main()
