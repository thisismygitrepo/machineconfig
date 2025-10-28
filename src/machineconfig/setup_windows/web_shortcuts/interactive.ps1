

iex (iwr "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/uv.ps1").Content
iex (iwr "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/scripts/windows/mcfgs.ps1").Content

function devops   { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=7.32" devops $args }
function cloud    { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=7.32" cloud $args }
function agents   { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=7.32" agents $args }
function sessions { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=7.32" sessions $args }
function ftpx     { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=7.32" ftpx $args }
function fire     { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=7.32" fire $args }
function croshell { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=7.32" croshell $args }
function utils    { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=7.32" utils $args }
function terminal { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=7.32" terminal $args }

function d { wrap_in_shell_script devops @args }
function c { wrap_in_shell_script cloud @args }
function a { wrap_in_shell_script agents @args }
function ss { wrap_in_shell_script sessions @args }
function ff { wrap_in_shell_script ftpx @args }
function f { wrap_in_shell_script fire @args }
function rr { wrap_in_shell_script croshell @args }
function u { wrap_in_shell_script utils @args }
function t { wrap_in_shell_script terminal @args }

Write-Host "mcfg command aliases are now defined in this PowerShell session."
