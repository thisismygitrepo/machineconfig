

curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh-server.sh | bash
cd ~
curl 'https://github.com/thisismygitrepo.keys' >> .ssh/authorized_keys
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh-server_add-sshkey.sh | bash
