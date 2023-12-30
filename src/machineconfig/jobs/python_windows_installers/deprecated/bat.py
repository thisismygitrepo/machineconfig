
# bat (rust-based, modern cat)
#  cargo install bat
# colored bat
from machineconfig.utils.installer import get_latest_release
from typing import Optional


__doc__ = """A cat(1) clone with wings."""
repo_url = 'https://github.com/sharkdp/bat'


def main(version: Optional[str] = None) -> None:
    get_latest_release(repo_url=repo_url, exe_name="bat", download_n_extract=True, version=version)


if __name__ == '__main__':
    main()
