
from machineconfig.utils.utils import get_latest_release, tb
url = get_latest_release('https://github.com/gsass1/NTop', download_n_extract=False)
url.joinpath('ntop.exe').download().move(folder=tb.get_env().WindowsApps, name="htop.exe", overwrite=True)

