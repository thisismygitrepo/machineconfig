
# with admin prviliage, run this:

# apps
winget install --name "Windows Terminal" --Id "Microsoft.WindowsTerminal" --Source winget  # Terminal is is installed by default on W 11
winget install --name "Powershell" --Id "Microsoft.PowerShell" --source winget  # powershell require admin
winget install --Id "Python.Python.3.11" --source winget

# virtual enviornment
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/ve.ps1 | Invoke-Expression

# dev repos
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/repos.ps1 | Invoke-Expression

# symlinks
. ~/code/machineconfig/src/machineconfig/setup_windows/symlinks.ps1
