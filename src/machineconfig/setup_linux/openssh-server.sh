#!/usr/bin/bash

sudo apt install openssh-server -y
sudo apt-get install tmate -y  # remote ssh from anywhere.

# sudo service ssh status
# sudo nano /etc/ssh/sshd_config
# sudo service ssh restart
# tunnels: https://www.youtube.com/watch?v=Wp7boqm3Xts
cd ~
mkdir -p .ssh
echo "FINISHED installing openssh-server and tmate."