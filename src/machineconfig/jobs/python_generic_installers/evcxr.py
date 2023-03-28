

from machineconfig.utils.utils import get_latest_release
from platform import system


url = "https://github.com/evcxr/evcxr"
__doc__ = """An evaluation context for Rust."""


def main(version=None):
    if system() == 'Windows':
        suffix = "x86_64-pc-windows-msvc"
        _ = get_latest_release(url, tool_name="evcxr", suffix=suffix, download_n_extract=True, delete=True, strip_v=False, compression="zip", version=version)
    else:
        suffix = "x86_64-unknown-linux-gnu"
        _ = get_latest_release(url, tool_name="evcxr", download_n_extract=True, delete=True, suffix=suffix, compression="tar.gz", linux=True, version=version)
    return ""


if __name__ == '__main__':
    main()
