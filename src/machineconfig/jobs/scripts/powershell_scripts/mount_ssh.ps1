

winget install WinFsp.WinFsp --source winget --scope user --accept-package-agreements --accept-source-agreements; winget install SSHFS-Win.SSHFS-Win --source winget --scope user --accept-package-agreements --accept-source-agreements

$host = ''
$user = ''
$sharePath = ''
$driveLetter = ''

uv run --python 3.14 --with "machineconfig>=8.37" python -m machineconfig.scripts.python.mount_ssh

net use T: \\sshfs.kr\$user@$host.local
# this worked: net use T: \\sshfs\alex@alex-p51s-5.local
