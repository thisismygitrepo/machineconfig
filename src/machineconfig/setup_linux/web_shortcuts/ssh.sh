#!/usr/bin/bash

echo """#=======================================================================
🔑 SSH KEY SETUP | Configuring SSH public key authentication
#=======================================================================
"""

if [ -z "$pubkey_url" ]; then
  echo """  🔍 No public key URL specified, using default GitHub URL
  🔗 URL: https://github.com/thisismygitrepo.keys
  """
  pubkey_url='https://github.com/thisismygitrepo.keys'  # (CHANGE APPROPRIATELY)
fi

if [ -z "$pubkey_string" ]; then
   echo """   📥 Fetching public key from URL...
   """
   export pubkey_string=$(curl --silent $pubkey_url)
fi

echo """#=======================================================================
🛠️  SSH SERVER INSTALLATION | Standard SSH setup
#=======================================================================

Setting up OpenSSH server...
"""
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_all.sh | sudo bash

echo """#=======================================================================
🔄 WSL CONFIGURATION | Additional WSL-specific setup
#=======================================================================
"""

# For WSL only, also run the following:
if [ -z "$port" ]; then
  echo """  🔌 No port specified, using default port 2222
  """
  export port=2222
fi

echo """📡 Setting up WSL-specific SSH configuration on port $port...
"""
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_wsl.sh | sudo bash

echo """#=======================================================================
✅ SETUP COMPLETE | SSH server configured successfully
#=======================================================================

🔒 SSH server is now ready to use
🔑 Authorized key has been configured
🔌 For WSL: Server configured to run on port $port
"""
