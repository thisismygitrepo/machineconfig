
$ve_name='ve'
& ~/venvs/$ve_name/Scripts/Activate.ps1
python -m fire machineconfig.setup_windows.wt_and_pwsh.set_pwsh_theme main
python -m fire machineconfig.setup_windows.wt_and_pwsh.set_wt_settings main
deactivate
