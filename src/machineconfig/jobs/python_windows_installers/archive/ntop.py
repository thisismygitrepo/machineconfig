

"""
Not used because it is not mature enough.
--version doesn't work
"""

from machineconfig.utils.utils import P
from machineconfig.utils.installer import get_latest_release

url = 'https://github.com/gsass1/NTop'


def main():
    link = get_latest_release(repo_url=url, exe_name="ntop", download_n_extract=False)
    if not isinstance(link, P): raise ValueError(f"Failed to get latest release. Expected a Path object, got {url}")
    link.joinpath('ntop.exe').download().move(folder=P.get_env().WindowsApps, name="htop.exe", overwrite=True)


if __name__ == '__main__':
    main()
