
# This is the Windows equivalent of copy-ssh-id on Linux.
# Just like the original function, it is a convenient way of doing two things in one go:
# 1- copy a certain public key to the remote machine.
#    scp ~/.ssh/id_rsa.pub $remote_user@$remote_host:~/.ssh/authorized_keys
# 2- Store the value on the remote in a file called .ssh/authorized_keys
#    ssh $remote_user@$remote_host "echo $public_key >> ~/.ssh/authorized_keys"
# Idea from: https://www.chrisjhart.com/Windows-10-ssh-copy-id/

$key_value = cat ($env:USERPROFILE + "\.ssh\id_rsa.pub")
ssh $args[0] "powershell.exe -Command type $key_value >> .ssh/authorized_keys"

$my_keys='https://github.com/thisismygitrepo.keys'
(Invoke-WebRequest $my_keys).Content >> .ssh/authorized_keys
