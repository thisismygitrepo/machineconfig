#!/usr/bin/bash

# https://askubuntu.com/questions/265982/unable-to-start-sshd
sudo apt-get purge openssh-server -y
sudo apt-get install openssh-server -y

# sudo apt install tmate -y  # remote tmux, see https://tmate.io see https://devsession.is/
sudo apt-get install tmate -y  # remote ssh from anywhere.

# sudo service ssh status
# sudo nano /etc/ssh/sshd_config
# sudo service ssh restart
# tunnels: https://www.youtube.com/watch?v=Wp7boqm3Xts

echo "FINISHED installing openssh-server and tmate."
