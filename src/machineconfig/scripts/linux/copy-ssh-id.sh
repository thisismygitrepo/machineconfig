
# allow ssh to linux:

# on the linux machine:
sudo apt install openssh-server

# locally
sftp username@hostname  # put in password for once
# !!
mkdir .ssh
cd .ssh || exit
put ./.ssh/id_rsa.pub
exit  # sftp doesn't support cat command.
cat id_rsa.pub >> authorized_keys
