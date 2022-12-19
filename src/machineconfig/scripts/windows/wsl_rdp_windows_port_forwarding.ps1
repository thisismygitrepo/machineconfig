

$port_num = 3391
wsl.exe -u root service xrdp start  # added by me, to ensure sshd is fired.
wsl.exe -u root service xrdp status
# If elevation needed, start new process
If (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))
{
  # Relaunch as an elevated process:
  Start-Process powershell.exe "-File",('"{0}"' -f $MyInvocation.MyCommand.Path),"$Args runas" -Verb RunAs
  exit
}


# Check WSL ip address
wsl hostname -I | Set-Variable -Name "WSL"
$found = $WSL -match '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}';
if (-not $found) {
  echo "WSL2 cannot be found. Terminate script.";
  exit;
}


# Remove and Create NetFireWallRule
Remove-NetFireWallRule -DisplayName 'WSL 2 Firewall Unlock';
if ($Args[0] -ne "delete") {
  New-NetFirewallRule -DisplayName 'WSL 2 Firewall Unlock2' -Direction Outbound -LocalPort ($port_num) -Action Allow -Protocol TCP;
  New-NetFirewallRule -DisplayName 'WSL 2 Firewall Unlock2' -Direction Inbound -LocalPort ($port_num) -Action Allow -Protocol TCP;
}

# Add each port into portproxy
$Addr = "0.0.0.0"
iex "netsh interface portproxy delete v4tov4 listenaddress=$Addr listenport=$port_num | Out-Null";
if ($Args[0] -ne "delete") {
    iex "netsh interface portproxy add v4tov4 listenaddress=$Addr listenport=$port_num connectaddress=$WSL connectport=$port_num | Out-Null";
}


# Display all portproxy information
netsh interface portproxy show v4tov4;

# Give user to chance to see above list when relaunched start
If ($Args[0] -eq "runas" -Or $Args[1] -eq "runas") {
  Write-Host -NoNewLine 'Press any key to close! ';
  $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown');
}
