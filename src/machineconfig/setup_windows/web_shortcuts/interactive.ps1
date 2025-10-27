

iex (iwr "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/uv.ps1").Content
iex (iwr "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/scripts/windows/mcfgs.ps1").Content

function devops   { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=6.98" devops $args }
function cloud    { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=6.98" cloud $args }
function agents   { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=6.98" agents $args }
function sessions { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=6.98" sessions $args }
function ftpx     { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=6.98" ftpx $args }
function fire     { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=6.98" fire $args }
function croshell { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=6.98" croshell $args }
function utils    { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=6.98" utils $args }
function terminal { & "$HOME\.local\bin\uvx.exe" --python 3.14 --from "machineconfig>=6.98" terminal $args }

function d { wrap_in_op_code devops @args }
function c { wrap_in_op_code cloud @args }
function a { wrap_in_op_code agents @args }
function ss { wrap_in_op_code sessions @args }
function ff { wrap_in_op_code ftpx @args }
function f { wrap_in_op_code fire @args }
function rr { wrap_in_op_code croshell @args }
function u { wrap_in_op_code utils @args }
function t { wrap_in_op_code terminal @args }

Write-Host "mcfg command aliases are now defined in this PowerShell session."
