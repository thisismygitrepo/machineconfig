
# search for words in files.
from machineconfig.utils.utils import get_latest_release, P
from typing import Optional

url = r'https://github.com/Genivia/ugrep'
__doc__ = """A fast, portable, feature-rich command-line search tool"""

def main(version: Optional[str] = None):
    f = get_latest_release(repo_url=url, exe_name="ugrep", version=version)
    if isinstance(f, P):
        f = f.joinpath('ugrep.exe').download()
        f.move(folder=f.get_env().WindowsApps, overwrite=True)


if __name__ == '__main__':
    main()
