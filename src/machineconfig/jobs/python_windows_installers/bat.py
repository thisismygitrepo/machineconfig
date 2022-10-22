
# bat (rust-based, modern cat)
#  cargo install bat
# colored bat
from machineconfig.utils.utils import get_latest_release


url = 'https://github.com/sharkdp/bat'

if __name__ == '__main__':
    get_latest_release(url, download_n_extract=True)
