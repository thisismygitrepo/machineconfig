
from machineconfig.utils.utils import get_latest_release

# fd (rust)
# cargo install fd-find
# search for files/folder names only. Result can be fed to fzf for further filtering. For that use: fd | fzf. one can also make fd the searcher in fzf


url = 'https://github.com/sharkdp/fd'


def main(version=None):
    get_latest_release(url, download_n_extract=True, version=version)


if __name__ == '__main__':
    main()
