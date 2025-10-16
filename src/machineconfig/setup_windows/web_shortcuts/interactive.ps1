

iex (iwr "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/uv.ps1").Content
function mcfg {
    & "$HOME\.local\bin\uv.exe" run --python 3.14 --with "machineconfig>=6.36" mcfg $args
}
function d { mcfg devops @args }
function c { mcfg cloud @args }
function a { mcfg agents @args }
function s { mcfg sessions @args }
function ff { mcfg ftpx @args }
function f { mcfg fire @args }
function cs { mcfg croshell @args }
Write-Host "mcfg command aliases are now defined in this PowerShell session."
