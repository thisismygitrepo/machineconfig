

$ve_name='ve'
& ~/venvs/$ve_name/Scripts/Activate.ps1

cd ~/code/machineconfig/src/machineconfig/scripts/windows

# ZoomIt
./croshell.ps1 -c "P(r'https://download.sysinternals.com/files/ZoomIt.zip').download(P.home().joinpath('Downloads')).unzip(inplace=True).joinpath('ZoomIt.exe').move(folder=get_env().WindowsApps)"

# bat (rust-based, modern cat)
#  cargo install --locked bat
#./croshell.ps1 -c "
#from machineconfig.utils.utils import get_latest_release
#f = P(get_latest_release('https://github.com/sharkdp/bat'))
#tmp = f.joinpath(f'bat-{f[-1]}-x86_64-pc-windows-msvc.zip').download().unzip(inplace=True)
#f = tmp.search()[0].joinpath(f'bat.exe').move(folder=f.get_env().WindowsApps)
#"

# fd (rust)
# cargo install fd-find
#./croshell.ps1 -c "
#from machineconfig.utils.utils import get_latest_release
#f = P(get_latest_release('https://github.com/sharkdp/fd'))
#tmp = f.joinpath(f'fd-{f[-1]}-x86_64-pc-windows-msvc.zip').download().unzip(inplace=True)
#f = tmp.search()[0].joinpath(f'fd.exe').move(folder=f.get_env().WindowsApps)
#"

# LF (glang)
./croshell.ps1 -c "
from machineconfig.utils.utils import get_latest_release
f = P(get_latest_release('https://github.com/gokcehan/lf')).joinpath('lf-windows-amd64.zip').download().unzip(inplace=True)
f.joinpath('lf.exe').move(folder=f.get_env().WindowsApps)"


# fzf (glang)
./croshell.ps1 -c "
from machineconfig.utils.utils import get_latest_release
f = P(get_latest_release('https://github.com/junegunn/fzf'))
tmp = f.joinpath(f'fzf-{f[-1]}-windows_amd64.zip').dteownload().unzip(inplace=True)
f = tmp.joinpath(f'fzf.exe').move(folder=f.get_env().WindowsApps)
"


#cd ~/code
#git clone https://github.com/neovide/neovide --depth 4
#cd neovide
#cargo build --release
#croshell.ps1 -c "P(r'~/code/neovide/target/release/neovide.exe').move(folder=get_env().WindowsApps)"


# steps as per: https://astronvim.github.io/
#pip install pynvim
#mv $HOME\AppData\Local\nvim $HOME\AppData\Local\nvim.bak
#mv $HOME\AppData\Local\nvim-data $HOME\AppData\Local\nvim-data.bak
#git clone https://github.com/AstroNvim/AstroNvim $HOME\AppData\Local\nvim
#nvim +PackerSync
#nvim --headless ":LspInstall pyright" +qall
#nvim --headless ":TSInstall python" +qall

# nvim with manual plugins
# nvim --headless +PlugInstall +qall  # this is non-interactive way of running :PlugInstall in nvim, run this after adding the plugins to init.vim
# cd ~\AppData\Local\nvim-data\plugged\coc.nvim  # should run after invim plugins are installed, especially coc.nvim for this directory to exist in the first place.
# npm install .
# nvim --headless -c 'CocInstall coc-pyright' -c 'qall'
