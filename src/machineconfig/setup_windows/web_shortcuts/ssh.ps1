# NOT INTENDED FOR PUBLIC USE. 
$pubkey_url='https://github.com/thisismygitrepo.keys'  # (CHANGE APPROPRIATELY)
$pubkey_string=(Invoke-WebRequest $pubkey_url).Content
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh_all.ps1 | Invoke-Expression
