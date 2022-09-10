
$ve_name='ve'
& ~/venvs/$ve_name/Scripts/Activate.ps1
python -m fire machineconfig.create_symlinks main
python -m fire "windows_terminal_setup/change_terminal_settings.py" main
