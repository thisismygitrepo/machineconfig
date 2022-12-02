
# on the side of the local machine, you need to sort out the following:
# if the $sshfile doesn't have a standard name, you will need to explicitly specify the identity while SSHing (e.g. ssh u@s -i ~/.ssh/my_id)
# However, this must be done every time. For permanent solutions, use .ssh/config

$sshfile = "$env:USERPROFILE\.ssh\id_rsa"

Set-Service ssh-agent -StartupType Manual  # allow the service to be started manually
ssh-agent  # start the service
ssh-add.exe $sshfile # add the key to the agent

