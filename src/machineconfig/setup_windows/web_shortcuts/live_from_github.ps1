
# Short @ https://bit.ly/cfgwg

irm "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/uv.ps1" | iex
irm "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/scripts/windows/wrap_mcfg.ps1" | iex

function mcfg { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "git+https://github.com/thisismygitrepo/machineconfig" mcfg $args }

function devops {mcfg devops @args }
function cloud {mcfg cloud @args }
function agents {mcfg agents @args }
function sessions {mcfg sessions @args }
function ftpx {mcfg ftpx @args }
function fire {mcfg fire @args }
function croshell {mcfg croshell @args }
function utils {mcfg utils @args }
function terminal {mcfg terminal @args }
function msearch {mcfg msearch @args }

function d { wrap_in_shell_script mcfg devops @args }
function c { wrap_in_shell_script mcfg cloud @args }
function a { wrap_in_shell_script mcfg agents @args }
function sx { wrap_in_shell_script mcfg sessions @args }
function fx { wrap_in_shell_script mcfg ftpx @args }
function f { wrap_in_shell_script mcfg fire @args }
function rr { wrap_in_shell_script mcfg croshell @args }
function u { wrap_in_shell_script mcfg utils @args }
function t { wrap_in_shell_script mcfg terminal @args }
function ms { wrap_in_shell_script mcfg msearch @args }

Write-Host "mcfg command aliases are now defined in this PowerShell session."
