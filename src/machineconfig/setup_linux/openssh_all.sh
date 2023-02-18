#!/usr/bin/bash

# most common ssh oitfalls: config files written in wrong LF/CLRF for this system (not readable), and, network problems, usually choose different port (2222 -> 2223) dot that from wsl and windows_server side.
mkdir -p ~/.ssh
echo $pubkey_string >> ~/.ssh/authorized_keys  # consider adding this after curl: | head -n 1 >> author...


sudo chmod 600 ~/.ssh/*
sudo chmod 700 ~/.ssh
echo "FINISHED modifying .ssh folder attributes."
#python -m fire ~/code/machineconfig/src/machineconfig/create_symlinks.py link_scripts
# netsh interface portproxy add v4tov4 listenport=2222 listenaddress=0.0.0.0 connectport=2222 connectaddres=172.29.153.156
# Google: ssh to wsl
# systemctl status/start/end sshd doesn't work on wsl


# https://askubuntu.com/questions/265982/unable-to-start-sshd
sudo apt purge openssh-server -y
sudo apt install openssh-server -y
sudo apt install tmate -y  # remote ssh from anywhere. # remote tmux, see https://tmate.io see https://devsession.is/
# sudo service ssh status
# sudo nano /etc/ssh/sshd_config
# sudo service ssh restart
# tunnels: https://www.youtube.com/watch?v=Wp7boqm3Xts
echo "FINISHED installing openssh-server and tmate."

