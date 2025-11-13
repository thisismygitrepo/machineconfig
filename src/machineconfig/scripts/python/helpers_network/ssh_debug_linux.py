

from platform import system
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich import box
import subprocess
import os

console = Console()


def ssh_debug_linux() -> dict[str, dict[str, str | bool]]:
    """
    Comprehensive SSH debugging function that checks for common pitfalls on Linux systems.
    
    Returns a dictionary with diagnostic results for each check performed.
    """
    if system() != "Linux":
        console.print(Panel("❌ This function is only supported on Linux systems", title="[bold red]Error[/bold red]", border_style="red"))
        raise NotImplementedError("ssh_debug_linux is only supported on Linux")
    
    console.print(Panel("🔍 SSH DEBUG - COMPREHENSIVE DIAGNOSTICS", box=box.DOUBLE_EDGE, title_align="left"))
    
    results: dict[str, dict[str, str | bool]] = {}
    issues_found: list[str] = []
    
    ssh_dir = Path.home().joinpath(".ssh")
    authorized_keys = ssh_dir.joinpath("authorized_keys")
    
    console.print(Panel("🔐 Checking SSH directory and authorized_keys...", title="[bold blue]File Permissions[/bold blue]", border_style="blue"))
    
    if not ssh_dir.exists():
        results["ssh_directory"] = {"status": "error", "message": "~/.ssh directory does not exist", "action": "Create with: mkdir -p ~/.ssh && chmod 700 ~/.ssh"}
        issues_found.append("SSH directory missing")
        console.print(Panel("❌ ~/.ssh directory does not exist\n💡 Run: mkdir -p ~/.ssh && chmod 700 ~/.ssh", title="[bold red]Critical Issue[/bold red]", border_style="red"))
    else:
        ssh_dir_stat = os.stat(ssh_dir)
        ssh_dir_perms = oct(ssh_dir_stat.st_mode)[-3:]
        if ssh_dir_perms != "700":
            results["ssh_directory"] = {"status": "warning", "message": f"~/.ssh has incorrect permissions: {ssh_dir_perms} (should be 700)", "action": "Fix with: chmod 700 ~/.ssh"}
            issues_found.append(f"SSH directory permissions incorrect: {ssh_dir_perms}")
            console.print(Panel(f"⚠️  ~/.ssh permissions: {ssh_dir_perms} (should be 700)\n💡 Fix: chmod 700 ~/.ssh", title="[bold yellow]Permission Issue[/bold yellow]", border_style="yellow"))
        else:
            results["ssh_directory"] = {"status": "ok", "message": "~/.ssh directory permissions correct (700)", "action": ""}
            console.print(Panel("✅ ~/.ssh directory permissions correct (700)", title="[bold green]OK[/bold green]", border_style="green"))
    
    if not authorized_keys.exists():
        results["authorized_keys"] = {"status": "warning", "message": "authorized_keys file does not exist", "action": "Create authorized_keys file and add public keys"}
        issues_found.append("authorized_keys missing")
        console.print(Panel("⚠️  authorized_keys file does not exist\n💡 Add your public key to ~/.ssh/authorized_keys", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    else:
        ak_stat = os.stat(authorized_keys)
        ak_perms = oct(ak_stat.st_mode)[-3:]
        if ak_perms not in ["600", "644"]:
            results["authorized_keys"] = {"status": "warning", "message": f"authorized_keys has incorrect permissions: {ak_perms} (should be 600 or 644)", "action": "Fix with: chmod 644 ~/.ssh/authorized_keys"}
            issues_found.append(f"authorized_keys permissions incorrect: {ak_perms}")
            console.print(Panel(f"⚠️  authorized_keys permissions: {ak_perms} (should be 600 or 644)\n💡 Fix: chmod 644 ~/.ssh/authorized_keys", title="[bold yellow]Permission Issue[/bold yellow]", border_style="yellow"))
        else:
            key_count = len([line for line in authorized_keys.read_text(encoding="utf-8").split("\n") if line.strip()])
            results["authorized_keys"] = {"status": "ok", "message": f"authorized_keys permissions correct ({ak_perms}), contains {key_count} key(s)", "action": ""}
            console.print(Panel(f"✅ authorized_keys permissions correct ({ak_perms})\n🔑 Contains {key_count} authorized key(s)", title="[bold green]OK[/bold green]", border_style="green"))
    
    console.print(Panel("🔧 Checking SSH service status...", title="[bold blue]Service Status[/bold blue]", border_style="blue"))
    
    try:
        ssh_service_check = subprocess.run(["systemctl", "is-active", "ssh"], capture_output=True, text=True, check=False)
        sshd_service_check = subprocess.run(["systemctl", "is-active", "sshd"], capture_output=True, text=True, check=False)
        
        ssh_active = ssh_service_check.returncode == 0
        sshd_active = sshd_service_check.returncode == 0
        
        if not ssh_active and not sshd_active:
            results["ssh_service"] = {"status": "error", "message": "SSH service is not running (checked both 'ssh' and 'sshd')", "action": "Start with: sudo systemctl start ssh (or sshd)"}
            issues_found.append("SSH service not running")
            console.print(Panel("❌ SSH service is not running\n💡 Start: sudo systemctl start ssh (or sshd)\n💡 Enable on boot: sudo systemctl enable ssh", title="[bold red]Critical Issue[/bold red]", border_style="red"))
        elif ssh_active or sshd_active:
            service_name = "ssh" if ssh_active else "sshd"
            results["ssh_service"] = {"status": "ok", "message": f"SSH service is running ({service_name})", "action": ""}
            console.print(Panel(f"✅ SSH service is running ({service_name})", title="[bold green]OK[/bold green]", border_style="green"))
    except FileNotFoundError:
        results["ssh_service"] = {"status": "warning", "message": "systemctl not found, cannot check service status", "action": "Check SSH service manually"}
        console.print(Panel("⚠️  systemctl not found\n💡 Check SSH service status manually", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    
    console.print(Panel("🌐 Checking network interfaces and IP addresses...", title="[bold blue]Network Interfaces[/bold blue]", border_style="blue"))
    
    try:
        ip_addr_check = subprocess.run(["ip", "addr", "show"], capture_output=True, text=True, check=False)
        if ip_addr_check.returncode == 0:
            ip_output = ip_addr_check.stdout
            import re
            inet_pattern = re.compile(r'inet\s+(\d+\.\d+\.\d+\.\d+)/\d+.*scope\s+global')
            ip_addresses = inet_pattern.findall(ip_output)
            
            if ip_addresses:
                results["network_interfaces"] = {"status": "ok", "message": f"Found {len(ip_addresses)} network interface(s)", "action": ""}
                console.print(Panel("✅ Network interfaces found:\n" + "\n".join([f"  • {ip}" for ip in ip_addresses]), title="[bold green]IP Addresses[/bold green]", border_style="green"))
            else:
                results["network_interfaces"] = {"status": "warning", "message": "No global IP addresses found", "action": "Check network configuration"}
                issues_found.append("No network IP addresses")
                console.print(Panel("⚠️  No global IP addresses found\n💡 This machine may not be reachable on the network\n💡 Check: ip addr show", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    except FileNotFoundError:
        results["network_interfaces"] = {"status": "warning", "message": "ip command not found", "action": "Check network manually"}
        console.print(Panel("⚠️  'ip' command not found\n💡 Try: ifconfig", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    
    console.print(Panel("🔌 Checking SSH port and listening status...", title="[bold blue]Network Status[/bold blue]", border_style="blue"))
    
    sshd_config_paths = [Path("/etc/ssh/sshd_config"), Path("/etc/sshd_config")]
    sshd_config = None
    for config_path in sshd_config_paths:
        if config_path.exists():
            sshd_config = config_path
            break
    
    if sshd_config:
        config_text = sshd_config.read_text(encoding="utf-8")
        port_lines = [line for line in config_text.split("\n") if line.strip().startswith("Port") and not line.strip().startswith("#")]
        if port_lines:
            ssh_port = port_lines[0].split()[1]
        else:
            ssh_port = "22"
        
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
                console.print(Panel("❌ PubkeyAuthentication is DISABLED\n💡 Edit /etc/ssh/sshd_config and set: PubkeyAuthentication yes\n💡 Then restart: sudo systemctl restart ssh", title="[bold red]Critical Issue[/bold red]", border_style="red"))
            else:
                results["pubkey_auth"] = {"status": "ok", "message": "PubkeyAuthentication is enabled", "action": ""}
                console.print(Panel("✅ PubkeyAuthentication is enabled", title="[bold green]OK[/bold green]", border_style="green"))
    else:
        results["sshd_config"] = {"status": "warning", "message": "sshd_config not found", "action": "Check SSH configuration manually"}
        ssh_port = "22"
        console.print(Panel("⚠️  sshd_config not found\n💡 Assuming default port 22", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    
    try:
        listening_check = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True, check=False)
        if listening_check.returncode == 0:
            listening_output = listening_check.stdout
            if f":{ssh_port}" in listening_output:
                ssh_lines = [line for line in listening_output.split("\n") if f":{ssh_port}" in line]
                listening_on_all = any("0.0.0.0" in line or "[::]" in line for line in ssh_lines)
                listening_on_localhost_only = all("127.0.0.1" in line or "[::1]" in line for line in ssh_lines)
                
                if listening_on_localhost_only:
                    results["ssh_listening"] = {"status": "error", "message": f"SSH is listening ONLY on localhost (127.0.0.1:{ssh_port}), not accessible from network", "action": "Edit /etc/ssh/sshd_config, check ListenAddress, restart SSH"}
                    issues_found.append("SSH listening only on localhost")
                    console.print(Panel(f"❌ SSH is listening ONLY on localhost (127.0.0.1:{ssh_port})\n💡 This prevents external connections!\n💡 Check /etc/ssh/sshd_config for 'ListenAddress'\n💡 Remove or comment out 'ListenAddress 127.0.0.1'\n💡 Or change to 'ListenAddress 0.0.0.0'\n💡 Then: sudo systemctl restart ssh", title="[bold red]Critical Issue[/bold red]", border_style="red"))
                elif listening_on_all:
                    results["ssh_listening"] = {"status": "ok", "message": f"SSH is listening on all interfaces (0.0.0.0:{ssh_port})", "action": ""}
                    console.print(Panel(f"✅ SSH is listening on all interfaces (0.0.0.0:{ssh_port})\n✅ Should be accessible from network", title="[bold green]OK[/bold green]", border_style="green"))
                else:
                    results["ssh_listening"] = {"status": "ok", "message": f"SSH is listening on port {ssh_port}", "action": ""}
                    console.print(Panel(f"✅ SSH is listening on port {ssh_port}\n\nListening on:\n" + "\n".join([f"  {line.strip()}" for line in ssh_lines[:3]]), title="[bold green]OK[/bold green]", border_style="green"))
            else:
                results["ssh_listening"] = {"status": "error", "message": f"SSH is NOT listening on port {ssh_port}", "action": "Check if SSH service is running and configured correctly"}
                issues_found.append(f"SSH not listening on port {ssh_port}")
                console.print(Panel(f"❌ SSH is NOT listening on port {ssh_port}\n💡 Check: sudo ss -tlnp | grep {ssh_port}\n💡 Restart: sudo systemctl restart ssh", title="[bold red]Critical Issue[/bold red]", border_style="red"))
        else:
            results["ssh_listening"] = {"status": "warning", "message": "Could not check listening status", "action": "Check manually with: ss -tlnp"}
            console.print(Panel("⚠️  Could not check listening status\n💡 Check manually: ss -tlnp | grep ssh", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    except FileNotFoundError:
        results["ssh_listening"] = {"status": "warning", "message": "ss command not found", "action": "Install net-tools or check manually"}
        console.print(Panel("⚠️  'ss' command not found\n💡 Try: netstat -tlnp | grep ssh", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    
    console.print(Panel("🧱 Checking firewall status...", title="[bold blue]Firewall[/bold blue]", border_style="blue"))
    
    firewall_checked = False
    
    try:
        ufw_status = subprocess.run(["ufw", "status"], capture_output=True, text=True, check=False)
        if ufw_status.returncode == 0:
            firewall_checked = True
            ufw_output = ufw_status.stdout
            if "Status: active" in ufw_output:
                if f"{ssh_port}/tcp" in ufw_output.lower() or f"{ssh_port}" in ufw_output.lower() or "ssh" in ufw_output.lower():
                    results["firewall_ufw"] = {"status": "ok", "message": f"UFW is active and SSH port {ssh_port} is allowed", "action": ""}
                    console.print(Panel(f"✅ UFW is active and SSH port {ssh_port} is allowed", title="[bold green]OK[/bold green]", border_style="green"))
                else:
                    results["firewall_ufw"] = {"status": "error", "message": f"UFW is active but SSH port {ssh_port} is NOT allowed", "action": f"Allow with: sudo ufw allow {ssh_port}/tcp"}
                    issues_found.append(f"UFW blocking port {ssh_port}")
                    console.print(Panel(f"❌ UFW is active but SSH port {ssh_port} is NOT allowed\n💡 Fix: sudo ufw allow {ssh_port}/tcp", title="[bold red]Critical Issue[/bold red]", border_style="red"))
            else:
                results["firewall_ufw"] = {"status": "ok", "message": "UFW is inactive", "action": ""}
                console.print(Panel("ℹ️  UFW is inactive (no firewall blocking)", title="[bold blue]Info[/bold blue]", border_style="blue"))
    except FileNotFoundError:
        pass
    
    if not firewall_checked:
        try:
            firewalld_status = subprocess.run(["firewall-cmd", "--state"], capture_output=True, text=True, check=False)
            if firewalld_status.returncode == 0 and "running" in firewalld_status.stdout.lower():
                firewall_checked = True
                firewalld_check = subprocess.run(["firewall-cmd", "--list-services"], capture_output=True, text=True, check=False)
                if firewalld_check.returncode == 0:
                    if "ssh" in firewalld_check.stdout.lower():
                        results["firewall_firewalld"] = {"status": "ok", "message": "firewalld is active and SSH service is allowed", "action": ""}
                        console.print(Panel("✅ firewalld is active and SSH service is allowed", title="[bold green]OK[/bold green]", border_style="green"))
                    else:
                        results["firewall_firewalld"] = {"status": "error", "message": "firewalld is active but SSH service is NOT allowed", "action": "Allow with: sudo firewall-cmd --permanent --add-service=ssh && sudo firewall-cmd --reload"}
                        issues_found.append("firewalld blocking SSH")
                        console.print(Panel("❌ firewalld is active but SSH is NOT allowed\n💡 Fix: sudo firewall-cmd --permanent --add-service=ssh\n💡 Then: sudo firewall-cmd --reload", title="[bold red]Critical Issue[/bold red]", border_style="red"))
        except FileNotFoundError:
            pass
    
    if not firewall_checked:
        try:
            iptables_check = subprocess.run(["iptables", "-L", "-n"], capture_output=True, text=True, check=False)
            if iptables_check.returncode == 0:
                firewall_checked = True
                iptables_output = iptables_check.stdout
                if f"dpt:{ssh_port}" in iptables_output or "ACCEPT" in iptables_output.split("\n")[0]:
                    results["firewall_iptables"] = {"status": "ok", "message": f"iptables appears to allow SSH traffic on port {ssh_port}", "action": ""}
                    console.print(Panel(f"ℹ️  iptables detected - appears to allow SSH on port {ssh_port}", title="[bold blue]Info[/bold blue]", border_style="blue"))
                else:
                    results["firewall_iptables"] = {"status": "warning", "message": f"iptables may be blocking SSH traffic on port {ssh_port}", "action": "Check rules manually: sudo iptables -L -n"}
                    console.print(Panel(f"⚠️  iptables detected - may be blocking SSH\n💡 Check: sudo iptables -L -n\n💡 Allow: sudo iptables -A INPUT -p tcp --dport {ssh_port} -j ACCEPT", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
        except FileNotFoundError:
            pass
    
    if not firewall_checked:
        results["firewall"] = {"status": "ok", "message": "No firewall detected or firewall commands not available", "action": ""}
        console.print(Panel("ℹ️  No firewall detected", title="[bold blue]Info[/bold blue]", border_style="blue"))
    
    console.print(Panel("🗂️  Checking for problematic files in /etc/...", title="[bold blue]System Files[/bold blue]", border_style="blue"))
    
    hosts_deny = Path("/etc/hosts.deny")
    if hosts_deny.exists():
        hosts_deny_content = hosts_deny.read_text(encoding="utf-8")
        active_lines = [line.strip() for line in hosts_deny_content.splitlines() if line.strip() and not line.strip().startswith("#")]
        active_content_lower = " ".join(active_lines).lower()
        if "sshd" in active_content_lower or "all" in active_content_lower:
            results["hosts_deny"] = {"status": "error", "message": "/etc/hosts.deny may be blocking SSH connections", "action": "Review /etc/hosts.deny and remove SSH blocks"}
            issues_found.append("/etc/hosts.deny blocking SSH")
            console.print(Panel("❌ /etc/hosts.deny may be blocking SSH\n💡 Check: cat /etc/hosts.deny\n💡 Remove any lines blocking 'sshd' or 'ALL'", title="[bold red]Critical Issue[/bold red]", border_style="red"))
        else:
            results["hosts_deny"] = {"status": "ok", "message": "/etc/hosts.deny exists but doesn't appear to block SSH", "action": ""}
            console.print(Panel("✅ /etc/hosts.deny doesn't block SSH", title="[bold green]OK[/bold green]", border_style="green"))
    else:
        results["hosts_deny"] = {"status": "ok", "message": "/etc/hosts.deny does not exist", "action": ""}
        console.print(Panel("✅ /etc/hosts.deny not present", title="[bold green]OK[/bold green]", border_style="green"))
    
    hosts_allow = Path("/etc/hosts.allow")
    if hosts_allow.exists():
        results["hosts_allow"] = {"status": "ok", "message": "/etc/hosts.allow exists (check if needed)", "action": ""}
        console.print(Panel("ℹ️  /etc/hosts.allow exists\n💡 Ensure it allows SSH if using TCP wrappers", title="[bold blue]Info[/bold blue]", border_style="blue"))
    
    console.print(Panel("👤 Checking home directory permissions...", title="[bold blue]User Permissions[/bold blue]", border_style="blue"))
    
    home_dir = Path.home()
    home_stat = os.stat(home_dir)
    home_perms = oct(home_stat.st_mode)[-3:]
    
    if home_perms[2] in ["7", "6"]:
        results["home_directory"] = {"status": "error", "message": f"Home directory has world-writable permissions: {home_perms} (SSH may refuse to work)", "action": f"Fix with: chmod 755 {home_dir}"}
        issues_found.append(f"Home directory world-writable: {home_perms}")
        console.print(Panel(f"❌ Home directory is world-writable ({home_perms})\n💡 SSH may refuse connections for security\n💡 Fix: chmod 755 {home_dir}", title="[bold red]Critical Issue[/bold red]", border_style="red"))
    else:
        results["home_directory"] = {"status": "ok", "message": f"Home directory permissions OK: {home_perms}", "action": ""}
        console.print(Panel(f"✅ Home directory permissions OK: {home_perms}", title="[bold green]OK[/bold green]", border_style="green"))
    
    console.print(Panel("🔍 Checking SELinux status...", title="[bold blue]SELinux[/bold blue]", border_style="blue"))
    
    try:
        selinux_check = subprocess.run(["getenforce"], capture_output=True, text=True, check=False)
        if selinux_check.returncode == 0:
            selinux_status = selinux_check.stdout.strip()
            if selinux_status == "Enforcing":
                restorecon_check = subprocess.run(["restorecon", "-Rv", str(ssh_dir)], capture_output=True, text=True, check=False)
                if restorecon_check.returncode == 0:
                    results["selinux"] = {"status": "ok", "message": f"SELinux is {selinux_status}, SSH contexts restored", "action": ""}
                    console.print(Panel(f"✅ SELinux is {selinux_status}\n✅ SSH contexts restored", title="[bold green]OK[/bold green]", border_style="green"))
                else:
                    results["selinux"] = {"status": "warning", "message": f"SELinux is {selinux_status}, may need context restoration", "action": f"Run: sudo restorecon -Rv {ssh_dir}"}
                    console.print(Panel(f"⚠️  SELinux is {selinux_status}\n💡 Fix contexts: sudo restorecon -Rv {ssh_dir}", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
            else:
                results["selinux"] = {"status": "ok", "message": f"SELinux is {selinux_status}", "action": ""}
                console.print(Panel(f"ℹ️  SELinux is {selinux_status}", title="[bold blue]Info[/bold blue]", border_style="blue"))
    except FileNotFoundError:
        results["selinux"] = {"status": "ok", "message": "SELinux not installed", "action": ""}
        console.print(Panel("ℹ️  SELinux not installed", title="[bold blue]Info[/bold blue]", border_style="blue"))
    
    console.print(Panel("📋 Checking SSH logs for errors...", title="[bold blue]Logs[/bold blue]", border_style="blue"))
    
    log_files = [Path("/var/log/auth.log"), Path("/var/log/secure")]
    log_found = False
    for log_file in log_files:
        if log_file.exists():
            log_found = True
            try:
                tail_check = subprocess.run(["tail", "-n", "50", str(log_file)], capture_output=True, text=True, check=False)
                if tail_check.returncode == 0:
                    log_content = tail_check.stdout
                    error_keywords = ["error", "failed", "refused", "denied", "invalid"]
                    ssh_errors = [line for line in log_content.split("\n") if any(keyword in line.lower() for keyword in error_keywords) and "ssh" in line.lower()]
                    if ssh_errors:
                        results["ssh_logs"] = {"status": "warning", "message": f"Found {len(ssh_errors)} potential SSH errors in {log_file}", "action": f"Review: sudo tail -f {log_file}"}
                        console.print(Panel(f"⚠️  Found {len(ssh_errors)} potential SSH errors in {log_file}\n💡 Review: sudo tail -f {log_file}\n\nRecent errors:\n" + "\n".join(ssh_errors[-3:]), title="[bold yellow]Log Errors[/bold yellow]", border_style="yellow"))
                    else:
                        results["ssh_logs"] = {"status": "ok", "message": f"No recent SSH errors in {log_file}", "action": ""}
                        console.print(Panel(f"✅ No recent SSH errors in {log_file}", title="[bold green]OK[/bold green]", border_style="green"))
            except Exception:
                results["ssh_logs"] = {"status": "warning", "message": f"Could not read {log_file}", "action": f"Check manually: sudo tail {log_file}"}
                console.print(Panel(f"⚠️  Could not read {log_file}\n💡 Check: sudo tail {log_file}", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
            break
    
    if not log_found:
        results["ssh_logs"] = {"status": "warning", "message": "SSH log files not found", "action": "Check journalctl: sudo journalctl -u ssh"}
        console.print(Panel("⚠️  SSH log files not found\n💡 Check: sudo journalctl -u ssh -n 50", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    
    console.print(Panel("🧪 Testing local SSH connection...", title="[bold blue]Connection Test[/bold blue]", border_style="blue"))
    
    try:
        local_user = os.environ.get("USER", os.environ.get("USERNAME", "unknown"))
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
        console.print(Panel("❌ Local SSH connection timed out\n💡 SSH server may not be responding\n💡 Check: sudo systemctl status ssh", title="[bold red]Critical Issue[/bold red]", border_style="red"))
    except FileNotFoundError:
        results["local_ssh_test"] = {"status": "warning", "message": "ssh client not found", "action": "Install SSH client"}
        console.print(Panel("⚠️  SSH client not installed\n💡 Install: sudo apt install openssh-client", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    except Exception as test_error:
        results["local_ssh_test"] = {"status": "warning", "message": f"Could not test SSH: {str(test_error)}", "action": ""}
        console.print(Panel(f"⚠️  Could not test SSH connection: {str(test_error)}", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
    
    console.print(Panel("📊 DIAGNOSTIC SUMMARY", box=box.DOUBLE_EDGE, title_align="left"))
    
    if issues_found:
        console.print(Panel(f"⚠️  Found {len(issues_found)} issue(s):\n\n" + "\n".join([f"• {issue}" for issue in issues_found]), title="[bold yellow]Issues Found[/bold yellow]", border_style="yellow"))
    else:
        console.print(Panel("✅ No critical issues detected\n\nIf you still cannot connect:\n• Check client-side configuration\n• Verify network connectivity\n• Ensure correct username and hostname\n• Check if public key is correctly added to authorized_keys", title="[bold green]All Checks Passed[/bold green]", border_style="green"))
    
    console.print(Panel("🔗 CONNECTION INFORMATION", box=box.DOUBLE_EDGE, title_align="left"))
    
    try:
        current_user = os.environ.get("USER", os.environ.get("USERNAME", "unknown"))
        hostname_result = subprocess.run(["hostname"], capture_output=True, text=True, check=False)
        hostname = hostname_result.stdout.strip() if hostname_result.returncode == 0 else "unknown"
        
        ip_addr_result = subprocess.run(["ip", "addr", "show"], capture_output=True, text=True, check=False)
        connection_ips: list[str] = []
        if ip_addr_result.returncode == 0:
            import re
            inet_pattern = re.compile(r'inet\s+(\d+\.\d+\.\d+\.\d+)/\d+.*scope\s+global')
            connection_ips = inet_pattern.findall(ip_addr_result.stdout)
        
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
        connection_info += "\n💡 Ensure your public key is in ~/.ssh/authorized_keys on this machine"
        connection_info += "\n💡 Or use password authentication if enabled in sshd_config"
        
        console.print(Panel(connection_info, title="[bold cyan]SSH Connection Details[/bold cyan]", border_style="cyan"))
    except Exception as conn_error:
        console.print(Panel(f"⚠️  Could not gather connection information: {str(conn_error)}", title="[bold yellow]Connection Info[/bold yellow]", border_style="yellow"))
    
    return results


if __name__ == "__main__":
    ssh_debug_linux()
