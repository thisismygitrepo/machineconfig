
# install server (sshd).
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh-server.ps1 | Invoke-Expression

if (!$pubkey_string) {
    $pubkey_url = 'https://github.com/thisismygitrepo.keys'  # (CHANGE APPROPRIATELY)
    $pubkey_string = (Invoke-WebRequest $pubkey_url).Content
} else {
    Write-Output "pubkey_string is already defined."
}


echo $null >> $HOME/.ssh/authorized_keys  # powershell way of touching a file if it doesn't exist
echo $pubkey_string >> $HOME/.ssh/authorized_keys
echo $pubkey_string > $HOME/.ssh/pubkey.pub

Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh-server_add-sshkey.ps1 | Invoke-Expression
ipconfig.exe

echo "Done"
echo "USE: ssh $env:USERNAME@$env:COMPUTERNAME -p 22"

