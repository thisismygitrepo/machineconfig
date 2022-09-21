#!/usr/bin/bash

# allow ssh to remote linux without password
# if local machine is linux, then use: ssh-copy-id, else if it is windows:
# type $env:USERPROFILE\.ssh\id_rsa.pub | ssh username@hostname "cat >> .ssh/authorized_keys"
sftp username@hostname  # put in password for once
# !!
mkdir .ssh
cd .ssh || exit
put ./.ssh/id_rsa.pub
exit  # sftp doesn't support cat command.
cat id_rsa.pub >> authorized_keys
