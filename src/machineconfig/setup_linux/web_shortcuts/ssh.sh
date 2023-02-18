
if [ -z "$pubkey_url" ]; then
  pubkey_url='https://github.com/thisismygitrepo.keys'  # (CHANGE APPROPRIATELY)
fi

if [ -z "$pubkey_string" ]; then
   export pubkey_string=$(curl --silent $pubkey_url)
fi

curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_all.sh | sudo bash
# For WSL only, also run the following:

if [ -z "$port" ]; then
  export port=2222
fi

curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_wsl.sh | sudo bash
