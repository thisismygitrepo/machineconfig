#!/usr/bin/bash

curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh-server.sh | bash
mkdir -p .ssh
curl --silent 'https://github.com/thisismygitrepo.keys' >> ~/.ssh/authorized_keys  # consider adding this after curl: | head -n 1 >> author...
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh-server_add-sshkey.sh | bash

