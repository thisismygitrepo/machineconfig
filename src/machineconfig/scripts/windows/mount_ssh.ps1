

winget install WinFsp.WinFsp; winget install SSHFS-Win.SSHFS-Win

$host = ''
$user = ''
$sharePath = ''
$driveLetter = ''

# . activate_ve
. $HOME/code/machineconfig/.venv/Scripts/activate.ps1

python -m machineconfig.scripts.python.mount_ssh
. $HOME/tmp_results/shells/python_return_command.ps1

net use T: \\sshfs.kr\$user@$host.local
# this worked: net use T: \\sshfs\alex@alex-p51s-5.local
