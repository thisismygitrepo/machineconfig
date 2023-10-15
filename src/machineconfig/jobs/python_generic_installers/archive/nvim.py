
"""nvim
"""

from machineconfig.utils.installer import get_latest_release
from platform import system
import crocodile.toolbox as tb

repo_url = tb.P(r"https://github.com/neovim/neovim")
release = get_latest_release(repo_url.as_url_str(), exe_name="nvim", download_n_extract=False)

if isinstance(release, tb.P):
    if system() == 'Windows':
        release.joinpath("nvim-win64.msi").download()()
    else:
        release.joinpath("nvim-linux64.tar.gz").download().ungz_untar(inplace=True)


if __name__ == '__main__':
    pass
