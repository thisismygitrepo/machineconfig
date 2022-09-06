
$ve_name = zz've'

& ~/venvs/$ve_name/Scripts/Activate.ps1
python -m fire machineconfig.create_symlinks main
# this is ambiguous, with which shell is this happening?
python -m fire machineconfig.create_symlinks add_scripts_to_path  # croshell is available, along with all scripts via $profile adding script path to env.Path
python -m fire "windows_terminal_setup/change_terminal_settings.py" main
#winget install JanDeDobbeleer.OhMyPosh
#python -m fire machineconfig.windows_terminal_setup/fancy_prompt_themes install
#python -m fire machineconfig.windows_terminal_setup/fancy_prompt_themes choose
cd ~/code/machineconfig/src/machineconfig/script/windows
./croshell.ps1 -c "P(r'https://download.sysinternals.com/files/ZoomIt.zip').download(P.home().joinpath('Downloads')).unzip(inplace=True).joinpath('ZoomIt.exe').move(folder=get_env().WindowsApps)"
./croshell.ps1 -c "
from machineconfig.utils.utils import get_latest_release
f = P(get_latest_release('https://github.com/gokcehan/lf')).joinpath('lf-windows-amd64.zip').download().unzip(inplace=True)
from crocodile import environment as env
f.move(folder=env.WindowsApps)"
