
# rg (rust)
# cargo install ripgrep
# used by lvim and spacevim
from machineconfig.utils.utils import get_latest_release

url = 'https://github.com/BurntSushi/ripgrep'


def main(): get_latest_release(url, download_n_extract=True, exe_name='rg')


if __name__ == '__main__':
    main()

