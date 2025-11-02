
iex (iwr "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/uv.ps1").Content
# iex (iwr "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/scripts/windows/wrap_mcfg.ps1").Content
uv tool install --upgrade  --python 3.14 machineconfig both

devops install --group ESSENTIAL_SYSTEM

# configs
devops config copy-assets both
devops config public --method copy --on-conflict overwrite-default-path --which all
devops config shell  # pwsh is neeeded first to get $PROFILE value.
devops config shell --which nushell

wt  # start Windows Terminal to pick up config changes

devops install --group ESSENTIAL
