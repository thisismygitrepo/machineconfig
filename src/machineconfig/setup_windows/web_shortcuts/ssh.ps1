
$pubkey_url='https://github.com/thisismygitrepo.keys'  # (CHANGE APPROPRIATELY)
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh_all.ps1 | Invoke-Expression
