
# apps
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/apps.ps1 | Invoke-Expression
# virtual enviornment
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/ve.ps1 | Invoke-Expression
# dev repos
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/repos.ps1 | Invoke-Expression
# symlinks: locally, run: `ftpsx username@hostname[:port] ~/dotfiles -z`, then, on the remote:
$machineconfig_path = (python -c "print(__import__('machineconfig').__file__[:-12])")
. $machineconfig/setup_windows/symlinks.ps1
# pwsh profile
# $machineconfig/setup_windows/wt_and_pwsh.ps1  # experimental
# devapps:
$machineconfig/setup_windows/devapps.ps1
