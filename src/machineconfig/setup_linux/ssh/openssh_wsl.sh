#!/usr/bin/bash
# 🐧 WSL2 SSH Configuration for LAN Access 🌐
# Purpose: Enable SSH access to WSL2 from LAN (requires wsl_server.ps1 in Windows)
# Common pitfall: sshd fails after config changes due to wrong line endings/permissions

# 🔍 Check if running in WSL
if [[ $(uname -a) == *"icrosoft"* ]]; then
  echo "✅ Running inside WSL"
else
  echo "❌ Not running inside WSL, no need for this script"
  exit 0
fi

# 🔢 Set SSH port
if [ -z "$port" ]; then
  port=2222
  echo "📝 Port variable not defined, setting it to $port"
fi

# 🛠️ Configure SSH
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
sudo sed -i 's/#Port 22/Port '$port'/g' /etc/ssh/sshd_config
sudo sed -i 's/#ListenAddress 0.0.0.0/ListenAddress 0.0.0.0/g' /etc/ssh/sshd_config
sudo sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/g' /etc/ssh/sshd_config
sudo sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config

# 🔑 Generate host keys and restart service
sudo service ssh start
sudo ssh-keygen -A
sudo service ssh --full-restart
sudo service ssh status

echo "✨ FINISHED configuring SSH in WSL2."

# 📚 References:
# Service startup: https://superuser.com/questions/1701853/how-to-enable-a-service-to-start-with-wsl2
# WSL config: https://learn.microsoft.com/en-us/windows/wsl/networking#accessing-a-wsl-2-distribution-from-your-local-area-network-lan

