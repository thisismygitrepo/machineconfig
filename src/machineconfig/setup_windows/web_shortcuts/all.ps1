
# apps
# Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/apps.ps1 | Invoke-Expression
# virtual enviornment
# Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/ve.ps1 | Invoke-Expression
(iwr bit.ly/cfgvewindows).Content | iex

# pwsh profile
$machineconfig = (& "$HOME\code\machineconfig\.venv\Scripts\python.exe" -c "print(__import__('machineconfig').__file__[:-12])")
# . $machineconfig/setup_windows/wt_and_pwsh.ps1  # experimental
# OR: python -c "from machineconfig.setup_windows.wt_and_pwsh.setup_pwsh_theme import install_nerd_fonts; install_nerd_fonts()"

# & "$HOME\code\machineconfig\.venv\Scripts\activate.ps1"
# python -m fire machineconfig.profile.create_hardlinks main --choice=all
# deactivate

# devapps:
. "$machineconfig\setup_windows\devapps.ps1"
