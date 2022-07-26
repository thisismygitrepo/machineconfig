
#python -m fire ~/code/machineconfig/src/machineconfig/create_symlinks.py link_scripts
sudo chmod 600 ~/.ssh/*
sudo chmod 700 ~/.ssh
cat .ssh/id_rsa.pub > .ssh/authorized_keys
echo "All Done!"
