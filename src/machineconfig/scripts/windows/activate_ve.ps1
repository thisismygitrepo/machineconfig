

if (!$env:VIRTUAL_ENV) {  # no ve activated ==> activate one.
    if (!$args[0]) {  # nothing passed.  >> use defaults
        if (Test-Path "$env:USERPROFILE/.machineconfig/default_ve") {
            $name = Get-Content "$env:USERPROFILE//.machineconfig/default_ve"  # use default file it exists
            & "$name/Scripts/Activate.ps1"
        }
        else {  # no default file.  >> use default name
            $name = "ve"
            mkdir $env:USERPROFILE/.machineconfig -ErrorAction SilentlyContinue
            # New-Item -ItemType File -Path "$env:USERPROFILE/.machineconfig/default_ve" -Value $env:VIRTUAL_ENV
            "$env:USERPROFILE/venvs/$name" > $env:USERPROFILE/.machineconfig/default_ve
	    & "$env:USERPROFILE/venvs/$name/Scripts/Activate.ps1"
            }
        }
    else {
          $name = $args[0]
          & "$env:USERPROFILE/venvs/$name/Scripts/Activate.ps1"
         }

    if ($?) { Write-Host "✅ Activated virtual environment $env:VIRTUAL_ENV" }

}
else {

    # if $args[0] is passed, it's a new ve to activate
    if ($args[0]) {
        echo "Deactivating virtual environment $env:VIRTUAL_ENV"
        deactivate -ErrorAction SilentlyContinue
        $name = $args[0]
        & "$env:USERPROFILE/venvs/$name/Scripts/Activate.ps1"
        if ($?) { Write-Host "✅ Activated virtual environment $env:VIRTUAL_ENV" }
    }
    else {
        Write-Host "🤔 Virtual environment $env:VIRTUAL_ENV already activated"
    }

    if (!(Test-Path $env:USERPROFILE/.machineconfig/default_ve)) {
        New-Item -ItemType Directory -Path "$env:USERPROFILE/.machineconfig" -ErrorAction SilentlyContinue
#         New-Item -ItemType File -Path "$env:USERPROFILE/.machineconfig/default_ve" -Value $env:VIRTUAL_ENV
        echo "$env:VIRTUAL_ENV" > "$env:USERPROFILE/.machineconfig/default_ve"
    }
}

