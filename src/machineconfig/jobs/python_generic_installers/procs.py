from machineconfig.utils.installer import get_latest_release
# import crocodile.toolbox as tb
import platform
from typing import Optional


repo_url = "https://github.com/dalance/procs/"
__doc__ = """procs is a modern replacement for ps written in Rust."""

def main(version: Optional[str] = None) -> None:
    if platform.system() == "Windows":
        get_latest_release(repo_url=repo_url, exe_name="procs", suffix="x86_64-windows", download_n_extract=True, version=version)
    elif platform.system() == "Linux":
        get_latest_release(repo_url=repo_url, exe_name="procs", suffix="x86_64-linux", download_n_extract=True, compression="zip", version=version)
    else:
        raise NotImplementedError(f"Platform {platform.system()} not supported.")


if __name__ == '__main__':
    main()
