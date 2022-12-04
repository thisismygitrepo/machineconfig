#!/usr/bin/bash
# most common ssh oitfalls: config files written in wrong LF/CLRF for this system (not readable), and, network problems, usually choose different port (2222 -> 2223) dot that from wsl and windows_server side.
mkdir -p ~/.ssh
curl --silent 'https://github.com/thisismygitrepo.keys' >> ~/.ssh/authorized_keys  # consider adding this after curl: | head -n 1 >> author...
# cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh-server_chmod.sh | bash
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh-server.sh | bash
#echo "FINISHED installing openssh-server and tmate."

