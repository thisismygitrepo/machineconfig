

from platform import system
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import subprocess
import os


console = Console()


def _run_ps(cmd: str) -> tuple[bool, str]:
    result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, check=False)
    return result.returncode == 0, result.stdout.strip()


def _detect_openssh() -> tuple[str, Path | None, Path | None]:
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
        raise NotImplementedError("ssh_debug_windows is only supported on Windows")

    results: dict[str, dict[str, str | bool]] = {}
    issues: list[tuple[str, str, str]] = []
    current_user = os.environ.get("USERNAME", "unknown")
    ssh_port = "22"
    ip_addresses: list[str] = []

    install_type, _sshd_exe, config_dir = _detect_openssh()
    ok, hostname = _run_ps("hostname")
    hostname = hostname if ok else "unknown"

    install_info: list[str] = []
    if install_type == "not_found":
        results["installation"] = {"status": "error", "message": "OpenSSH Server not installed"}
        issues.append(("OpenSSH not installed", "Cannot accept incoming SSH connections", "Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0"))
        install_info.append("❌ OpenSSH Server: [red]NOT INSTALLED[/red]")
    else:
        results["installation"] = {"status": "ok", "message": f"OpenSSH installed ({install_type})"}
        install_info.append(f"✅ OpenSSH Server: installed via {'Windows Capability' if install_type == 'capability' else 'winget'}")
        install_info.append(f"   Config: {config_dir}")

    ok, status = _run_ps("Get-Service -Name sshd -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Status")
    if not ok or not status:
        results["ssh_service"] = {"status": "error", "message": "sshd service not found"}
        issues.append(("sshd service missing", "SSH daemon not installed", "Install OpenSSH Server first"))
        install_info.append("❌ sshd service: [red]NOT FOUND[/red]")
    elif status != "Running":
        results["ssh_service"] = {"status": "error", "message": f"sshd is {status}"}
        issues.append((f"sshd is {status}", "SSH connections will be refused", "Start-Service sshd ; Set-Service sshd -StartupType Automatic"))
        install_info.append(f"❌ sshd service: [yellow]{status}[/yellow]")
    else:
        results["ssh_service"] = {"status": "ok", "message": "sshd running"}
        ok, startup = _run_ps("Get-Service -Name sshd | Select-Object -ExpandProperty StartType")
        startup_note = f" (startup: {startup})" if ok else ""
        install_info.append(f"✅ sshd service: [green]Running[/green]{startup_note}")

    console.print(Panel("\n".join(install_info), title="[bold]Installation & Service[/bold]", border_style="blue"))

    ssh_dir = Path.home().joinpath(".ssh")
    authorized_keys = ssh_dir.joinpath("authorized_keys")
    admin_auth_keys = Path("C:/ProgramData/ssh/administrators_authorized_keys")
    perm_info: list[str] = []

    ok, is_admin_str = _run_ps("([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)")
    is_admin = "True" in is_admin_str

    if is_admin:
        perm_info.append(f"👤 User [cyan]{current_user}[/cyan] is an [yellow]Administrator[/yellow]")
        perm_info.append("   ➜ Keys must be in: [cyan]C:\\ProgramData\\ssh\\administrators_authorized_keys[/cyan]")
        target_auth_keys = admin_auth_keys
    else:
        perm_info.append(f"👤 User [cyan]{current_user}[/cyan] is a standard user")
        perm_info.append(f"   ➜ Keys should be in: [cyan]{authorized_keys}[/cyan]")
        target_auth_keys = authorized_keys

    if not target_auth_keys.exists():
        results["authorized_keys"] = {"status": "error", "message": f"{target_auth_keys.name} missing"}
        issues.append((f"{target_auth_keys.name} missing", "No public keys authorized - SSH login will fail", f"Create file and add your public key to {target_auth_keys}"))
        perm_info.append(f"\n❌ [red]{target_auth_keys.name} does not exist[/red]")
        perm_info.append("   [dim]No keys = no login. Add your public key to this file.[/dim]")
    else:
        try:
            keys = [line for line in target_auth_keys.read_text(encoding="utf-8").split("\n") if line.strip()]
            results["authorized_keys"] = {"status": "ok", "message": f"{len(keys)} key(s)"}
            perm_info.append(f"\n✅ {target_auth_keys.name}: [green]{len(keys)} key(s)[/green]")
        except Exception as e:
            perm_info.append(f"\n⚠️  Could not read {target_auth_keys.name}: {e}")

    if is_admin and admin_auth_keys.exists():
        ok, icacls_out = _run_ps(f'icacls "{admin_auth_keys}"')
        if ok:
            needs_fix = "BUILTIN\\Users" in icacls_out or "Everyone" in icacls_out
            if needs_fix:
                results["admin_keys_perms"] = {"status": "error", "message": "Permissions too open"}
                issues.append(("administrators_authorized_keys permissions wrong", "sshd ignores file if permissions allow other users", f'icacls "{admin_auth_keys}" /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"'))
                perm_info.append("❌ [red]Permissions too open[/red] - sshd will ignore this file!")
            else:
                perm_info.append("✅ Permissions: restricted to Administrators/SYSTEM")

    console.print(Panel("\n".join(perm_info), title="[bold]Keys & Permissions[/bold]", border_style="blue"))

    net_info: list[str] = []
    ok, ip_out = _run_ps("Get-NetIPAddress -AddressFamily IPv4 -PrefixOrigin Dhcp,Manual | Where-Object {$_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*'} | Select-Object -ExpandProperty IPAddress")
    if ok and ip_out:
        ip_addresses = [ip.strip() for ip in ip_out.split("\n") if ip.strip()]
        net_info.append(f"🌐 IP addresses: [cyan]{', '.join(ip_addresses)}[/cyan]")

    sshd_config: Path | None = config_dir.joinpath("sshd_config") if config_dir else None
    if sshd_config and sshd_config.exists():
        try:
            config_text = sshd_config.read_text(encoding="utf-8")
            port_lines = [line for line in config_text.split("\n") if line.strip().startswith("Port") and not line.strip().startswith("#")]
            if port_lines:
                ssh_port = port_lines[0].split()[1]
            net_info.append(f"🔌 SSH port: [cyan]{ssh_port}[/cyan]")

            pubkey_lines = [line for line in config_text.split("\n") if "PubkeyAuthentication" in line and not line.strip().startswith("#")]
            if pubkey_lines and "no" in pubkey_lines[-1].lower():
                results["pubkey_auth"] = {"status": "error", "message": "PubkeyAuthentication disabled"}
                issues.append(("PubkeyAuthentication disabled", "Key-based login won't work", f'Edit {sshd_config} and set PubkeyAuthentication yes, then Restart-Service sshd'))
                net_info.append("❌ PubkeyAuthentication: [red]disabled[/red]")
            else:
                net_info.append("✅ PubkeyAuthentication: enabled")

            password_lines = [line for line in config_text.split("\n") if "PasswordAuthentication" in line and not line.strip().startswith("#")]
            if password_lines:
                password_enabled = "yes" in password_lines[-1].lower()
                if password_enabled:
                    results["password_auth"] = {"status": "ok", "message": "PasswordAuthentication enabled"}
                    net_info.append("✅ PasswordAuthentication: [green]enabled[/green]")
                else:
                    results["password_auth"] = {"status": "info", "message": "PasswordAuthentication disabled"}
                    net_info.append("ℹ️  PasswordAuthentication: [yellow]disabled[/yellow] (key-only)")
            else:
                results["password_auth"] = {"status": "ok", "message": "PasswordAuthentication enabled (default)"}
                net_info.append("✅ PasswordAuthentication: [green]enabled[/green] (default)")
        except Exception:
            pass

    netstat = subprocess.run(["netstat", "-an"], capture_output=True, text=True, check=False)
    if netstat.returncode == 0:
        listening_lines = [line for line in netstat.stdout.split("\n") if f":{ssh_port}" in line and "LISTENING" in line]
        if not listening_lines:
            results["ssh_listening"] = {"status": "error", "message": f"Not listening on port {ssh_port}"}
            issues.append((f"SSH not listening on port {ssh_port}", "No connections possible", "Restart-Service sshd"))
            net_info.append(f"❌ Listening: [red]NOT listening on port {ssh_port}[/red]")
        elif all("127.0.0.1" in line or "[::1]" in line for line in listening_lines):
            results["ssh_listening"] = {"status": "error", "message": "Listening on localhost only"}
            issues.append(("SSH bound to localhost only", "Only local connections work", f"Check ListenAddress in {sshd_config}"))
            net_info.append("❌ Listening: [red]localhost only[/red] (remote connections blocked)")
        else:
            results["ssh_listening"] = {"status": "ok", "message": f"Listening on port {ssh_port}"}
            net_info.append(f"✅ Listening: 0.0.0.0:{ssh_port}")

    fw_cmd = f"""
        $rules = Get-NetFirewallRule -ErrorAction SilentlyContinue | Where-Object {{
            ($_.DisplayName -like '*SSH*' -or $_.DisplayName -like '*OpenSSH*' -or $_.Name -like '*SSH*' -or $_.Name -like '*sshd*') -and
            $_.Direction -eq 'Inbound'
        }}
        if (-not $rules) {{
            $portFilter = Get-NetFirewallPortFilter -ErrorAction SilentlyContinue | Where-Object {{ $_.LocalPort -eq '{ssh_port}' -and $_.Protocol -eq 'TCP' }}
            if ($portFilter) {{
                $rules = $portFilter | ForEach-Object {{ Get-NetFirewallRule -AssociatedNetFirewallPortFilter $_ -ErrorAction SilentlyContinue }} | Where-Object {{ $_.Direction -eq 'Inbound' }}
            }}
        }}
        if ($rules) {{
            $rules | Select-Object Name, DisplayName, Enabled, Action | Format-List
        }}
    """
    ok, fw_out = _run_ps(fw_cmd)
    if ok and fw_out.strip():
        has_allow = "Enabled : True" in fw_out and "Action : Allow" in fw_out
        if has_allow:
            results["firewall"] = {"status": "ok", "message": "Firewall allows SSH"}
            net_info.append("✅ Firewall: SSH rule exists and enabled")
        else:
            results["firewall"] = {"status": "warning", "message": "Firewall rule exists but may not be active"}
            issues.append(("Firewall rule not active", "Incoming SSH may be blocked", f'New-NetFirewallRule -Name "SSH" -DisplayName "SSH" -Protocol TCP -LocalPort {ssh_port} -Action Allow -Enabled True'))
            net_info.append("⚠️  Firewall: SSH rule exists but [yellow]not enabled[/yellow]")
    else:
        if not is_admin:
            results["firewall"] = {"status": "warning", "message": "Cannot verify firewall (run as Admin)"}
            net_info.append("⚠️  Firewall: [yellow]Cannot verify - run script as Administrator[/yellow]")
            net_info.append("   [dim]Firewall rules may exist but require elevation to query.[/dim]")
        else:
            results["firewall"] = {"status": "error", "message": "No SSH firewall rule"}
            issues.append(("No SSH firewall rule", "Windows Firewall blocks incoming SSH by default", f'New-NetFirewallRule -Name "SSH" -DisplayName "SSH" -Protocol TCP -LocalPort {ssh_port} -Action Allow -Enabled True'))
            net_info.append("❌ Firewall: [red]No SSH rule found[/red]")
            net_info.append("   [dim]Windows blocks all incoming by default. Must create allow rule.[/dim]")

    console.print(Panel("\n".join(net_info), title="[bold]Network & Firewall[/bold]", border_style="blue"))

    if issues:
        fix_table = Table(title="Issues & Fixes", box=box.ROUNDED, show_lines=True, title_style="bold red")
        fix_table.add_column("Issue", style="yellow", width=30)
        fix_table.add_column("Impact", style="white", width=35)
        fix_table.add_column("Fix Command", style="green", width=60)
        for issue, impact, fix in issues:
            fix_table.add_row(issue, impact, fix)
        console.print(fix_table)

        console.print(Panel(f"[bold yellow]⚠️  {len(issues)} issue(s) found[/bold yellow]\nRun the fix commands above (as Administrator) then re-run this diagnostic.", title="[bold]Summary[/bold]", border_style="yellow"))
    else:
        conn_info = f"👤 {current_user}  🖥️  {hostname}  🔌 :{ssh_port}"
        if ip_addresses:
            conn_info += f"\n\n[bold]Connect:[/bold] ssh {current_user}@{ip_addresses[0]}"
        console.print(Panel(f"[bold green]✅ All checks passed[/bold green]\n\n{conn_info}", title="[bold]Ready[/bold]", border_style="green"))

    return results


if __name__ == "__main__":
    ssh_debug_windows()
