
$my_keys='https://github.com/thisismygitrepo.keys'
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/blob/main/src/machineconfig/setup_windows/openssh-server.ps1 | Invoke-Expression
cd ~
(Invoke-WebRequest $my_keys).Content >> .ssh/authorized_keys
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/blob/main/src/machineconfig/setup_windows/openssh-server_add-sshkey.ps1 | Invoke-Expression
