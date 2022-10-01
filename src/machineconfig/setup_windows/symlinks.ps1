
$ve_name='ve'
& ~/venvs/$ve_name/Scripts/Activate.ps1
python -m fire machineconfig.symlinks.create main

python -m fire machineconfig.setup_windows_terminal.set_settings main
python -m fire machineconfig.setup_windows_terminal.ohmyposh install
python -m fire machineconfig.setup_windows_terminal.ohmyposh change_shell_profile
