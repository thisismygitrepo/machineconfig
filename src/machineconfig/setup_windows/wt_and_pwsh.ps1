
# apps
winget install --no-upgrade --name "Windows Terminal" --Id "Microsoft.WindowsTerminal" --Source winget  # Terminal is is installed by default on W 11
winget install --no-upgrade --name "Powershell" --Id "Microsoft.PowerShell" --source winget  # powershell require admin

# & "$env:USERPROFILE\scripts\activate_ve.ps1"
. $HOME\venvs\ve\Scripts\activate.ps1
python -m fire machineconfig.setup_windows.wt_and_pwsh.set_pwsh_theme install_nerd_fonts
python -m fire machineconfig.setup_windows.wt_and_pwsh.set_wt_settings main
deactivate
