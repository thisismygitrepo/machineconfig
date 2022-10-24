
# bat (rust-based, modern cat)
#  cargo install bat
# colored bat
from machineconfig.utils.utils import get_latest_release


url = 'https://github.com/sharkdp/bat'


def main(): get_latest_release(url, download_n_extract=True)


if __name__ == '__main__':
    main()
