

if ($args[0] -eq $null)
{
    if ($env:VENV_NAME -eq $null) {$name = "ve"}
    else {$name = $env:VENV_NAME}
}
else {$name = $args[0]}

#write-host $name

& ("~/venvs/" + $name + "/Scripts/Activate.ps1")

#function Activate-VirtualEnv{
#    [CmdletBinding()]
#    param (
#        [String] $VirtualEnvName = "ve"
#    )
#    & ("~/venvs/" + $VirtualEnvName + "/Scripts/Activate.ps1")
#}

#$drive = Read-Host "Enviroment name (ve)"
#if ( $drive -eq "" )
#{
#    $drive = "ve"
#}
#& ("~/venvs/" + $drive + "/Scripts/Activate.ps1")
