

iex (iwr "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/uv.ps1").Content
iex (iwr "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/scripts/windows/wrap_mcfg.ps1").Content

function devops   { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=7.94" devops $args }
function cloud    { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=7.94" cloud $args }
function agents   { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=7.94" agents $args }
function sessions { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=7.94" sessions $args }
function ftpx     { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=7.94" ftpx $args }
function fire     { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=7.94" fire $args }
function croshell { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=7.94" croshell $args }
function utils    { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=7.94" utils $args }
function terminal { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=7.94" terminal $args }
function msearch  { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=7.94" msearch $args }

function d { wrap_in_shell_script devops @args }
function c { wrap_in_shell_script cloud @args }
function a { wrap_in_shell_script agents @args }
function sx { wrap_in_shell_script sessions @args }
function fx { wrap_in_shell_script ftpx @args }
function f { wrap_in_shell_script fire @args }
function rr { wrap_in_shell_script croshell @args }
function u { wrap_in_shell_script utils @args }
function t { wrap_in_shell_script terminal @args }
function ms { wrap_in_shell_script msearch @args }

Write-Host "mcfg command aliases are now defined in this PowerShell session."

devops self interactive
