
irm "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/uv.ps1" | iex
# irm "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/scripts/windows/wrap_mcfg.ps1" | iex

uv tool install --upgrade  --python 3.14 machineconfig

devops install --group sysabc

# configs
devops config copy-assets both
devops config public --method copy --on-conflict overwrite-default-path --which all
devops config shell
devops config shell --which nushell

devops install --group termabc 
wt  # start Windows Terminal to pick up config changes
devops install --group gui
