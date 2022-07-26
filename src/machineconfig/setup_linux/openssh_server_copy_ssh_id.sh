
# allow ssh to remote linux without password
# if local machine is linux, then use: ssh-copy-id, else if it is windows:
sftp username@hostname  # put in password for once
# !!
mkdir .ssh
cd .ssh || exit
put ./.ssh/id_rsa.pub
exit  # sftp doesn't support cat command.
cat id_rsa.pub >> authorized_keys
