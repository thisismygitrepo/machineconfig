
# apps
winget install --no-upgrade --name "Windows Terminal" --Id "Microsoft.WindowsTerminal" --source winget --scope user  # Terminal is is installed by default on W 11
winget install --no-upgrade --name "Powershell" --Id "Microsoft.PowerShell" --source winget --scope user  # powershell require admin

. $HOME\code\machineconfig\.venv\Scripts\activate.ps1
python -m fire machineconfig.setup_windows.wt_and_pwsh.install_nerd_fonts main
python -m fire machineconfig.setup_windows.wt_and_pwsh.set_wt_settings main
deactivate
