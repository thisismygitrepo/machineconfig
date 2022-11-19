
from machineconfig.utils.utils import get_latest_release, find_move_delete_linux

url = 'https://github.com/tbillington/kondo'


def main():
    downloaded = get_latest_release(url, download_n_extract=False).joinpath("kondo-x86_64-unknown-linux-gnu.tar.gz").download().ungz_untar(inplace=True)
    find_move_delete_linux(downloaded=downloaded, tool_name="kondo")


if __name__ == '__main__':
    main()
