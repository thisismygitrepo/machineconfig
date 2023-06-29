
# mount nfs share on windows
# Enable-WindowsOptionalFeature -FeatureName ServicesForNFS-ClientOnly, ClientForNFS-Infrastructure -Online -NoRestart
# New-PSDrive -Name "z" -Root "\\alex-p51s-5/home/alex/dbhdd" -Persist -PSProvider "FileSystem"
# notice there is not : separation between host and path
# mount.exe -o anon,nolock,rw,hard,intr,noatime,proto=tcp,no_root_squash alex-p51s-5:/home/alex/dbhdd X:


# Install NFS client
Write-Host "Installing NFS client..."
Install-WindowsFeature ClientForNFS-Infrastructure -IncludeManagementTools
Write-Host "NFS client installed successfully."

# Prompt user for NFS server details
$server = Read-Host "Enter the IP address or hostname of the NFS server (e.g. 192.168.1.100 or nfs.example.com)"
if ([string]::IsNullOrWhiteSpace($server)) {
    Write-Warning "No input received. Using default IP address of 192.168.1.100."
    $server = "192.168.1.100"
}
$sharePath = Read-Host "Enter the path to the shared directory on the NFS server (e.g. /exports/share)"
if ([string]::IsNullOrWhiteSpace($sharePath)) {
    Write-Warning "No input received. Using default path of /exports/share."
    $sharePath = "/exports/share"
}
$options = Read-Host "Enter any NFS share options (e.g. rw,sec=sys,no_subtree_check)"
if ([string]::IsNullOrWhiteSpace($options)) {
    Write-Warning "No input received. Using default options of rw,sec=sys,no_subtree_check."
    $options = "rw,sec=sys,no_subtree_check"
}

# Configure NFS server
Write-Host "Configuring NFS server..."
$nfsServerCommand = "exportfs -o $options $sharePath"
Write-Host "Running command: $nfsServerCommand"
Invoke-Expression $nfsServerCommand
Write-Host "NFS server configured successfully."

# Mount NFS share
$driveLetter = Read-Host "Enter a drive letter to use for the NFS share (e.g. Z)"
if ([string]::IsNullOrWhiteSpace($driveLetter)) {
    Write-Warning "No input received. Using default drive letter of Z."
    $driveLetter = "Z"
}

$mountCommand = "mount.exe $server" + ":$sharePath $driveLetter" + " -o rw,hard,intr,noatime,proto=tcp,no_root_squash"
#.exe is crucial, mount is nothing but alias for New-PSDrive
# New-PSDrive -Name "Y" -Root "\\host/path" -Persist -PSProvider "FileSystem" -Credential $cred
# see this: https://superuser.com/questions/1677820/powershell-mount-nfs-with-options

Write-Host "Mounting NFS share..."
Write-Host "Running command: $mountCommand"
Invoke-Expression $mountCommand
Write-Host "NFS share mounted successfully."
