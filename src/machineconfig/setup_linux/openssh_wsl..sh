
sudo service ssh start
sudo ssh-keygen -A  # without this, ssh gives this error:
#  * Starting OpenBSD Secure Shell server sshd
#  sshd: no hostkeys available -- exiting.
sudo service ssh status

