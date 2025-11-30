

from platform import system
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich import box
import subprocess
import os
import re

console = Console()


def ssh_debug_linux() -> dict[str, dict[str, str | bool]]:
    if system() != "Linux":
        console.print(Panel("❌ This function is only supported on Linux systems", title="[bold red]Error[/bold red]", border_style="red"))
        raise NotImplementedError("ssh_debug_linux is only supported on Linux")
    
    console.print(Panel("🔍 SSH DEBUG - COMPREHENSIVE DIAGNOSTICS", box=box.DOUBLE_EDGE, title_align="left"))
    
    results: dict[str, dict[str, str | bool]] = {}
    issues_found: list[str] = []
    ssh_dir = Path.home().joinpath(".ssh")
    authorized_keys = ssh_dir.joinpath("authorized_keys")
    home_dir = Path.home()
    current_user = os.environ.get("USER", os.environ.get("USERNAME", "unknown"))
    ssh_port = "22"
    
    file_checks: list[str] = []
    if not ssh_dir.exists():
        results["ssh_directory"] = {"status": "error", "message": "~/.ssh directory does not exist", "action": "Create with: mkdir -p ~/.ssh && chmod 700 ~/.ssh"}
        issues_found.append("SSH directory missing")
        file_checks.append("❌ ~/.ssh directory does not exist → mkdir -p ~/.ssh && chmod 700 ~/.ssh")
    else:
        ssh_dir_stat = os.stat(ssh_dir)
        ssh_dir_perms = oct(ssh_dir_stat.st_mode)[-3:]
        if ssh_dir_perms != "700":
            results["ssh_directory"] = {"status": "warning", "message": f"~/.ssh permissions: {ssh_dir_perms} (should be 700)", "action": "chmod 700 ~/.ssh"}
            issues_found.append(f"SSH directory permissions incorrect: {ssh_dir_perms}")
            file_checks.append(f"⚠️  ~/.ssh permissions: {ssh_dir_perms} (should be 700)")
        else:
            results["ssh_directory"] = {"status": "ok", "message": "~/.ssh permissions correct (700)", "action": ""}
            file_checks.append("✅ ~/.ssh directory permissions correct (700)")
    
    if not authorized_keys.exists():
        results["authorized_keys"] = {"status": "warning", "message": "authorized_keys does not exist", "action": "Add public keys"}
        issues_found.append("authorized_keys missing")
        file_checks.append("⚠️  authorized_keys file does not exist")
    else:
        ak_stat = os.stat(authorized_keys)
        ak_perms = oct(ak_stat.st_mode)[-3:]
        if ak_perms not in ["600", "644"]:
            results["authorized_keys"] = {"status": "warning", "message": f"authorized_keys permissions: {ak_perms} (should be 600 or 644)", "action": "chmod 644 ~/.ssh/authorized_keys"}
            issues_found.append(f"authorized_keys permissions incorrect: {ak_perms}")
            file_checks.append(f"⚠️  authorized_keys permissions: {ak_perms} (should be 600/644)")
        else:
            key_count = len([line for line in authorized_keys.read_text(encoding="utf-8").split("\n") if line.strip()])
            results["authorized_keys"] = {"status": "ok", "message": f"authorized_keys permissions correct ({ak_perms}), {key_count} key(s)", "action": ""}
            file_checks.append(f"✅ authorized_keys permissions correct ({ak_perms}), {key_count} key(s)")
    
    home_stat = os.stat(home_dir)
    home_perms = oct(home_stat.st_mode)[-3:]
    if home_perms[2] in ["7", "6"]:
        results["home_directory"] = {"status": "error", "message": f"Home directory world-writable: {home_perms}", "action": f"chmod 755 {home_dir}"}
        issues_found.append(f"Home directory world-writable: {home_perms}")
        file_checks.append(f"❌ Home directory world-writable ({home_perms}) → chmod 755 {home_dir}")
    else:
        results["home_directory"] = {"status": "ok", "message": f"Home directory permissions OK: {home_perms}", "action": ""}
        file_checks.append(f"✅ Home directory permissions OK ({home_perms})")
    
    console.print(Panel("\n".join(file_checks), title="[bold blue]🔐 File Permissions[/bold blue]", border_style="blue"))
    
    service_checks: list[str] = []
    try:
        ssh_service_check = subprocess.run(["systemctl", "is-active", "ssh"], capture_output=True, text=True, check=False)
        sshd_service_check = subprocess.run(["systemctl", "is-active", "sshd"], capture_output=True, text=True, check=False)
        ssh_active = ssh_service_check.returncode == 0
        sshd_active = sshd_service_check.returncode == 0
        if not ssh_active and not sshd_active:
            results["ssh_service"] = {"status": "error", "message": "SSH service is not running", "action": "sudo systemctl start ssh"}
            issues_found.append("SSH service not running")
            service_checks.append("❌ SSH service not running → sudo systemctl start ssh")
        else:
            service_name = "ssh" if ssh_active else "sshd"
            results["ssh_service"] = {"status": "ok", "message": f"SSH service running ({service_name})", "action": ""}
            service_checks.append(f"✅ SSH service is running ({service_name})")
    except FileNotFoundError:
        results["ssh_service"] = {"status": "warning", "message": "systemctl not found", "action": "Check manually"}
        service_checks.append("⚠️  systemctl not found, check SSH service manually")
    
    console.print(Panel("\n".join(service_checks), title="[bold blue]🔧 Service Status[/bold blue]", border_style="blue"))
    
    network_checks: list[str] = []
    ip_addresses: list[str] = []
    try:
        ip_addr_check = subprocess.run(["ip", "addr", "show"], capture_output=True, text=True, check=False)
        if ip_addr_check.returncode == 0:
            inet_pattern = re.compile(r'inet\s+(\d+\.\d+\.\d+\.\d+)/\d+.*scope\s+global')
            ip_addresses = inet_pattern.findall(ip_addr_check.stdout)
            if ip_addresses:
                results["network_interfaces"] = {"status": "ok", "message": f"Found {len(ip_addresses)} interface(s)", "action": ""}
                network_checks.append("✅ Network interfaces: " + ", ".join(ip_addresses))
            else:
                results["network_interfaces"] = {"status": "warning", "message": "No global IP addresses", "action": "Check network"}
                issues_found.append("No network IP addresses")
                network_checks.append("⚠️  No global IP addresses found")
    except FileNotFoundError:
        network_checks.append("⚠️  'ip' command not found")
    
    sshd_config_paths = [Path("/etc/ssh/sshd_config"), Path("/etc/sshd_config")]
    sshd_config = None
    for config_path in sshd_config_paths:
        if config_path.exists():
            sshd_config = config_path
            break
    
    config_info: list[str] = []
    if sshd_config:
        config_text = sshd_config.read_text(encoding="utf-8")
        port_lines = [line for line in config_text.split("\n") if line.strip().startswith("Port") and not line.strip().startswith("#")]
        if port_lines:
            ssh_port = port_lines[0].split()[1]
        results["sshd_config"] = {"status": "ok", "message": f"SSH port: {ssh_port}", "action": ""}
        config_info.append(f"✅ SSH port: {ssh_port}")
        
        password_auth_lines = [line for line in config_text.split("\n") if "PasswordAuthentication" in line and not line.strip().startswith("#")]
        if password_auth_lines:
            password_auth_enabled = "yes" in password_auth_lines[-1].lower()
            config_info.append(f"ℹ️  PasswordAuthentication: {'enabled' if password_auth_enabled else 'disabled'}")
        
        pubkey_auth_lines = [line for line in config_text.split("\n") if "PubkeyAuthentication" in line and not line.strip().startswith("#")]
        if pubkey_auth_lines:
            pubkey_auth_enabled = "yes" in pubkey_auth_lines[-1].lower()
            if not pubkey_auth_enabled:
                results["pubkey_auth"] = {"status": "error", "message": "PubkeyAuthentication disabled", "action": "Enable in sshd_config"}
                issues_found.append("PubkeyAuthentication disabled")
                config_info.append("❌ PubkeyAuthentication: disabled")
            else:
                results["pubkey_auth"] = {"status": "ok", "message": "PubkeyAuthentication enabled", "action": ""}
                config_info.append("✅ PubkeyAuthentication: enabled")
    else:
        results["sshd_config"] = {"status": "warning", "message": "sshd_config not found", "action": "Check SSH installation"}
        config_info.append("⚠️  sshd_config not found (assuming port 22)")
    
    try:
        listening_check = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True, check=False)
        if listening_check.returncode == 0:
            listening_output = listening_check.stdout
            if f":{ssh_port}" in listening_output:
                ssh_lines = [line for line in listening_output.split("\n") if f":{ssh_port}" in line]
                listening_on_all = any("0.0.0.0" in line or "[::]" in line for line in ssh_lines)
                listening_on_localhost_only = all("127.0.0.1" in line or "[::1]" in line for line in ssh_lines)
                if listening_on_localhost_only:
                    results["ssh_listening"] = {"status": "error", "message": "SSH listening on localhost only", "action": "Check ListenAddress in sshd_config"}
                    issues_found.append("SSH listening only on localhost")
                    network_checks.append(f"❌ SSH listening on localhost only (not reachable from network)")
                elif listening_on_all:
                    results["ssh_listening"] = {"status": "ok", "message": f"SSH listening on 0.0.0.0:{ssh_port}", "action": ""}
                    network_checks.append(f"✅ SSH listening on all interfaces (0.0.0.0:{ssh_port})")
                else:
                    results["ssh_listening"] = {"status": "ok", "message": f"SSH listening on port {ssh_port}", "action": ""}
                    network_checks.append(f"✅ SSH listening on port {ssh_port}")
            else:
                results["ssh_listening"] = {"status": "error", "message": f"SSH NOT listening on port {ssh_port}", "action": "Restart SSH service"}
                issues_found.append(f"SSH not listening on port {ssh_port}")
                network_checks.append(f"❌ SSH NOT listening on port {ssh_port}")
    except FileNotFoundError:
        network_checks.append("⚠️  'ss' command not found")
    
    firewall_checked = False
    try:
        ufw_status = subprocess.run(["ufw", "status"], capture_output=True, text=True, check=False)
        if ufw_status.returncode == 0:
            firewall_checked = True
            ufw_output = ufw_status.stdout
            if "Status: active" in ufw_output:
                if f"{ssh_port}/tcp" in ufw_output.lower() or f"{ssh_port}" in ufw_output.lower() or "ssh" in ufw_output.lower():
                    results["firewall_ufw"] = {"status": "ok", "message": f"UFW allows SSH on port {ssh_port}", "action": ""}
                    network_checks.append(f"✅ UFW firewall allows SSH")
                else:
                    results["firewall_ufw"] = {"status": "error", "message": f"UFW blocking port {ssh_port}", "action": f"sudo ufw allow {ssh_port}/tcp"}
                    issues_found.append(f"UFW blocking port {ssh_port}")
                    network_checks.append(f"❌ UFW blocking SSH → sudo ufw allow {ssh_port}/tcp")
            else:
                network_checks.append("ℹ️  UFW inactive")
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
                        results["firewall_firewalld"] = {"status": "ok", "message": "firewalld allows SSH", "action": ""}
                        network_checks.append("✅ firewalld allows SSH")
                    else:
                        results["firewall_firewalld"] = {"status": "error", "message": "firewalld blocking SSH", "action": "sudo firewall-cmd --permanent --add-service=ssh"}
                        issues_found.append("firewalld blocking SSH")
                        network_checks.append("❌ firewalld blocking SSH")
        except FileNotFoundError:
            pass
    
    if not firewall_checked:
        network_checks.append("ℹ️  No firewall detected")
    
    console.print(Panel("\n".join(network_checks + config_info), title="[bold blue]🌐 Network & Configuration[/bold blue]", border_style="blue"))
    
    other_checks: list[str] = []
    hosts_deny = Path("/etc/hosts.deny")
    if hosts_deny.exists():
        hosts_deny_content = hosts_deny.read_text(encoding="utf-8")
        active_lines = [line.strip() for line in hosts_deny_content.splitlines() if line.strip() and not line.strip().startswith("#")]
        active_content_lower = " ".join(active_lines).lower()
        if "sshd" in active_content_lower or "all" in active_content_lower:
            results["hosts_deny"] = {"status": "error", "message": "/etc/hosts.deny blocking SSH", "action": "Review /etc/hosts.deny"}
            issues_found.append("/etc/hosts.deny blocking SSH")
            other_checks.append("❌ /etc/hosts.deny may block SSH")
        else:
            other_checks.append("✅ /etc/hosts.deny doesn't block SSH")
    else:
        other_checks.append("✅ /etc/hosts.deny not present")
    
    try:
        selinux_check = subprocess.run(["getenforce"], capture_output=True, text=True, check=False)
        if selinux_check.returncode == 0:
            selinux_status = selinux_check.stdout.strip()
            if selinux_status == "Enforcing":
                other_checks.append(f"ℹ️  SELinux is Enforcing (run restorecon -Rv ~/.ssh if issues)")
            else:
                other_checks.append(f"ℹ️  SELinux is {selinux_status}")
    except FileNotFoundError:
        pass
    
    log_files = [Path("/var/log/auth.log"), Path("/var/log/secure")]
    log_found = False
    for log_file in log_files:
        if log_file.exists():
            log_found = True
            try:
                tail_check = subprocess.run(["tail", "-n", "30", str(log_file)], capture_output=True, text=True, check=False)
                if tail_check.returncode == 0:
                    error_keywords = ["error", "failed", "refused", "denied", "invalid"]
                    ssh_errors = [line for line in tail_check.stdout.split("\n") if any(kw in line.lower() for kw in error_keywords) and "ssh" in line.lower()]
                    if ssh_errors:
                        results["ssh_logs"] = {"status": "warning", "message": f"{len(ssh_errors)} SSH errors in log", "action": f"Review {log_file}"}
                        other_checks.append(f"⚠️  Found {len(ssh_errors)} SSH error(s) in {log_file.name}")
                    else:
                        other_checks.append(f"✅ No recent SSH errors in {log_file.name}")
            except Exception:
                other_checks.append(f"⚠️  Could not read {log_file}")
            break
    if not log_found:
        other_checks.append("⚠️  SSH log files not found (try journalctl -u ssh)")
    
    try:
        ssh_test = subprocess.run(["ssh", "-o", "ConnectTimeout=5", "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes", f"{current_user}@localhost", "echo", "test"], capture_output=True, text=True, check=False, timeout=10)
        if ssh_test.returncode == 0:
            results["local_ssh_test"] = {"status": "ok", "message": "Local SSH connection successful", "action": ""}
            other_checks.append("✅ Local SSH connection test passed")
        else:
            results["local_ssh_test"] = {"status": "warning", "message": "Local SSH test failed", "action": "Check keys/config"}
            other_checks.append("⚠️  Local SSH test failed (may need key setup)")
    except subprocess.TimeoutExpired:
        results["local_ssh_test"] = {"status": "error", "message": "SSH connection timed out", "action": "Check SSH service"}
        issues_found.append("SSH connection timeout")
        other_checks.append("❌ Local SSH connection timed out")
    except FileNotFoundError:
        other_checks.append("⚠️  SSH client not installed")
    except Exception:
        other_checks.append("⚠️  Could not test SSH connection")
    
    if other_checks:
        console.print(Panel("\n".join(other_checks), title="[bold blue]🧪 Additional Checks[/bold blue]", border_style="blue"))
    
    summary_lines: list[str] = []
    if issues_found:
        summary_lines.append(f"[bold yellow]⚠️  Found {len(issues_found)} issue(s):[/bold yellow]\n")
        for issue in issues_found:
            summary_lines.append(f"  • {issue}")
        summary_lines.append("\n[dim]Fix the issues above and run debug again.[/dim]")
    else:
        summary_lines.append("[bold green]✅ No critical issues detected[/bold green]\n")
        summary_lines.append("If you still cannot connect:")
        summary_lines.append("  • Check client-side configuration")
        summary_lines.append("  • Verify network connectivity")
        summary_lines.append("  • Ensure public key is in ~/.ssh/authorized_keys")
    
    hostname_result = subprocess.run(["hostname"], capture_output=True, text=True, check=False)
    hostname = hostname_result.stdout.strip() if hostname_result.returncode == 0 else "unknown"
    
    summary_lines.append(f"\n[bold cyan]🔗 Connection Info:[/bold cyan]")
    summary_lines.append(f"  👤 User: {current_user}  |  🖥️  Host: {hostname}  |  🔌 Port: {ssh_port}")
    if ip_addresses:
        summary_lines.append(f"\n  Connect via: ssh {current_user}@{ip_addresses[0]}")
        if len(ip_addresses) > 1:
            summary_lines.append(f"  [dim](also: {', '.join(ip_addresses[1:])})[/dim]")
    
    console.print(Panel("\n".join(summary_lines), title="[bold]📊 Summary[/bold]", border_style="cyan", box=box.DOUBLE_EDGE))
    
    return results


if __name__ == "__main__":
    ssh_debug_linux()
