
if ( $env:VIRTUAL_ENV -eq $null)
{


    if ($args[0] -eq $null)
    {
        $name = "ve"
    }
    else
    {
        $name = $args[0]
    }

    #write-host $name

    & ("~/venvs/" + $name + "/Scripts/Activate.ps1")
    echo "Activated virtual environment ` $name ` " 
}
else

{
    echo "Virtual environment already activated ` $env:VIRTUAL_ENV ` "
}

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
