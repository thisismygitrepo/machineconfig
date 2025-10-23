

iex (iwr "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/uv.ps1").Content
function mcfg {
    & "$HOME\.local\bin\uv.exe" run --python 3.14 --with "machineconfig>=6.81" mcfg $args
}
function d { mcfg devops @args }
function c { mcfg cloud @args }
function a { mcfg agents @args }
function ss { mcfg sessions @args }
function ff { mcfg ftpx @args }
function f { mcfg fire @args }
function rr { mcfg croshell @args }
function u { mcfg utils @args }
Write-Host "mcfg command aliases are now defined in this PowerShell session."
