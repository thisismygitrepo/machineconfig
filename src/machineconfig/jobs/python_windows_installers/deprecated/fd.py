from machineconfig.utils.installer import get_latest_release
from typing import Optional

# fd (rust)
# cargo install fd-find
# search for files/folder names only. Result can be fed to fzf for further filtering. For that use: fd | fzf. one can also make fd the searcher in fzf


repo_url = 'https://github.com/sharkdp/fd'
__doc__ = """fd is a simple, fast and user-friendly alternative to find."""

def main(version: Optional[str] = None):
    get_latest_release(repo_url=repo_url, exe_name="fd", download_n_extract=True, version=version)


if __name__ == '__main__':
    main()
