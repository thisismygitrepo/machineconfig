
# apps
winget install --no-upgrade --name "Windows Terminal" --Id "Microsoft.WindowsTerminal" --source winget --scope user  # Terminal is is installed by default on W 11
winget install --no-upgrade --name "Powershell" --Id "Microsoft.PowerShell" --source winget --scope user  # powershell require admin

. $HOME\code\machineconfig\\Scripts\activate.ps1
python -m fire machineconfig.setup_windows.wt_and_pwsh.set_pwsh_theme install_nerd_fonts
python -m fire machineconfig.setup_windows.wt_and_pwsh.set_wt_settings main
deactivate
