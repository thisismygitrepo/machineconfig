
# NOT INTENDED FOR PUBLIC USE. 

if (!$pubkey_string) {
    $pubkey_url = 'https://github.com/thisismygitrepo.keys'  # (CHANGE APPROPRIATELY)
    $pubkey_string = (Invoke-WebRequest $pubkey_url).Content
} else {
    Write-Output "pubkey_string is already defined."
}

Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh_all.ps1 | Invoke-Expression
