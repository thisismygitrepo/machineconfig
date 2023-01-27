

"""
Not used because it is not mature enough.
--version doesn't work
"""

from machineconfig.utils.utils import get_latest_release, tb


url = 'https://github.com/gsass1/NTop'


def main():
    link = get_latest_release(url, download_n_extract=False)
    link.joinpath('ntop.exe').download().move(folder=tb.get_env().WindowsApps, name="htop.exe", overwrite=True)


if __name__ == '__main__':
    main()
