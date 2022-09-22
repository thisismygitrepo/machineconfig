
# https://superuser.com/questions/1701853/how-to-enable-a-service-to-start-with-wsl2

sudo service ssh start
sudo ssh-keygen -A  # without this, ssh gives this error:
#  * Starting OpenBSD Secure Shell server sshd
#  sshd: no hostkeys available -- exiting.
sudo service ssh status
sudo service ssh --full-restart  # use systemctl if this doesn't work.


