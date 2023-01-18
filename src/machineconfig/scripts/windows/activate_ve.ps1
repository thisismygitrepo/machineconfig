

if (!$env:VIRTUAL_ENV) {  # no ve activated ==> activate one.
    if (!$args[0]) {  # nothing passed.  >> use defaults
        if (Test-Path "$env:USERPROFILE//.machineconfig/default_ve") {
            $name = Get-Content "$env:USERPROFILE//.machineconfig/default_ve"  # use default file it exists
            & "$name/Scripts/Activate.ps1"
        }
        else {  # no default file.  >> use default name
            $name = "ve"
            & "$env:USERPROFILE/venvs/$name/Scripts/Activate.ps1"
            mkdir $env:USERPROFILE/.machineconfig -ErrorAction SilentlyContinue
            New-Item -ItemType File -Path "$env:USERPROFILE/.machineconfig/default_ve" -Value $env:VIRTUAL_ENV
            }
        }
    else {
          $name = $args[0]
          & "$env:USERPROFILE/venvs/$name/Scripts/Activate.ps1"
         }

    Write-Host "Activated virtual environment $env:VIRTUAL_ENV"

}
else {

    # if $args[0] is passed, it's a new ve to activate
    if ($args[0]) {
        echo "Deactivating virtual environment $env:VIRTUAL_ENV "
        deactivate -ErrorAction SilentlyContinue
        $name = $args[0]
        & "$env:USERPROFILE/venvs/$name/Scripts/Activate.ps1"
        Write-Host "Activated virtual environment $env:VIRTUAL_ENV "
    }
    else {
        Write-Host "Virtual environment $env:VIRTUAL_ENV already activate"
    }

    if (!(Test-Path $env:USERPROFILE/.machineconfig/default_ve)) {
        New-Item -ItemType Directory -Path "$env:USERPROFILE/.machineconfig" -ErrorAction SilentlyContinue
        New-Item -ItemType File -Path "$env:USERPROFILE/.machineconfig/default_ve" -Value $env:VIRTUAL_ENV
    }
}

#if ( $env:VIRTUAL_ENV -eq $null)
#{
#    if ($args[0] -eq $null)
#    {
#        $name = "ve"
#    }
#    else
#    {
#        $name = $args[0]
#    }
#    #write-host $name
#    & ("$env:USERPROFILE/venvs/" + $name + "/Scripts/Activate.ps1")
#    echo "Activated virtual environment ` $name ` "
#}
#else
#{
#    echo "Virtual environment already activated ` $env:VIRTUAL_ENV ` "
#}


#function Activate-VirtualEnv{
#    [CmdletBinding()]
#    param (
#        [String] $VirtualEnvName = "ve"
#    )
#    & ("$env:USERPROFILE/venvs/" + $VirtualEnvName + "/Scripts/Activate.ps1")
#}

#$drive = Read-Host "Enviroment name (ve)"
#if ( $drive -eq "" )
#{
#    $drive = "ve"
#}
#& ("$env:USERPROFILE/venvs/" + $drive + "/Scripts/Activate.ps1")
