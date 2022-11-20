
$drive = Read-Host "DriveLetter (default D:)"

if ( $drive -eq "" )
{
    $drive = "D:"
}

$SecureString = ConvertTo-SecureString (cat ~/dotfiles/creds/data/bitlocker_pwd) -AsPlainText -Force
Unlock-BitLocker -MountPoint $drive -Password $SecureString
