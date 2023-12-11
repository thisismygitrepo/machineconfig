from machineconfig.utils.installer import get_latest_release
import platform
from typing import Optional


repo_url = "https://github.com/pvolok/mprocs"
__doc__ = """Windows/Linux poorman's zellij"""


def main(version: Optional[str] = None) -> None:
    if platform.system() == "Windows":
        get_latest_release(repo_url=repo_url, exe_name="mprocs", suffix="win64", download_n_extract=True, version=version, strip_v=True)
    elif platform.system() == "Linux":
        get_latest_release(repo_url=repo_url, exe_name="mprocs", suffix="linux64", download_n_extract=True, compression="tar.gz", version=version, strip_v=True)
    else:
        raise NotImplementedError(f"Platform {platform.system()} not supported.")


if __name__ == '__main__':
    main()
