
# to update ubuntu
do-release-upgrade # /etc/update-manager/release-upgrades

# to update the kernel
# from https://askubuntu.com/questions/1388115/how-do-i-update-my-kernel-to-the-latest-one
wget https://raw.githubusercontent.com/pimlie/ubuntu-mainline-kernel.sh/master/ubuntu-mainline-kernel.sh
sudo install ubuntu-mainline-kernel.sh /usr/local/bin/
sudo ubuntu-mainline-kernel.sh -c
sudo ubuntu-mainline-kernel.sh -i -y
sudo reboot
