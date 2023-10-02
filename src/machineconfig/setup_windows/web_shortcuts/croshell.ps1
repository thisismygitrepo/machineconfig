
# with admin prviliage, run this:

# apps
winget install --no-upgrade --name "Windows Terminal" --Id "Microsoft.WindowsTerminal" --Source winget  # Terminal is is installed by default on W 11
winget install --no-upgrade --name "Powershell" --Id "Microsoft.PowerShell" --source winget  # powershell require admin

# virtual enviornment
# Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/ve.ps1 | Invoke-Expression
(iwr bit.ly/cfgvewindows).Content

# dev repos
# Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/repos.ps1 | Invoke-Expression
(iwr bit.ly/cfgreposwindows).Content

# symlinks
. ~/code/machineconfig/src/machineconfig/setup_windows/symlinks.ps1
