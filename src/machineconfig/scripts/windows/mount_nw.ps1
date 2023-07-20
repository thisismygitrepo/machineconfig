
# mapping a network drive
# read share name by asking for it
$share_info = Read-Host -Prompt "Enter share info (e.g. \\SAH0229234\t7share) "
$username = Read-Host -Prompt "Enter username (e.g. alex) "
$cred = Get-Credential -Credential "$username"
Write-Host "Executing: New-PSDrive -Name Z -PSProvider FileSystem -Root $share_info -Persist -Credential $cred"
New-PSDrive -Name "Z" -PSProvider "FileSystem" -Root $share_info -Persist -Credential $cred

