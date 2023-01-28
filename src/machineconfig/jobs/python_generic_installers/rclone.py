

from machineconfig.utils.utils import get_latest_release
# import crocodile.toolbox as tb
import platform


url = r"https://github.com/rclone/rclone"


def main(version=None):
    if platform.system() == "Windows":
        get_latest_release(url, suffix="windows-amd64", download_n_extract=True, version=version)
    elif platform.system() == "Linux":
        get_latest_release(url, suffix="linux-amd64", download_n_extract=True, linux=True, compression="zip", version=version)
    else:
        raise NotImplementedError(f"Platform {platform.system()} not supported.")


if __name__ == '__main__':
    main()
