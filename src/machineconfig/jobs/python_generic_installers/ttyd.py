

from machineconfig.utils.utils import get_latest_release, find_move_delete_linux, find_move_delete_windows
import platform


url = "https://github.com/tsl0922/ttyd"
__doc__ = """ttyd shares your terminal on the web."""


def main(version=None):
    if platform.system() == "Windows":
        release = get_latest_release(url, version=version, download_n_extract=False, linux=False)
        find_move_delete_windows(downloaded=release.joinpath("ttyd.win32.exe").download().with_name("ttyd.exe", inplace=True), tool_name="ttyd.exe")
    elif platform.system() == "Linux":
        release = get_latest_release(url, version=version, download_n_extract=False, linux=True)
        find_move_delete_linux(release.joinpath("ttyd.x86_64").download().with_name("ttyd", inplace=True), tool_name="ttyd")
    return None


if __name__ == '__main__':
    main()
