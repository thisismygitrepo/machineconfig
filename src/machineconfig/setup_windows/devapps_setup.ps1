

$ve_name='ve'
& ~/venvs/$ve_name/Scripts/Activate.ps1
cd ~/code/machineconfig/src/machineconfig/script/windows

# ZoomIt
./croshell.ps1 -c "P(r'https://download.sysinternals.com/files/ZoomIt.zip').download(P.home().joinpath('Downloads')).unzip(inplace=True).joinpath('ZoomIt.exe').move(folder=get_env().WindowsApps)"

# LF
./croshell.ps1 -c "
from machineconfig.utils.utils import get_latest_release
f = P(get_latest_release('https://github.com/gokcehan/lf')).joinpath('lf-windows-amd64.zip').download().unzip(inplace=True)
f.joinpath('lf.exe').move(folder=f.get_env().WindowsApps)"

# bat (modern cat)
./croshell.ps1 -c "
from machineconfig.utils.utils import get_latest_release
f = P(get_latest_release('https://github.com/sharkdp/bat'))
tmp = f.joinpath(f'bat-{f[-1]}-x86_64-pc-windows-msvc.zip').download().unzip(inplace=True)
f = tmp.search()[0].joinpath(f'bat.exe').move(folder=f.get_env().WindowsApps)
"

# nvim extensions
pip install pynvim
nvim --headless +PlugInstall +qall  # this is non-interactive way of running :PlugInstall in nvim, run this after adding the plugins to init.vim
cd ~\AppData\Local\nvim-data\plugged\coc.nvim  # should run after invim plugins are installed, especially coc.nvim for this directory to exist in the first place.
npm install .
nvim --headless -c 'CocInstall coc-pyright' -c 'qall'
