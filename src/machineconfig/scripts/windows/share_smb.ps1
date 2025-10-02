

$Path = $HOME + '\data\share_smb'

Get-SmbShare

if (!(Test-Path -Path $Path)) {
    New-Item -ItemType Directory -Path $Path
}

# ICACLS $Path /grant $env:USERDOMAIN\$env:USERNAME:S

# provided access to all users irrespective of active directory
echo "Make sure you have elevated privledges to run this command"
New-SmbShare -Name "share_smb" -Path "$Path" FullAccess "Everyone"

