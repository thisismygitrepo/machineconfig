
from machineconfig.utils.utils import get_latest_release
import crocodile.toolbox as tb
import platform


url = "https://github.com/dalance/procs/"


def main():
    if platform.system() == "Windows":
        get_latest_release(url, suffix="x86_64-windows", download_n_extract=True)
    elif platform.system() == "Linux":
        get_latest_release(url, suffix="x86_64-linux", download_n_extract=True, linux=True, compression="zip")
    else:
        raise NotImplementedError(f"Platform {platform.system()} not supported.")


if __name__ == '__main__':
    main()
