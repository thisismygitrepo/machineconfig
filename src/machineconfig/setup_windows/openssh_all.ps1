
$my_keys='https://github.com/thisismygitrepo.keys'
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh-server.sh | bash
curl $my_keys >> .ssh/authorized_keys
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh-server_add-sshkey.sh | bash
