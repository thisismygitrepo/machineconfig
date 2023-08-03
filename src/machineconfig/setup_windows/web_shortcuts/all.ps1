
# apps
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/apps.ps1 | Invoke-Expression
# virtual enviornment
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/ve.ps1 | Invoke-Expression
# dev repos
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/repos.ps1 | Invoke-Expression

# pwsh profile
$machineconfig = (python -c "print(__import__('machineconfig').__file__[:-12])")
. $machineconfig/setup_windows/wt_and_pwsh.ps1  # experimental
# OR: python -c "from machineconfig.setup_windows.wt_and_pwsh.setup_pwsh_theme import install_nerd_fonts; install_nerd_fonts()"

# devapps:
. "$machineconfig/setup_windows/devapps.ps1"

# symlinks: locally, run: `ftpsx username@hostname[:port] ~/dotfiles -z`, then, on the remote:
#. "$machineconfig/setup_windows/symlinks.ps1"  # one cane either do this with devops utility any time.
