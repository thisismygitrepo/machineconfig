
# mount nfs share on windows
# Enable-WindowsOptionalFeature -FeatureName ServicesForNFS-ClientOnly, ClientForNFS-Infrastructure -Online -NoRestart
# New-PSDrive -Name "z" -Root "\\alex-p51s-5/home/alex/dbhdd" -Persist -PSProvider "FileSystem"
# notice there is not : separation between host and path
# mount.exe -o anon,nolock,rw,hard,intr,noatime,proto=tcp,no_root_squash alex-p51s-5:/home/alex/dbhdd X:


# Install NFS client
Write-Host "Installing NFS client..."
# this is for windows server: Install-WindowsFeature ClientForNFS-Infrastructure -IncludeManagementTools
Enable-WindowsOptionalFeature -FeatureName ServicesForNFS-ClientOnly, ClientForNFS-Infrastructure -Online -NoRestart
Write-Host "NFS client installed successfully."

$server=''
$sharePath=''
$driveLetter=''
$options = "rw,sec=sys,no_subtree_check"

# . activate_ve
. $HOME/code/machineconfig/.venv/Scripts/activate.ps1

python -m machineconfig.scripts.python.mount_nfs
. $HOME/tmp_results/shells/python_return_command.ps1

# Configure NFS server
#Write-Host "Configuring NFS server..."
#$nfsServerCommand = "exportfs -o $options $sharePath"
#Write-Host "Running command: $nfsServerCommand"
#Invoke-Expression $nfsServerCommand
#Write-Host "NFS server configured successfully."

$mountCommand = "mount.exe $server" + ":$sharePath $driveLetter" # + " -o rw,hard,intr,noatime,proto=tcp,no_root_squash"
#.exe is crucial, mount is nothing but alias for New-PSDrive
# New-PSDrive -Name "Y" -Root "\\host/path" -Persist -PSProvider "FileSystem" -Credential $cred
# see this: https://superuser.com/questions/1677820/powershell-mount-nfs-with-options

Write-Host "Mounting NFS share..."
Write-Host "Running command: $mountCommand"
Invoke-Expression $mountCommand
# create symlink to the mounted drive from ~/data/mount_nfs/{remote_server}
Write-Host "Executing this following command: New-Item -ItemType SymbolicLink -Path $HOME/data/mount_nfs/$server -Target $driveLetter -Force"
New-Item -ItemType SymbolicLink -Path "$HOME/data/mount_nfs/$server" -Target "$driveLetter" -Force
Write-Host "NFS share mounted successfully."
