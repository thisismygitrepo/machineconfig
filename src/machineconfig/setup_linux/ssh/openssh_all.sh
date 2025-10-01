#!/usr/bin/bash
# 🔐 OpenSSH Server Setup and Configuration

# Common pitfalls: 
# 🚫 Wrong line endings (LF/CRLF) in config files
# 🌐 Network port conflicts (try 2222 -> 2223) between WSL and Windows

# 📁 Setup SSH directory and permissions
mkdir -p ~/.ssh
echo $pubkey_string >> ~/.ssh/authorized_keys
sudo chmod 600 ~/.ssh/*
sudo chmod 700 ~/.ssh
echo "✅ FINISHED modifying .ssh folder attributes."

# 🔄 Clean install OpenSSH server
sudo nala install openssh-server -y || true  # try to install first
sudo nala purge openssh-server -y
sudo nala install openssh-server -y
echo "✅ FINISHED installing openssh-server."

# 📝 Additional commands if needed:
# sudo service ssh status
# sudo nano /etc/ssh/sshd_config
# sudo service ssh restart
# For tunnels see: https://www.youtube.com/watch?v=Wp7boqm3Xts
