
$ve_name='ve'

& ~/venvs/$ve_name/Scripts/Activate.ps1
python -m fire "./create_symlinks.py" main
# this is ambiguous, with which shell is this happening?
python -m fire "./create_symlinks.py" add_scripts_to_path  # croshell is available, along with all scripts via $profile adding script path to env.Path
python -m fire "windows_terminal_setup/change_terminal_settings.py" main
#winget install JanDeDobbeleer.OhMyPosh
#python -m fire "windows_terminal_setup/fancy_prompt_themes.py" install
#python -m fire "windows_terminal_setup/fancy_prompt_themes.py" choose
cd ~/code/machineconfig/src/machineconfig/script/windows
./croshell.ps1 -c "P(r'https://download.sysinternals.com/files/ZoomIt.zip').download(P.home().joinpath('Downloads')).unzip(inplace=True).joinpath('ZoomIt.exe').move(folder=get_env().WindowsApps)"
