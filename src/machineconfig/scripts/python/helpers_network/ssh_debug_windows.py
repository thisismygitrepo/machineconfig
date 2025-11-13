

from platform import system
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich import box
import subprocess
import os

console = Console()


def ssh_debug_windows() -> dict[str, dict[str, str | bool]]:
    """
    Comprehensive SSH debugging function that checks for common pitfalls on Windows systems.
    
    Returns a dictionary with diagnostic results for each check performed.
    """
    if system() != "Windows":
        console.print(Panel("❌ This function is only supported on Windows systems", title="[bold red]Error[/bold red]", border_style="red"))
        raise NotImplementedError("ssh_debug_windows is only supported on Windows")
    
    console.print(Panel("🔍 SSH DEBUG - COMPREHENSIVE DIAGNOSTICS (WINDOWS)", box=box.DOUBLE_EDGE, title_align="left"))
    
    results: dict[str, dict[str, str | bool]] = {}
    issues_found: list[str] = []
    
    ssh_dir = Path.home().joinpath(".ssh")
    authorized_keys = ssh_dir.joinpath("authorized_keys")
    
    console.print(Panel("🔐 Checking SSH directory and authorized_keys...", title="[bold blue]File Permissions[/bold blue]", border_style="blue"))
    
    if not ssh_dir.exists():
        results["ssh_directory"] = {"status": "error", "message": "~/.ssh directory does not exist", "action": "Create with: mkdir %USERPROFILE%\\.ssh"}
        issues_found.append("SSH directory missing")
        console.print(Panel("❌ ~/.ssh directory does not exist\n💡 Run: mkdir %USERPROFILE%\\.ssh", title="[bold red]Critical Issue[/bold red]", border_style="red"))
    else:
        results["ssh_directory"] = {"status": "ok", "message": "~/.ssh directory exists", "action": ""}
        console.print(Panel("✅ ~/.ssh directory exists", title="[bold green]OK[/bold green]", border_style="green"))
        
        try:
            icacls_check = subprocess.run(["icacls", str(ssh_dir)], capture_output=True, text=True, check=False)
            if icacls_check.returncode == 0:
                icacls_output = icacls_check.stdout
                if "BUILTIN\\Administrators:(OI)(CI)(F)" in icacls_output or "NT AUTHORITY\\SYSTEM:(OI)(CI)(F)" in icacls_output:
                    console.print(Panel(f"ℹ️  ~/.ssh permissions:\n{icacls_output[:300]}", title="[bold blue]Info[/bold blue]", border_style="blue"))
        except Exception:
            pass
    
    if not authorized_keys.exists():
        results["authorized_keys"] = {"status": "warning", "message": "authorized_keys file does not exist", "action": "Create authorized_keys file and add public keys"}
        issues_found.append("authorized_keys missing")
        console.print(Panel("⚠️  authorized_keys file does not exist\n💡 Add your public key to %USERPROFILE%\\.ssh\\authorized_keys", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    else:
        try:
            key_count = len([line for line in authorized_keys.read_text(encoding="utf-8").split("\n") if line.strip()])
            results["authorized_keys"] = {"status": "ok", "message": f"authorized_keys exists, contains {key_count} key(s)", "action": ""}
            console.print(Panel(f"✅ authorized_keys file exists\n🔑 Contains {key_count} authorized key(s)", title="[bold green]OK[/bold green]", border_style="green"))
            
            try:
                icacls_check = subprocess.run(["icacls", str(authorized_keys)], capture_output=True, text=True, check=False)
                if icacls_check.returncode == 0:
                    icacls_output = icacls_check.stdout
                    current_user = os.environ.get("USERNAME", "")
                    if f"{current_user}:(F)" in icacls_output or f"{current_user}:(M)" in icacls_output:
                        console.print(Panel(f"✅ authorized_keys permissions appear correct for user {current_user}", title="[bold green]OK[/bold green]", border_style="green"))
                    else:
                        console.print(Panel(f"⚠️  authorized_keys permissions may need adjustment\n💡 Run: icacls %USERPROFILE%\\.ssh\\authorized_keys /inheritance:r /grant \"{current_user}:F\"", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
            except Exception:
                pass
        except Exception as read_error:
            results["authorized_keys"] = {"status": "warning", "message": f"Could not read authorized_keys: {str(read_error)}", "action": "Check file encoding and permissions"}
            console.print(Panel(f"⚠️  Could not read authorized_keys: {str(read_error)}", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    
    console.print(Panel("🔧 Checking SSH service status...", title="[bold blue]Service Status[/bold blue]", border_style="blue"))
    
    try:
        ssh_service_check = subprocess.run(["powershell", "-Command", "Get-Service -Name sshd -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Status"], capture_output=True, text=True, check=False)
        
        if ssh_service_check.returncode == 0 and ssh_service_check.stdout.strip():
            service_status = ssh_service_check.stdout.strip()
            if service_status == "Running":
                results["ssh_service"] = {"status": "ok", "message": "SSH service (sshd) is running", "action": ""}
                console.print(Panel("✅ SSH service (sshd) is running", title="[bold green]OK[/bold green]", border_style="green"))
                
                startup_type_check = subprocess.run(["powershell", "-Command", "Get-Service -Name sshd | Select-Object -ExpandProperty StartType"], capture_output=True, text=True, check=False)
                if startup_type_check.returncode == 0:
                    startup_type = startup_type_check.stdout.strip()
                    if startup_type != "Automatic":
                        console.print(Panel(f"ℹ️  SSH service startup type: {startup_type}\n💡 To start automatically: Set-Service -Name sshd -StartupType Automatic", title="[bold blue]Info[/bold blue]", border_style="blue"))
            else:
                results["ssh_service"] = {"status": "error", "message": f"SSH service is {service_status}", "action": "Start with: Start-Service sshd"}
                issues_found.append(f"SSH service {service_status}")
                console.print(Panel(f"❌ SSH service is {service_status}\n💡 Start: Start-Service sshd\n💡 Enable on boot: Set-Service -Name sshd -StartupType Automatic", title="[bold red]Critical Issue[/bold red]", border_style="red"))
        else:
            results["ssh_service"] = {"status": "error", "message": "SSH service (sshd) not found", "action": "Install OpenSSH Server: Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0"}
            issues_found.append("SSH service not installed")
            console.print(Panel("❌ SSH service (sshd) not found\n💡 Install: Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0\n💡 Then start: Start-Service sshd", title="[bold red]Critical Issue[/bold red]", border_style="red"))
    except Exception as service_error:
        results["ssh_service"] = {"status": "warning", "message": f"Could not check service status: {str(service_error)}", "action": "Check SSH service manually"}
        console.print(Panel(f"⚠️  Could not check SSH service status: {str(service_error)}\n💡 Check manually: Get-Service sshd", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    
    console.print(Panel("🌐 Checking network interfaces and IP addresses...", title="[bold blue]Network Interfaces[/bold blue]", border_style="blue"))
    
    try:
        ip_addr_check = subprocess.run(["powershell", "-Command", "Get-NetIPAddress -AddressFamily IPv4 -PrefixOrigin Dhcp,Manual | Where-Object {$_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*'} | Select-Object -ExpandProperty IPAddress"], capture_output=True, text=True, check=False)
        if ip_addr_check.returncode == 0 and ip_addr_check.stdout.strip():
            ip_addresses = [ip.strip() for ip in ip_addr_check.stdout.strip().split("\n") if ip.strip()]
            
            if ip_addresses:
                results["network_interfaces"] = {"status": "ok", "message": f"Found {len(ip_addresses)} network interface(s)", "action": ""}
                console.print(Panel("✅ Network interfaces found:\n" + "\n".join([f"  • {ip}" for ip in ip_addresses]), title="[bold green]IP Addresses[/bold green]", border_style="green"))
            else:
                results["network_interfaces"] = {"status": "warning", "message": "No global IP addresses found", "action": "Check network configuration"}
                issues_found.append("No network IP addresses")
                console.print(Panel("⚠️  No global IP addresses found\n💡 This machine may not be reachable on the network\n💡 Check: Get-NetIPAddress", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
        else:
            results["network_interfaces"] = {"status": "warning", "message": "Could not retrieve IP addresses", "action": "Check network manually"}
            console.print(Panel("⚠️  Could not retrieve IP addresses\n💡 Check: ipconfig", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    except Exception:
        results["network_interfaces"] = {"status": "warning", "message": "Could not check network interfaces", "action": "Check network manually"}
        console.print(Panel("⚠️  Could not check network interfaces\n💡 Try: ipconfig", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    
    console.print(Panel("🔌 Checking SSH port and listening status...", title="[bold blue]Network Status[/bold blue]", border_style="blue"))
    
    sshd_config_paths = [Path("C:\\ProgramData\\ssh\\sshd_config"), Path(os.environ.get("PROGRAMDATA", "C:\\ProgramData")).joinpath("ssh", "sshd_config")]
    sshd_config = None
    for config_path in sshd_config_paths:
        if config_path.exists():
            sshd_config = config_path
            break
    
    ssh_port = "22"
    if sshd_config:
        try:
            config_text = sshd_config.read_text(encoding="utf-8")
            port_lines = [line for line in config_text.split("\n") if line.strip().startswith("Port") and not line.strip().startswith("#")]
            if port_lines:
                ssh_port = port_lines[0].split()[1]
            
            results["sshd_config"] = {"status": "ok", "message": f"SSH configured to listen on port {ssh_port}", "action": ""}
            console.print(Panel(f"✅ SSH configured to listen on port {ssh_port}", title="[bold green]Config[/bold green]", border_style="green"))
            
            password_auth_lines = [line for line in config_text.split("\n") if "PasswordAuthentication" in line and not line.strip().startswith("#")]
            if password_auth_lines:
                password_auth_enabled = "yes" in password_auth_lines[-1].lower()
                if not password_auth_enabled:
                    console.print(Panel("ℹ️  Password authentication is disabled\n💡 Only SSH keys will work", title="[bold blue]Info[/bold blue]", border_style="blue"))
            
            pubkey_auth_lines = [line for line in config_text.split("\n") if "PubkeyAuthentication" in line and not line.strip().startswith("#")]
            if pubkey_auth_lines:
                pubkey_auth_enabled = "yes" in pubkey_auth_lines[-1].lower()
                if not pubkey_auth_enabled:
                    results["pubkey_auth"] = {"status": "error", "message": "PubkeyAuthentication is disabled in sshd_config", "action": "Enable with: PubkeyAuthentication yes in sshd_config"}
                    issues_found.append("PubkeyAuthentication disabled")
                    console.print(Panel(f"❌ PubkeyAuthentication is DISABLED\n💡 Edit {sshd_config} and set: PubkeyAuthentication yes\n💡 Then restart: Restart-Service sshd", title="[bold red]Critical Issue[/bold red]", border_style="red"))
                else:
                    results["pubkey_auth"] = {"status": "ok", "message": "PubkeyAuthentication is enabled", "action": ""}
                    console.print(Panel("✅ PubkeyAuthentication is enabled", title="[bold green]OK[/bold green]", border_style="green"))
            
            authorized_keys_file_lines = [line for line in config_text.split("\n") if "AuthorizedKeysFile" in line and not line.strip().startswith("#")]
            if authorized_keys_file_lines:
                auth_keys_path = authorized_keys_file_lines[-1].split(None, 1)[1] if len(authorized_keys_file_lines[-1].split(None, 1)) > 1 else ".ssh/authorized_keys"
                console.print(Panel(f"ℹ️  AuthorizedKeysFile: {auth_keys_path}", title="[bold blue]Info[/bold blue]", border_style="blue"))
            
            admin_authorized_keys_lines = [line for line in config_text.split("\n") if "Match Group administrators" in line or "AuthorizedKeysFile __PROGRAMDATA__" in line]
            if admin_authorized_keys_lines:
                console.print(Panel("⚠️  IMPORTANT: Administrators group uses different authorized_keys location\n💡 For admin users, keys should be in: C:\\ProgramData\\ssh\\administrators_authorized_keys\n💡 Not in user's .ssh/authorized_keys!", title="[bold yellow]Admin Users[/bold yellow]", border_style="yellow"))
                
                programdata_auth_keys = Path(os.environ.get("PROGRAMDATA", "C:\\ProgramData")).joinpath("ssh", "administrators_authorized_keys")
                if programdata_auth_keys.exists():
                    console.print(Panel("✅ administrators_authorized_keys file exists", title="[bold green]OK[/bold green]", border_style="green"))
                else:
                    results["admin_authorized_keys"] = {"status": "warning", "message": "administrators_authorized_keys not found for admin users", "action": "Create C:\\ProgramData\\ssh\\administrators_authorized_keys"}
                    console.print(Panel("⚠️  administrators_authorized_keys not found\n💡 Create: C:\\ProgramData\\ssh\\administrators_authorized_keys\n💡 Set permissions: icacls C:\\ProgramData\\ssh\\administrators_authorized_keys /inheritance:r /grant SYSTEM:F /grant Administrators:F", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
        except Exception as config_error:
            results["sshd_config"] = {"status": "warning", "message": f"Could not read sshd_config: {str(config_error)}", "action": "Check SSH configuration manually"}
            console.print(Panel(f"⚠️  Could not read sshd_config: {str(config_error)}", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    else:
        results["sshd_config"] = {"status": "warning", "message": "sshd_config not found", "action": "Check SSH configuration manually"}
        console.print(Panel("⚠️  sshd_config not found\n💡 Check if OpenSSH Server is installed\n💡 Expected location: C:\\ProgramData\\ssh\\sshd_config", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    
    try:
        netstat_check = subprocess.run(["netstat", "-an"], capture_output=True, text=True, check=False)
        if netstat_check.returncode == 0:
            netstat_output = netstat_check.stdout
            if f":{ssh_port}" in netstat_output and "LISTENING" in netstat_output:
                ssh_lines = [line for line in netstat_output.split("\n") if f":{ssh_port}" in line and "LISTENING" in line]
                listening_on_all = any("0.0.0.0" in line or "[::]" in line for line in ssh_lines)
                listening_on_localhost_only = all("127.0.0.1" in line or "[::1]" in line for line in ssh_lines)
                
                if listening_on_localhost_only:
                    results["ssh_listening"] = {"status": "error", "message": f"SSH is listening ONLY on localhost (127.0.0.1:{ssh_port}), not accessible from network", "action": f"Edit {sshd_config}, check ListenAddress, restart SSH"}
                    issues_found.append("SSH listening only on localhost")
                    console.print(Panel(f"❌ SSH is listening ONLY on localhost (127.0.0.1:{ssh_port})\n💡 This prevents external connections!\n💡 Check sshd_config for 'ListenAddress'\n💡 Remove or comment out 'ListenAddress 127.0.0.1'\n💡 Or change to 'ListenAddress 0.0.0.0'\n💡 Then: Restart-Service sshd", title="[bold red]Critical Issue[/bold red]", border_style="red"))
                elif listening_on_all:
                    results["ssh_listening"] = {"status": "ok", "message": f"SSH is listening on all interfaces (0.0.0.0:{ssh_port})", "action": ""}
                    console.print(Panel(f"✅ SSH is listening on all interfaces (0.0.0.0:{ssh_port})\n✅ Should be accessible from network", title="[bold green]OK[/bold green]", border_style="green"))
                else:
                    results["ssh_listening"] = {"status": "ok", "message": f"SSH is listening on port {ssh_port}", "action": ""}
                    console.print(Panel(f"✅ SSH is listening on port {ssh_port}\n\nListening on:\n" + "\n".join([f"  {line.strip()}" for line in ssh_lines[:3]]), title="[bold green]OK[/bold green]", border_style="green"))
            else:
                results["ssh_listening"] = {"status": "error", "message": f"SSH is NOT listening on port {ssh_port}", "action": "Check if SSH service is running and configured correctly"}
                issues_found.append(f"SSH not listening on port {ssh_port}")
                console.print(Panel(f"❌ SSH is NOT listening on port {ssh_port}\n💡 Check: netstat -an | findstr :{ssh_port}\n💡 Restart: Restart-Service sshd", title="[bold red]Critical Issue[/bold red]", border_style="red"))
        else:
            results["ssh_listening"] = {"status": "warning", "message": "Could not check listening status", "action": "Check manually with: netstat -an"}
            console.print(Panel("⚠️  Could not check listening status\n💡 Check manually: netstat -an | findstr :22", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    except Exception:
        results["ssh_listening"] = {"status": "warning", "message": "Could not check listening status", "action": "Check manually"}
        console.print(Panel("⚠️  Could not check listening status\n💡 Try: netstat -an | findstr :22", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    
    console.print(Panel("🧱 Checking Windows Firewall status...", title="[bold blue]Firewall[/bold blue]", border_style="blue"))
    
    try:
        firewall_check = subprocess.run(["powershell", "-Command", "Get-NetFirewallRule -DisplayName '*SSH*' | Select-Object DisplayName, Enabled, Direction, Action"], capture_output=True, text=True, check=False)
        if firewall_check.returncode == 0 and firewall_check.stdout.strip():
            firewall_output = firewall_check.stdout
            ssh_rules_enabled = "True" in firewall_output and "Allow" in firewall_output
            
            if ssh_rules_enabled:
                results["firewall"] = {"status": "ok", "message": "Windows Firewall has SSH rules enabled", "action": ""}
                console.print(Panel("✅ Windows Firewall has SSH rules enabled\n\n" + firewall_output[:300], title="[bold green]OK[/bold green]", border_style="green"))
            else:
                results["firewall"] = {"status": "error", "message": "Windows Firewall may be blocking SSH", "action": "Add firewall rule: New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22"}
                issues_found.append("Firewall blocking SSH")
                console.print(Panel("❌ Windows Firewall may be blocking SSH\n💡 Add rule: New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22", title="[bold red]Critical Issue[/bold red]", border_style="red"))
        else:
            firewall_status_check = subprocess.run(["powershell", "-Command", "Get-NetFirewallProfile | Select-Object Name, Enabled"], capture_output=True, text=True, check=False)
            if firewall_status_check.returncode == 0:
                console.print(Panel("⚠️  No SSH-specific firewall rules found\n💡 Add rule: New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    except Exception:
        results["firewall"] = {"status": "warning", "message": "Could not check firewall status", "action": "Check manually"}
        console.print(Panel("⚠️  Could not check Windows Firewall\n💡 Check manually: Get-NetFirewallRule -DisplayName '*SSH*'", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    
    console.print(Panel("👥 Checking user account and admin status...", title="[bold blue]User Account[/bold blue]", border_style="blue"))
    
    try:
        current_user = os.environ.get("USERNAME", "unknown")
        admin_check = subprocess.run(["powershell", "-Command", "([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)"], capture_output=True, text=True, check=False)
        
        is_admin = "True" in admin_check.stdout if admin_check.returncode == 0 else False
        
        if is_admin:
            results["user_account"] = {"status": "warning", "message": f"Current user ({current_user}) is an Administrator", "action": "Check administrators_authorized_keys location"}
            console.print(Panel(f"⚠️  Current user ({current_user}) is an Administrator\n💡 Admin users may need keys in: C:\\ProgramData\\ssh\\administrators_authorized_keys\n💡 Not in %USERPROFILE%\\.ssh\\authorized_keys", title="[bold yellow]Important[/bold yellow]", border_style="yellow"))
        else:
            results["user_account"] = {"status": "ok", "message": f"Current user ({current_user}) is a standard user", "action": ""}
            console.print(Panel(f"✅ Current user ({current_user}) is a standard user\n💡 Keys should be in: %USERPROFILE%\\.ssh\\authorized_keys", title="[bold green]OK[/bold green]", border_style="green"))
    except Exception:
        results["user_account"] = {"status": "warning", "message": "Could not check user account status", "action": ""}
        console.print(Panel("⚠️  Could not check user account status", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    
    console.print(Panel("📋 Checking SSH logs for errors...", title="[bold blue]Logs[/bold blue]", border_style="blue"))
    
    try:
        log_check = subprocess.run(["powershell", "-Command", "Get-WinEvent -LogName 'OpenSSH/Admin' -MaxEvents 20 -ErrorAction SilentlyContinue | Where-Object {$_.LevelDisplayName -eq 'Error' -or $_.LevelDisplayName -eq 'Warning'} | Select-Object TimeCreated, LevelDisplayName, Message | Format-List"], capture_output=True, text=True, check=False)
        
        if log_check.returncode == 0 and log_check.stdout.strip():
            log_output = log_check.stdout
            results["ssh_logs"] = {"status": "warning", "message": "Found SSH errors/warnings in event log", "action": "Review event log"}
            console.print(Panel(f"⚠️  Found SSH errors/warnings:\n\n{log_output[:500]}", title="[bold yellow]Log Errors[/bold yellow]", border_style="yellow"))
        else:
            results["ssh_logs"] = {"status": "ok", "message": "No recent SSH errors in event log", "action": ""}
            console.print(Panel("✅ No recent SSH errors in event log", title="[bold green]OK[/bold green]", border_style="green"))
    except Exception:
        results["ssh_logs"] = {"status": "warning", "message": "Could not check SSH logs", "action": "Check manually: Get-WinEvent -LogName 'OpenSSH/Admin'"}
        console.print(Panel("⚠️  Could not check SSH logs\n💡 Check: Get-WinEvent -LogName 'OpenSSH/Admin' -MaxEvents 20", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    
    console.print(Panel("🧪 Testing local SSH connection...", title="[bold blue]Connection Test[/bold blue]", border_style="blue"))
    
    try:
        local_user = os.environ.get("USERNAME", "unknown")
        ssh_test = subprocess.run(["ssh", "-o", "ConnectTimeout=5", "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes", f"{local_user}@localhost", "echo", "test"], capture_output=True, text=True, check=False, timeout=10)
        
        if ssh_test.returncode == 0:
            results["local_ssh_test"] = {"status": "ok", "message": "Local SSH connection successful", "action": ""}
            console.print(Panel("✅ Local SSH connection works\n✅ SSH server is functional", title="[bold green]OK[/bold green]", border_style="green"))
        else:
            error_output = ssh_test.stderr
            results["local_ssh_test"] = {"status": "warning", "message": f"Local SSH test failed: {error_output[:100]}", "action": "Check SSH keys and configuration"}
            console.print(Panel(f"⚠️  Local SSH test failed\n💡 Error: {error_output[:200]}\n💡 This may be normal if key authentication is not set up for localhost", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    except subprocess.TimeoutExpired:
        results["local_ssh_test"] = {"status": "error", "message": "Local SSH connection timed out", "action": "SSH may be hanging or not responding"}
        issues_found.append("SSH connection timeout")
        console.print(Panel("❌ Local SSH connection timed out\n💡 SSH server may not be responding\n💡 Check: Get-Service sshd", title="[bold red]Critical Issue[/bold red]", border_style="red"))
    except FileNotFoundError:
        results["local_ssh_test"] = {"status": "warning", "message": "ssh client not found", "action": "Install SSH client: Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0"}
        console.print(Panel("⚠️  SSH client not installed\n💡 Install: Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    except Exception as test_error:
        results["local_ssh_test"] = {"status": "warning", "message": f"Could not test SSH: {str(test_error)}", "action": ""}
        console.print(Panel(f"⚠️  Could not test SSH connection: {str(test_error)}", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    
    console.print(Panel("📊 DIAGNOSTIC SUMMARY", box=box.DOUBLE_EDGE, title_align="left"))
    
    if issues_found:
        console.print(Panel(f"⚠️  Found {len(issues_found)} issue(s):\n\n" + "\n".join([f"• {issue}" for issue in issues_found]), title="[bold yellow]Issues Found[/bold yellow]", border_style="yellow"))
    else:
        console.print(Panel("✅ No critical issues detected\n\nIf you still cannot connect:\n• Check client-side configuration\n• Verify network connectivity\n• Ensure correct username and hostname\n• Check if public key is correctly added to authorized_keys\n• For admin users, check C:\\ProgramData\\ssh\\administrators_authorized_keys", title="[bold green]All Checks Passed[/bold green]", border_style="green"))
    
    console.print(Panel("🔗 CONNECTION INFORMATION", box=box.DOUBLE_EDGE, title_align="left"))
    
    try:
        current_user = os.environ.get("USERNAME", "unknown")
        hostname_result = subprocess.run(["hostname"], capture_output=True, text=True, check=False)
        hostname = hostname_result.stdout.strip() if hostname_result.returncode == 0 else "unknown"
        
        ip_addr_result = subprocess.run(["powershell", "-Command", "Get-NetIPAddress -AddressFamily IPv4 -PrefixOrigin Dhcp,Manual | Where-Object {$_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*'} | Select-Object -ExpandProperty IPAddress"], capture_output=True, text=True, check=False)
        connection_ips: list[str] = []
        if ip_addr_result.returncode == 0 and ip_addr_result.stdout.strip():
            connection_ips = [ip.strip() for ip in ip_addr_result.stdout.strip().split("\n") if ip.strip()]
        
        connection_info = f"👤 Username: {current_user}\n🖥️  Hostname: {hostname}\n🔌 SSH Port: {ssh_port}\n"
        
        if connection_ips:
            connection_info += "\n🌐 This machine can be accessed via SSH from other machines on the same network using:\n\n"
            for ip in connection_ips:
                connection_info += f"   ssh {current_user}@{ip}\n"
            if ssh_port != "22":
                connection_info += f"\n   (Port {ssh_port} should be used: ssh -p {ssh_port} {current_user}@<IP>)\n"
        else:
            connection_info += "\n⚠️  No network IP addresses found - this machine may not be reachable from the network"
        
        connection_info += "\n\n💡 From another machine on the same network, use one of the commands above"
        connection_info += "\n💡 Ensure your public key is in the correct authorized_keys location"
        connection_info += "\n💡 For admin users: C:\\ProgramData\\ssh\\administrators_authorized_keys"
        connection_info += "\n💡 For standard users: %USERPROFILE%\\.ssh\\authorized_keys"
        
        console.print(Panel(connection_info, title="[bold cyan]SSH Connection Details[/bold cyan]", border_style="cyan"))
    except Exception as conn_error:
        console.print(Panel(f"⚠️  Could not gather connection information: {str(conn_error)}", title="[bold yellow]Connection Info[/bold yellow]", border_style="yellow"))
    
    return results


if __name__ == "__main__":
    ssh_debug_windows()
