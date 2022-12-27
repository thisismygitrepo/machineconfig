

from machineconfig.utils.utils import get_latest_release
from platform import system


url = "https://github.com/watchexec/watchexec"


def main():
    if system() == 'Windows':
        suffix = "x86_64-pc-windows-msvc"
        _ = get_latest_release(url, suffix=suffix, download_n_extract=True, delete=False, strip_v=True, compression="zip")
    else:
        suffix = "x86_64-unknown-linux-musl"
        _ = get_latest_release(url, download_n_extract=True, delete=True, suffix=suffix, compression="tar.xz", linux=True)
    return ""


if __name__ == '__main__':
    main()
