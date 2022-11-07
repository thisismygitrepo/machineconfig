
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh-server.ps1 | Invoke-Expression

$my_keys=$args[0]
if ($my_keys -eq $null) {
    $my_keys="https://github.com/thisismygitrepo.keys"
}
cd ~
(Invoke-WebRequest $my_keys).Content >> .ssh/authorized_keys
(Invoke-WebRequest $my_keys).Content >> .ssh/id_rsa.pub
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh-server_add-sshkey.ps1 | Invoke-Expression
