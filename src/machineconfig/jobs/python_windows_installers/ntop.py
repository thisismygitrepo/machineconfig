
from machineconfig.utils.utils import get_latest_release, tb

url = 'https://github.com/gsass1/NTop'

if __name__ == '__main__':
    url = get_latest_release(url, download_n_extract=False)
    url.joinpath('ntop.exe').download().move(folder=tb.get_env().WindowsApps, name="htop.exe", overwrite=True)

