
$ve_name='ve'
& ~/venvs/$ve_name/Scripts/Activate.ps1
python -m fire machineconfig.create_symlinks main
python -m fire machingconfig.setup_windows_terminal.set_settings main
python -m fire machingconfig.setup_windows_terminal.ohmyposh install
python -m fire machingconfig.setup_windows_terminal.change_shell_profile install
