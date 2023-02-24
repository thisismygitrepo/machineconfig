

from machineconfig.utils.utils import get_latest_release
import platform


url = "https://github.com/pvolok/mprocs"


def main(version=None):
    if platform.system() == "Windows":
        get_latest_release(url, suffix="win64", download_n_extract=True, version=version, strip_v=True)
    elif platform.system() == "Linux":
        get_latest_release(url, suffix="linux64", download_n_extract=True, linux=True, compression="tar.gz", version=version, strip_v=True)
    else:
        raise NotImplementedError(f"Platform {platform.system()} not supported.")


if __name__ == '__main__':
    main()
