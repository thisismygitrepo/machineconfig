

from machineconfig.utils.utils import get_latest_release
from platform import system


url = "https://github.com/Byron/dua-cli"


def main():
    if system() == 'Windows':
        suffix = "x86_64-pc-windows-msvc"
        _ = get_latest_release(url, tool_name="dua", suffix=suffix, download_n_extract=True, delete=False, strip_v=False, compression="zip")
    else:
        suffix = "x86_64-unknown-linux-musl"
        _ = get_latest_release(url, tool_name="dua", download_n_extract=True, delete=True, suffix=suffix, compression="tar.gz", linux=True)
    return ""


if __name__ == '__main__':
    main()
