

from machineconfig.utils.utils import get_latest_release, find_move_delete_windows, find_move_delete_linux
import crocodile.toolbox as tb
import platform


url = "https://github.com/sniptt-official/ots"


def main():
    if platform.system() == "Windows":
        latest = get_latest_release(url, download_n_extract=False)
        downloaded = latest.joinpath(f'ots_{latest[-1].str.replace("v", "")}_windows_amd64.zip').download()
        find_move_delete_windows(downloaded=downloaded.unzip(inplace=True), tool_name="ots",  delete=True)
    elif platform.system() == "Linux":
        latest = get_latest_release(url, suffix="x86_64-linux", download_n_extract=True, linux=True, compression="zip")
        downloaded = latest.joinpath(f'ots_{latest[-1].str.replace("v", "")}_linux_amd64.tar.gz').download()
        find_move_delete_linux(downloaded=downloaded.ungz_untar(inplace=True), tool_name="ots",  delete=True)
    else:
        raise NotImplementedError(f"Platform {platform.system()} not supported.")


if __name__ == '__main__':
    main()
