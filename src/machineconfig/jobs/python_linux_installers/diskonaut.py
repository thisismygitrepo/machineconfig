
import crocodile.toolbox as tb
from machineconfig.utils.utils import get_latest_release


def main():
    url = r'https://github.com/imsnif/diskonaut'
    url = get_latest_release(url, download_n_extract=True, suffix="unknown-linux-musl", compression="tar.gz", linux=True)


if __name__ == '__main__':
    main()
