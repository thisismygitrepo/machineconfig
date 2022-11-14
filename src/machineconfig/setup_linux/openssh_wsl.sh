
# The purpose of this file is to config SSH in WSL2 so that it is accessible from LAN.
# before running this script, WSL2 can only be SSHed from the same machine, given WSL2 address.
# after running this setup, user from within windows must run wsl_server.ps1 to activate port forwarding.

sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
sudo sed -i 's/#Port 22/Port 2222/g' /etc/ssh/sshd_config
sudo sed -i 's/#ListenAddress 0.0.0.0/ListenAddress 0.0.0.0/g' /etc/ssh/sshd_config
sudo sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/g' /etc/ssh/sshd_config
# sudo sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config

# The following is to encounter this error:
#  * Starting OpenBSD Secure Shell server sshd
#  sshd: no hostkeys available -- exiting.
sudo service ssh start
sudo ssh-keygen -A  # without this, ssh gives this error: use systemctl if this doesn't work. sudo systemctl status ssh
sudo service ssh --full-restart
sudo service ssh status
echo "FINISHED configuring SSH in WSL2."

# https://superuser.com/questions/1701853/how-to-enable-a-service-to-start-with-wsl2
# another way: https://gist.github.com/dentechy/de2be62b55cfd234681921d5a8b6be11
# relevant wsl.config file: https://superuser.com/questions/1150597/linux-overrides-etc-hosts-on-windows-linux-subsystem
# more on wsl config https://www.aleksandrhovhannisyan.com/blog/limiting-memory-usage-in-wsl-2/#:~:text=According%20to%20Microsoft's%20documentation%2C%20the,whichever%20happens%20to%20be%20smaller.
# https://learn.microsoft.com/en-us/windows/wsl/networking#accessing-a-wsl-2-distribution-from-your-local-area-network-lan

