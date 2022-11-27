
from machineconfig.utils.utils import get_latest_release, find_move_delete_linux
from platform import system
import crocodile.toolbox as tb


url = r"https://github.com/gopasspw/gopass"


def main():
    release = get_latest_release(url, file_name="gopass-1.14.11.tar.gz", download_n_extract=True, linux=True)


if __name__ == '__main__':
    main()
