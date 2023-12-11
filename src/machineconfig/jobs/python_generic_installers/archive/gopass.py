from machineconfig.utils.installer import get_latest_release
from platform import system
# import crocodile.toolbox as tb
from typing import Optional


url = r"https://github.com/gopasspw/gopass"
__doc__ = """cli password manager"""


def main(version: Optional[str] = None) -> None:
    if system() == "Windows": get_latest_release(url, exe_name="gopass", suffix="windows-amd64", download_n_extract=True, strip_v=True, tool_name="gopass", delete=False, version=version)
    elif system() == "Linux": get_latest_release(url, exe_name="gopass", suffix="linux-amd64", download_n_extract=True, compression="tar.gz", strip_v=True, tool_name="gopass", delete=False, version=version)
    else: raise NotImplementedError(f"System {system()} is not supported")


if __name__ == '__main__':
    main()
