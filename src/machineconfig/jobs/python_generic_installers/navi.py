
from machineconfig.utils.utils import get_latest_release
import platform


url = "https://github.com/denisidoro/navi"
__doc__ = """Interactive cheatsheet tool for the command-line"""


def main(version=None):
    if platform.system() == "Windows":
        get_latest_release(url, suffix="x86_64-pc-windows-gnu", download_n_extract=True, version=version)
    elif platform.system() == "Linux":
        get_latest_release(url, suffix="x86_64-unknown-linux-musl", download_n_extract=True, linux=True, compression="tar.gz", version=version)
    else:
        raise NotImplementedError(f"Platform {platform.system()} not supported.")


if __name__ == '__main__':
    main()
