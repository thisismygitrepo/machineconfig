
from machineconfig.utils.installer import get_latest_release
# import crocodile.toolbox as tb
import platform
from typing import Optional


__doc__ = """select from options, written in golang"""
repo_url = "https://github.com/charmbracelet/gum"


def main(version: Optional[str] = None):
    if platform.system() == "Windows":
        _url = get_latest_release(repo_url=repo_url, exe_name="gum", version=version, strip_v=True, suffix="Windows_x86_64", compression="zip", download_n_extract=True, sep="_")
    elif platform.system() == "Linux":
        _url = get_latest_release(repo_url=repo_url, exe_name="gum", version=version, strip_v=True, suffix="Linux_arm64", compression="tar.gz", download_n_extract=True, sep="_")
    else:
        raise NotImplementedError(f"Not supported OS for {platform.system()}")


if __name__ == '__main__':
    main()
