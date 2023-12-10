
$CONFIG_PATH = "$env:USERPROFILE\.config\machineconfig\default_ve"

if (!$env:VIRTUAL_ENV)
    {  # no ve activated ==> activate one.
    if (!$args[0]) {  # nothing passed.  >> use defaults

        if (Test-Path ".\.ve_path") {
            $name = Get-Content "./.ve_path"  # use default file it exists
            & "$name\Scripts\Activate.ps1"
        }
        elseif (Test-Path $CONFIG_PATH) {
            $name = Get-Content $CONFIG_PATH  # use default file it exists
            & "$name\Scripts\Activate.ps1"
        }
        else {  # no default file.  >> use default name
            $name = "ve"
            mkdir $env:USERPROFILE\.config\machineconfig -ErrorAction SilentlyContinue
            "$env:USERPROFILE\venvs\$name" > $CONFIG_PATH
	    & "$env:USERPROFILE\venvs\$name\Scripts\Activate.ps1"
            }

        }
    else {
          $name = $args[0]
          & "$env:USERPROFILE\venvs\$name\Scripts\Activate.ps1"
         }

    if ($?) { Write-Host "`u{2705} Activated virtual environment $env:VIRTUAL_ENV" }

}

else {

    # if $args[0] is passed, it's a new ve to activate
    # echo "$env:USERPROFILE\venvs\$args"
    $ve_name = $args[0]
    if ($args[0] -and "$env:VIRTUAL_ENV" -ne "$env:USERPROFILE\venvs\$ve_name") {
        Write-Output "`u{1F53B} Deactivating virtual environment $env:VIRTUAL_ENV"
        deactivate -ErrorAction SilentlyContinue
        $name = $args[0]
        & "$env:USERPROFILE\venvs\$name\Scripts\Activate.ps1"
        if ($?) { Write-Host "`u{2705} Activated virtual environment $env:VIRTUAL_ENV " }
    }
    else {
        Write-Host "`u{26A0} Virtual environment '$env:VIRTUAL_ENV' is already activated "
    }

    if (!(Test-Path $CONFIG_PATH)) {
        New-Item -ItemType Directory -Path $env:USERPROFILE\.config\machineconfig -ErrorAction SilentlyContinue
        $env:VIRTUAL_ENV > $CONFIG_PATH
    }
}

