
#python -m fire ~/code/machineconfig/src/machineconfig/create_symlinks.py link_scripts
sudo chmod 600 ~/.ssh/*
sudo chmod 700 ~/.ssh
# cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
echo "All Done!"

# netsh interface portproxy add v4tov4 listenport=2222 listenaddress=0.0.0.0 connectport=2222 connectaddres=172.29.153.156
# Google: ssh to wsl
# sudo service ssh --full-restart
# systemctl status/start/end sshd doesn't work on wsl
