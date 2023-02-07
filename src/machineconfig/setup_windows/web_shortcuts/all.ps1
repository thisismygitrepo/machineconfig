
# apps
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/apps.ps1 | Invoke-Expression
# virtual enviornment
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/ve.ps1 | Invoke-Expression
# dev repos
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/repos.ps1 | Invoke-Expression
# symlinks: locally, run: `ftpsx username@hostname[:port] ~/dotfiles -z`, then, on the remote:
. ~/code/machineconfig/src/machineconfig/setup_windows/symlinks.ps1
# pwsh profile
# ~/code/machineconfig/src/machineconfig/setup_windows/wt_and_pwsh.ps1  # experimental
# devapps:
~/code/machineconfig/src/machineconfig/setup_windows/devapps.ps1

