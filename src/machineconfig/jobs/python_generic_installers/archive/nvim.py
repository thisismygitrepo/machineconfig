
from machineconfig.utils.utils import get_latest_release, find_move_delete_linux
from platform import system
import crocodile.toolbox as tb

repo_url = tb.P(r"https://github.com/neovim/neovim")
release = get_latest_release(repo_url.as_url_str(), download_n_extract=False)

if system() == 'Windows':
    release.joinpath("nvim-win64.msi").download()()
else:
    release.joinpath("nvim-linux64.tar.gz").download().ungz_untar(inplace=True)

if __name__ == '__main__':
    pass
