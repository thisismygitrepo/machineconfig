
# with admin prviliage, run this in order to minimally install croshell.

# virtual enviornment
# Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/ve.ps1 | Invoke-Expression
(iwr bit.ly/cfgvewindows).Content | iex

# dev repos
# Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/repos.ps1 | Invoke-Expression
(iwr bit.ly/cfgreposwindows).Content | iex

# symlinks
. $HOME/code/machineconfig/src/machineconfig/setup_windows/symlinks.ps1

# windows terminal and powershell
(iwr bit.ly/cfgwt).Content | iex
