
# bat (rust-based, modern cat)
#  cargo install bat
# colored bat
from machineconfig.utils.utils import get_latest_release

__doc__ = """A cat(1) clone with wings."""

url = 'https://github.com/sharkdp/bat'


def main(version=None): get_latest_release(url, download_n_extract=True, version=version)


if __name__ == '__main__':
    main()
