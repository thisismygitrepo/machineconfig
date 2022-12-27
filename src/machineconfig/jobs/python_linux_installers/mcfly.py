
from machineconfig.utils.utils import get_latest_release, find_move_delete_linux

url = "https://github.com/cantino/mcfly"


def main():
    get_latest_release(url, suffix="x86_64-unknown-linux-musl", download_n_extract=True, linux=True, compression="tar.gz")


if __name__ == '__main__':
    main()
