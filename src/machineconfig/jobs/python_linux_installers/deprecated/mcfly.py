from machineconfig.utils.installer import get_latest_release
from typing import Optional

repo_url = "https://github.com/cantino/mcfly"
__doc__ = """Fly through your shell history. Great Scott!"""

def main(version: Optional[str] = None):
    get_latest_release(repo_url=repo_url, exe_name="mcfly", suffix="x86_64-unknown-linux-musl", download_n_extract=True, compression="tar.gz", version=version)


if __name__ == '__main__':
    main()
