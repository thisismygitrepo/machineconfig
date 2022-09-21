
from machineconfig.utils.utils import get_latest_release
from crocodile.toolbox import P, get_env
get_latest_release('https://github.com/sharkdp/bat', download_n_extract=True)
get_latest_release('https://github.com/sharkdp/fd', download_n_extract=True)
get_latest_release('https://github.com/junegunn/fzf', suffix='windows_amd64', download_n_extract=True)
get_latest_release('https://github.com/gokcehan/lf', name='lf-windows-amd64.zip', download_n_extract=True)
get_latest_release('https://github.com/BurntSushi/ripgrep', download_n_extract=True)
f = get_latest_release(r'https://github.com/Genivia/ugrep').joinpath('ugrep.exe').download(); f.move(folder=f.get_env().WindowsApps, overwrite=True)
P(r'https://download.sysinternals.com/files/ZoomIt.zip').download(P.home().joinpath('Downloads')).unzip(inplace=True).joinpath('ZoomIt.exe').move(folder=get_env().WindowsApps)
