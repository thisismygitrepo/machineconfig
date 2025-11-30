

from platform import system
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich import box
import subprocess
import os

console = Console()


def detect_openssh_installation() -> tuple[str, Path | None, Path | None]:
    """Detect OpenSSH installation type and paths.
    Returns: (install_type, sshd_exe_path, config_dir)
    install_type: 'capability' | 'winget' | 'not_found'
    """
    capability_sshd = Path("C:/Windows/System32/OpenSSH/sshd.exe")
    capability_config = Path("C:/ProgramData/ssh")
    winget_sshd = Path("C:/Program Files/OpenSSH/sshd.exe")
    winget_config = Path("C:/Program Files/OpenSSH")
    if capability_sshd.exists():
        return ("capability", capability_sshd, capability_config)
    if winget_sshd.exists():
        return ("winget", winget_sshd, winget_config)
    return ("not_found", None, None)


def ssh_debug_windows() -> dict[str, dict[str, str | bool]]:
    if system() != "Windows":
        console.print(Panel("❌ This function is only supported on Windows systems", title="[bold red]Error[/bold red]", border_style="red"))
        raise NotImplementedError("ssh_debug_windows is only supported on Windows")
    
    console.print(Panel("🔍 SSH DEBUG - COMPREHENSIVE DIAGNOSTICS (WINDOWS)", box=box.DOUBLE_EDGE, title_align="left"))
    
    results: dict[str, dict[str, str | bool]] = {}
    issues_found: list[str] = []
    ssh_dir = Path.home().joinpath(".ssh")
    authorized_keys = ssh_dir.joinpath("authorized_keys")
    current_user = os.environ.get("USERNAME", "unknown")
    ssh_port = "22"
    
    install_type, sshd_exe_path, config_dir = detect_openssh_installation()
    
    install_checks: list[str] = []
    if install_type == "capability":
        results["installation"] = {"status": "ok", "message": "OpenSSH installed via Windows Capability", "action": ""}
        install_checks.append("✅ OpenSSH installed via Windows Capability (Add-WindowsCapability)")
        install_checks.append(f"   Executable: {sshd_exe_path}")
        install_checks.append(f"   Config dir: {config_dir}")
    elif install_type == "winget":
        results["installation"] = {"status": "ok", "message": "OpenSSH installed via winget/standalone", "action": ""}
        install_checks.append("✅ OpenSSH installed via winget/standalone package")
        install_checks.append(f"   Executable: {sshd_exe_path}")
        install_checks.append(f"   Config dir: {config_dir}")
    else:
        results["installation"] = {"status": "error", "message": "OpenSSH Server not found", "action": "Install via: Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 OR winget install Microsoft.OpenSSH.Beta"}
        install_checks.append("❌ OpenSSH Server not found")
        install_checks.append("   Install via: Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0")
        install_checks.append("   Or via: winget install Microsoft.OpenSSH.Beta")
        issues_found.append("OpenSSH Server not installed")
    console.print(Panel("\n".join(install_checks), title="[bold blue]📦 Installation[/bold blue]", border_style="blue"))
    
    file_checks: list[str] = []
    if not ssh_dir.exists():
        results["ssh_directory"] = {"status": "error", "message": "~/.ssh directory does not exist", "action": "Create with: mkdir %USERPROFILE%\\.ssh"}
        issues_found.append("SSH directory missing")
        file_checks.append("❌ ~/.ssh directory does not exist → mkdir %USERPROFILE%\\.ssh")
    else:
        results["ssh_directory"] = {"status": "ok", "message": "~/.ssh directory exists", "action": ""}
        file_checks.append("✅ ~/.ssh directory exists")
    
    if not authorized_keys.exists():
        results["authorized_keys"] = {"status": "warning", "message": "authorized_keys file does not exist", "action": "Create authorized_keys file and add public keys"}
        issues_found.append("authorized_keys missing")
        file_checks.append("⚠️  authorized_keys file does not exist")
    else:
        try:
            key_count = len([line for line in authorized_keys.read_text(encoding="utf-8").split("\n") if line.strip()])
            results["authorized_keys"] = {"status": "ok", "message": f"authorized_keys exists, contains {key_count} key(s)", "action": ""}
            file_checks.append(f"✅ authorized_keys file exists ({key_count} key(s))")
            try:
                icacls_check = subprocess.run(["icacls", str(authorized_keys)], capture_output=True, text=True, check=False)
                if icacls_check.returncode == 0:
                    icacls_output = icacls_check.stdout
                    if f"{current_user}:(F)" in icacls_output or f"{current_user}:(M)" in icacls_output:
                        file_checks.append(f"✅ authorized_keys permissions correct for {current_user}")
                    else:
                        file_checks.append("⚠️  authorized_keys permissions may need adjustment")
            except Exception:
                pass
        except Exception as read_error:
            results["authorized_keys"] = {"status": "warning", "message": f"Could not read authorized_keys: {str(read_error)}", "action": "Check file encoding and permissions"}
            file_checks.append(f"⚠️  Could not read authorized_keys: {read_error}")
    
    console.print(Panel("\n".join(file_checks), title="[bold blue]🔐 File Permissions[/bold blue]", border_style="blue"))
    
    service_checks: list[str] = []
    try:
        ssh_service_check = subprocess.run(["powershell", "-Command", "Get-Service -Name sshd -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Status"], capture_output=True, text=True, check=False)
        if ssh_service_check.returncode == 0 and ssh_service_check.stdout.strip():
            service_status = ssh_service_check.stdout.strip()
            if service_status == "Running":
                results["ssh_service"] = {"status": "ok", "message": "SSH service (sshd) is running", "action": ""}
                service_checks.append("✅ SSH service (sshd) is running")
                startup_type_check = subprocess.run(["powershell", "-Command", "Get-Service -Name sshd | Select-Object -ExpandProperty StartType"], capture_output=True, text=True, check=False)
                if startup_type_check.returncode == 0:
                    startup_type = startup_type_check.stdout.strip()
                    if startup_type != "Automatic":
                        service_checks.append(f"ℹ️  Startup type: {startup_type} (not automatic)")
            else:
                results["ssh_service"] = {"status": "error", "message": f"SSH service is {service_status}", "action": "Start with: Start-Service sshd"}
                issues_found.append(f"SSH service {service_status}")
                service_checks.append(f"❌ SSH service is {service_status} → Start-Service sshd")
        else:
            results["ssh_service"] = {"status": "error", "message": "SSH service (sshd) not found", "action": "Install OpenSSH Server"}
            issues_found.append("SSH service not installed")
            service_checks.append("❌ SSH service (sshd) not found → Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0")
    except Exception as service_error:
        results["ssh_service"] = {"status": "warning", "message": f"Could not check service status: {str(service_error)}", "action": "Check SSH service manually"}
        service_checks.append(f"⚠️  Could not check service: {service_error}")
    
    console.print(Panel("\n".join(service_checks), title="[bold blue]🔧 Service Status[/bold blue]", border_style="blue"))
    
    network_checks: list[str] = []
    ip_addresses: list[str] = []
    try:
        ip_addr_check = subprocess.run(["powershell", "-Command", "Get-NetIPAddress -AddressFamily IPv4 -PrefixOrigin Dhcp,Manual | Where-Object {$_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*'} | Select-Object -ExpandProperty IPAddress"], capture_output=True, text=True, check=False)
        if ip_addr_check.returncode == 0 and ip_addr_check.stdout.strip():
            ip_addresses = [ip.strip() for ip in ip_addr_check.stdout.strip().split("\n") if ip.strip()]
            if ip_addresses:
                results["network_interfaces"] = {"status": "ok", "message": f"Found {len(ip_addresses)} network interface(s)", "action": ""}
                network_checks.append("✅ Network interfaces: " + ", ".join(ip_addresses))
            else:
                results["network_interfaces"] = {"status": "warning", "message": "No global IP addresses found", "action": "Check network configuration"}
                issues_found.append("No network IP addresses")
                network_checks.append("⚠️  No global IP addresses found")
    except Exception:
        results["network_interfaces"] = {"status": "warning", "message": "Could not check network interfaces", "action": "Check network manually"}
        network_checks.append("⚠️  Could not check network interfaces")
    
    sshd_config: Path | None = None
    if config_dir is not None:
        sshd_config = config_dir.joinpath("sshd_config")
        if not sshd_config.exists():
            sshd_config = None
    if sshd_config is None:
        sshd_config_paths = [Path("C:/ProgramData/ssh/sshd_config"), Path("C:/Program Files/OpenSSH/sshd_config")]
        for config_path in sshd_config_paths:
            if config_path.exists():
                sshd_config = config_path
                break
    
    config_info: list[str] = []
    if sshd_config:
        try:
            config_text = sshd_config.read_text(encoding="utf-8")
            port_lines = [line for line in config_text.split("\n") if line.strip().startswith("Port") and not line.strip().startswith("#")]
            if port_lines:
                ssh_port = port_lines[0].split()[1]
            results["sshd_config"] = {"status": "ok", "message": f"SSH configured to listen on port {ssh_port}", "action": ""}
            config_info.append(f"✅ SSH port: {ssh_port}")
            
            password_auth_lines = [line for line in config_text.split("\n") if "PasswordAuthentication" in line and not line.strip().startswith("#")]
            if password_auth_lines:
                password_auth_enabled = "yes" in password_auth_lines[-1].lower()
                config_info.append(f"ℹ️  PasswordAuthentication: {'enabled' if password_auth_enabled else 'disabled'}")
            
            pubkey_auth_lines = [line for line in config_text.split("\n") if "PubkeyAuthentication" in line and not line.strip().startswith("#")]
            if pubkey_auth_lines:
                pubkey_auth_enabled = "yes" in pubkey_auth_lines[-1].lower()
                if not pubkey_auth_enabled:
                    results["pubkey_auth"] = {"status": "error", "message": "PubkeyAuthentication is disabled", "action": "Enable in sshd_config"}
                    issues_found.append("PubkeyAuthentication disabled")
                    config_info.append("❌ PubkeyAuthentication: disabled")
                else:
                    results["pubkey_auth"] = {"status": "ok", "message": "PubkeyAuthentication is enabled", "action": ""}
                    config_info.append("✅ PubkeyAuthentication: enabled")
            
            admin_lines = [line for line in config_text.split("\n") if "Match Group administrators" in line or "AuthorizedKeysFile __PROGRAMDATA__" in line]
            if admin_lines:
                admin_keys_dir = Path("C:/ProgramData/ssh")
                admin_auth_keys = admin_keys_dir.joinpath("administrators_authorized_keys")
                if admin_auth_keys.exists():
                    config_info.append(f"✅ administrators_authorized_keys exists at {admin_auth_keys}")
                else:
                    results["admin_authorized_keys"] = {"status": "warning", "message": "administrators_authorized_keys not found", "action": f"Create at {admin_auth_keys}"}
                    config_info.append(f"⚠️  Admin users need keys in {admin_auth_keys}")
        except Exception as config_error:
            results["sshd_config"] = {"status": "warning", "message": f"Could not read sshd_config: {str(config_error)}", "action": "Check manually"}
            config_info.append("⚠️  Could not read sshd_config")
    else:
        results["sshd_config"] = {"status": "warning", "message": "sshd_config not found", "action": "Check SSH installation"}
        config_info.append("⚠️  sshd_config not found")
    
    try:
        netstat_check = subprocess.run(["netstat", "-an"], capture_output=True, text=True, check=False)
        if netstat_check.returncode == 0:
            netstat_output = netstat_check.stdout
            if f":{ssh_port}" in netstat_output and "LISTENING" in netstat_output:
                ssh_lines = [line for line in netstat_output.split("\n") if f":{ssh_port}" in line and "LISTENING" in line]
                listening_on_all = any("0.0.0.0" in line or "[::]" in line for line in ssh_lines)
                listening_on_localhost_only = all("127.0.0.1" in line or "[::1]" in line for line in ssh_lines)
                if listening_on_localhost_only:
                    results["ssh_listening"] = {"status": "error", "message": "SSH listening ONLY on localhost", "action": "Check ListenAddress in sshd_config"}
                    issues_found.append("SSH listening only on localhost")
                    network_checks.append("❌ SSH listening on localhost only (not reachable from network)")
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
    except Exception:
        network_checks.append("⚠️  Could not check listening status")
    
    try:
        firewall_check = subprocess.run(["powershell", "-Command", "Get-NetFirewallRule -DisplayName '*SSH*' | Select-Object DisplayName, Enabled, Action"], capture_output=True, text=True, check=False)
        if firewall_check.returncode == 0 and firewall_check.stdout.strip():
            ssh_rules_enabled = "True" in firewall_check.stdout and "Allow" in firewall_check.stdout
            if ssh_rules_enabled:
                results["firewall"] = {"status": "ok", "message": "Firewall allows SSH", "action": ""}
                network_checks.append("✅ Windows Firewall allows SSH")
            else:
                results["firewall"] = {"status": "error", "message": "Firewall may block SSH", "action": "Add firewall rule"}
                issues_found.append("Firewall blocking SSH")
                network_checks.append("❌ Windows Firewall may block SSH")
        else:
            network_checks.append("⚠️  No SSH firewall rules found")
    except Exception:
        network_checks.append("⚠️  Could not check firewall")
    
    console.print(Panel("\n".join(network_checks + config_info), title="[bold blue]🌐 Network & Configuration[/bold blue]", border_style="blue"))
    
    other_checks: list[str] = []
    try:
        admin_check = subprocess.run(["powershell", "-Command", "([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)"], capture_output=True, text=True, check=False)
        is_admin = "True" in admin_check.stdout if admin_check.returncode == 0 else False
        if is_admin:
            results["user_account"] = {"status": "warning", "message": f"{current_user} is an Administrator", "action": "Use administrators_authorized_keys"}
            other_checks.append(f"⚠️  {current_user} is an Administrator (use C:\\ProgramData\\ssh\\administrators_authorized_keys)")
        else:
            results["user_account"] = {"status": "ok", "message": f"{current_user} is a standard user", "action": ""}
            other_checks.append(f"✅ {current_user} is a standard user")
    except Exception:
        other_checks.append("⚠️  Could not check user account")
    
    try:
        log_check = subprocess.run(["powershell", "-Command", "Get-WinEvent -LogName 'OpenSSH/Admin' -MaxEvents 10 -ErrorAction SilentlyContinue | Where-Object {$_.LevelDisplayName -eq 'Error'} | Measure-Object | Select-Object -ExpandProperty Count"], capture_output=True, text=True, check=False)
        if log_check.returncode == 0 and log_check.stdout.strip():
            error_count = int(log_check.stdout.strip()) if log_check.stdout.strip().isdigit() else 0
            if error_count > 0:
                results["ssh_logs"] = {"status": "warning", "message": f"Found {error_count} SSH errors in log", "action": "Review event log"}
                other_checks.append(f"⚠️  Found {error_count} error(s) in SSH event log")
            else:
                results["ssh_logs"] = {"status": "ok", "message": "No recent SSH errors", "action": ""}
                other_checks.append("✅ No recent SSH errors in event log")
        else:
            other_checks.append("✅ No recent SSH errors in event log")
    except Exception:
        other_checks.append("⚠️  Could not check SSH logs")
    
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
        results["local_ssh_test"] = {"status": "warning", "message": "SSH client not found", "action": "Install SSH client"}
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
        summary_lines.append("  • Ensure public key is in correct authorized_keys")
    
    hostname_result = subprocess.run(["hostname"], capture_output=True, text=True, check=False)
    hostname = hostname_result.stdout.strip() if hostname_result.returncode == 0 else "unknown"
    
    summary_lines.append("\n[bold cyan]🔗 Connection Info:[/bold cyan]")
    summary_lines.append(f"  👤 User: {current_user}  |  🖥️  Host: {hostname}  |  🔌 Port: {ssh_port}")
    if ip_addresses:
        summary_lines.append(f"\n  Connect via: ssh {current_user}@{ip_addresses[0]}")
        if len(ip_addresses) > 1:
            summary_lines.append(f"  [dim](also: {', '.join(ip_addresses[1:])})[/dim]")
    
    console.print(Panel("\n".join(summary_lines), title="[bold]📊 Summary[/bold]", border_style="cyan", box=box.DOUBLE_EDGE))
    
    return results


if __name__ == "__main__":
    ssh_debug_windows()
