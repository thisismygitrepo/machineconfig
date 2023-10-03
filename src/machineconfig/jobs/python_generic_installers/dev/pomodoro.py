
""" Pomodoro timer for the command-line, written in Go.
"""

from machineconfig.utils.utils import get_latest_release
import platform
from typing import Optional


url = "https://github.com/open-pomodoro/openpomodoro-cli"
__doc__ = """Pomodoro timer for the command-line"""


def main(version: Optional[str] = None) -> None:
    if platform.system() == "Windows":
        get_latest_release(url, suffix="windows_amd64", download_n_extract=True, version=version, strip_v=True, compression="tar.gz", sep="_", exe_name="pomodoro")
    elif platform.system() == "Linux":
        get_latest_release(url, suffix="linux_amd64", download_n_extract=True, linux=True, compression="tar.gz", version=version, strip_v=True, sep="_", exe_name="pomodoro")
    else:
        raise NotImplementedError(f"Platform {platform.system()} not supported.")


if __name__ == '__main__':
    main()
