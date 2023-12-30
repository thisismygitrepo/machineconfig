
# rg (rust)
# cargo install ripgrep
# used by lvim and spacevim
from machineconfig.utils.installer import get_latest_release
from typing import Optional


repo_url = 'https://github.com/BurntSushi/ripgrep'
__doc__ = """recursively searches directories for a regex pattern while respecting your gitignore rules"""


def main(version: Optional[str] = None):
    get_latest_release(repo_url=repo_url, download_n_extract=True, exe_name='rg', version=version)


if __name__ == '__main__':
    main()
