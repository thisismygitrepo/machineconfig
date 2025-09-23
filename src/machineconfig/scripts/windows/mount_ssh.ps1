

winget install WinFsp.WinFsp; winget install SSHFS-Win.SSHFS-Win

$host = ''
$user = ''
$sharePath = ''
$driveLetter = ''

uv run --python 3.13 --no-dev --project $HOME/code/machineconfig python -m machineconfig.scripts.python.mount_ssh

net use T: \\sshfs.kr\$user@$host.local
# this worked: net use T: \\sshfs\alex@alex-p51s-5.local
