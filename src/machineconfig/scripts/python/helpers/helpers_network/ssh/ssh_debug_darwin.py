

from platform import system
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import os
import re

from machineconfig.scripts.python.helpers.helpers_network.ssh.ssh_debug_darwin_utils import check_sshd_installed, run_cmd


console = Console()


def ssh_debug_darwin() -> dict[str, dict[str, str | bool]]:
    if system() != "Darwin":
        raise NotImplementedError("ssh_debug_darwin is only supported on macOS")

    results: dict[str, dict[str, str | bool]] = {}
    issues: list[tuple[str, str, str]] = []
    current_user = os.environ.get("USER", "unknown")
    ssh_port = "22"
    ip_addresses: list[str] = []

    ok, hostname = run_cmd(["hostname"])
    hostname = hostname if ok else "unknown"

    install_info: list[str] = []
    sshd_installed, sshd_path = check_sshd_installed()
    if not sshd_installed:
        results["installation"] = {"status": "error", "message": "OpenSSH Server not installed"}
        issues.append(("sshd not installed", "Cannot accept incoming SSH connections", "brew install openssh"))
        install_info.append("❌ OpenSSH Server: [red]NOT INSTALLED[/red]")
        install_info.append("   [dim]Install with: brew install openssh[/dim]")
    else:
        results["installation"] = {"status": "ok", "message": f"sshd found at {sshd_path}"}
        install_info.append(f"✅ OpenSSH Server: installed at [cyan]{sshd_path}[/cyan]")
    console.print(Panel("\n".join(install_info), title="[bold]Installation[/bold]", border_style="blue"))

    ssh_dir = Path.home().joinpath(".ssh")
    authorized_keys = ssh_dir.joinpath("authorized_keys")
    home_dir = Path.home()

    perm_info: list[str] = []
    home_stat = os.stat(home_dir)
    home_perms = oct(home_stat.st_mode)[-3:]
    if home_perms[2] in ["7", "6", "3", "2"]:
        results["home_directory"] = {"status": "error", "message": f"Home world-writable: {home_perms}"}
        issues.append((f"Home dir perms {home_perms}", "sshd refuses login if home is world-writable", f"chmod 755 {home_dir}"))
        perm_info.append(f"❌ Home directory: [red]{home_perms}[/red] (world-writable)")
        perm_info.append("   [dim]sshd will refuse key auth if home is writable by others[/dim]")
    else:
        perm_info.append(f"✅ Home directory: {home_perms}")

    if not ssh_dir.exists():
        results["ssh_directory"] = {"status": "error", "message": "~/.ssh missing"}
        issues.append(("~/.ssh missing", "No place for authorized_keys", "mkdir -p ~/.ssh && chmod 700 ~/.ssh"))
        perm_info.append("❌ ~/.ssh: [red]does not exist[/red]")
    else:
        ssh_perms = oct(os.stat(ssh_dir).st_mode)[-3:]
        if ssh_perms != "700":
            results["ssh_directory"] = {"status": "error", "message": f"~/.ssh perms {ssh_perms}"}
            issues.append((f"~/.ssh perms {ssh_perms}", "sshd requires 700 on ~/.ssh", "chmod 700 ~/.ssh"))
            perm_info.append(f"❌ ~/.ssh: [red]{ssh_perms}[/red] (must be 700)")
        else:
            perm_info.append(f"✅ ~/.ssh: {ssh_perms}")

    if not authorized_keys.exists():
        results["authorized_keys"] = {"status": "error", "message": "authorized_keys missing"}
        issues.append(("authorized_keys missing", "No keys = no login", "Add public key: cat id_rsa.pub >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"))
        perm_info.append("❌ authorized_keys: [red]does not exist[/red]")
        perm_info.append("   [dim]No authorized keys = cannot login with SSH key[/dim]")
    else:
        ak_perms = oct(os.stat(authorized_keys).st_mode)[-3:]
        try:
            keys = [line for line in authorized_keys.read_text(encoding="utf-8").split("\n") if line.strip()]
            key_count = len(keys)
        except Exception:
            key_count = 0
        if ak_perms not in ["600", "644"]:
            results["authorized_keys"] = {"status": "error", "message": f"authorized_keys perms {ak_perms}"}
            issues.append((f"authorized_keys perms {ak_perms}", "sshd requires 600 or 644", "chmod 600 ~/.ssh/authorized_keys"))
            perm_info.append(f"❌ authorized_keys: [red]{ak_perms}[/red] ({key_count} key(s)) - must be 600/644")
        else:
            results["authorized_keys"] = {"status": "ok", "message": f"{key_count} key(s)"}
            perm_info.append(f"✅ authorized_keys: {ak_perms} ([green]{key_count} key(s)[/green])")

    console.print(Panel("\n".join(perm_info), title="[bold]Permissions[/bold]", border_style="blue"))

    svc_info: list[str] = []
    ok, launchctl_out = run_cmd(["launchctl", "list", "com.openssh.sshd"])
    is_running = ok and '"PID"' in launchctl_out
    
    ok2, launchctl_check = run_cmd(["sudo", "launchctl", "print", "system/com.openssh.sshd"])
    if ok2 and ("state = running" in launchctl_check or "active count" in launchctl_check):
        is_running = True
    
    ok3, system_prefs_check = run_cmd(["sudo", "systemsetup", "-getremotelogin"])
    remote_login_enabled = ok3 and "On" in system_prefs_check
    
    if is_running or remote_login_enabled:
        results["ssh_service"] = {"status": "ok", "message": "sshd running"}
        svc_info.append("✅ Service: [green]sshd running[/green]")
    else:
        results["ssh_service"] = {"status": "error", "message": "sshd not running"}
        issues.append(("sshd not running", "No SSH daemon = no connections", "sudo systemsetup -setremotelogin on"))
        svc_info.append("❌ Service: [red]not running[/red]")
        svc_info.append("   [dim]Enable with: sudo systemsetup -setremotelogin on[/dim]")

    console.print(Panel("\n".join(svc_info), title="[bold]Service[/bold]", border_style="blue"))

    net_info: list[str] = []
    ok, ifconfig_out = run_cmd(["ifconfig"])
    if ok:
        ip_addresses = re.findall(r'inet\s+(\d+\.\d+\.\d+\.\d+)(?:\s+netmask|\s+-->)', ifconfig_out)
        ip_addresses = [ip for ip in ip_addresses if not ip.startswith("127.")]
        if ip_addresses:
            net_info.append(f"🌐 IP: [cyan]{', '.join(ip_addresses)}[/cyan]")

    sshd_config_paths = [Path("/etc/ssh/sshd_config"), Path("/private/etc/ssh/sshd_config")]
    sshd_config: Path | None = None
    for p in sshd_config_paths:
        if p.exists():
            sshd_config = p
            break

    sshd_config_d = Path("/etc/ssh/sshd_config.d")
    if not sshd_config_d.exists():
        sshd_config_d = Path("/private/etc/ssh/sshd_config.d")
    
    override_files: list[Path] = []
    if sshd_config_d.exists():
        for conf_file in sorted(sshd_config_d.glob("*.conf")):
            override_files.append(conf_file)

    if override_files:
        cloud_info: list[str] = []
        cloud_info.append(f"⚠️  Found [yellow]{len(override_files)}[/yellow] override file(s) in {sshd_config_d}")
        cloud_info.append("   [dim]These files can override settings in the main sshd_config![/dim]")
        for cf in override_files:
            cloud_info.append(f"   \u2022 [cyan]{cf.name}[/cyan]")
        console.print(Panel("\n".join(cloud_info), title="[bold yellow]SSH Config Overrides[/bold yellow]", border_style="yellow"))

    if sshd_config:
        try:
            config_text = sshd_config.read_text(encoding="utf-8")
            port_lines = [line for line in config_text.split("\n") if line.strip().startswith("Port") and not line.strip().startswith("#")]
            if port_lines:
                ssh_port = port_lines[0].split()[1]
            net_info.append(f"🔌 Port: [cyan]{ssh_port}[/cyan]")

            pubkey_lines = [line for line in config_text.split("\n") if "PubkeyAuthentication" in line and not line.strip().startswith("#")]
            if pubkey_lines and "no" in pubkey_lines[-1].lower():
                results["pubkey_auth"] = {"status": "error", "message": "PubkeyAuthentication disabled"}
                issues.append(("PubkeyAuthentication disabled", "Key-based login won't work", f"Edit {sshd_config}: set PubkeyAuthentication yes, then restart SSH"))
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

            permit_root = [line for line in config_text.split("\n") if "PermitRootLogin" in line and not line.strip().startswith("#")]
            if permit_root:
                val = permit_root[-1].split()[-1].lower()
                net_info.append(f"ℹ️  PermitRootLogin: {val}")
        except Exception:
            pass

    ok, lsof_out = run_cmd(["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"])
    listening = False
    localhost_only = False
    if ok:
        ssh_lines = [line for line in lsof_out.split("\n") if f":{ssh_port}" in line and "sshd" in line.lower()]
        if ssh_lines:
            listening = True
            if all("127.0.0.1" in line or "[::1]" in line for line in ssh_lines):
                localhost_only = True
    
    if not listening:
        results["ssh_listening"] = {"status": "error", "message": f"Not listening on {ssh_port}"}
        issues.append((f"Not listening on port {ssh_port}", "No connections possible", "sudo systemsetup -setremotelogin off && sudo systemsetup -setremotelogin on"))
        net_info.append(f"❌ Listening: [red]NOT on port {ssh_port}[/red]")
    elif localhost_only:
        results["ssh_listening"] = {"status": "error", "message": "Localhost only"}
        issues.append(("SSH bound to localhost", "Only local connections", f"Edit {sshd_config}: remove/comment ListenAddress 127.0.0.1"))
        net_info.append("❌ Listening: [red]localhost only[/red]")
    else:
        results["ssh_listening"] = {"status": "ok", "message": f"Listening on {ssh_port}"}
        net_info.append(f"✅ Listening: *:{ssh_port}")

    ok, pf_status = run_cmd(["sudo", "pfctl", "-s", "info"])
    if ok and "Status: Enabled" in pf_status:
        ok2, pf_rules = run_cmd(["sudo", "pfctl", "-s", "rules"])
        if ok2:
            ssh_blocked = any(f"block" in line and (f"port {ssh_port}" in line or "port ssh" in line) for line in pf_rules.split("\n"))
            if ssh_blocked:
                results["firewall"] = {"status": "error", "message": "PF blocking SSH"}
                issues.append(("PF blocking SSH", "Incoming connections dropped", "Check /etc/pf.conf and remove blocking rules for port 22"))
                net_info.append("❌ Firewall (PF): [red]blocking SSH[/red]")
            else:
                results["firewall"] = {"status": "ok", "message": "PF not blocking SSH"}
                net_info.append("✅ Firewall (PF): not blocking SSH")
    else:
        ok, app_fw_status = run_cmd(["sudo", "/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"])
        if ok and "enabled" in app_fw_status.lower():
            ok2, app_fw_sshd = run_cmd(["sudo", "/usr/libexec/ApplicationFirewall/socketfilterfw", "--getappblocked", "/usr/sbin/sshd"])
            if ok2:
                if "blocked" in app_fw_sshd.lower() and "no" not in app_fw_sshd.lower():
                    results["firewall"] = {"status": "error", "message": "Application Firewall blocking SSH"}
                    issues.append(("Application Firewall blocking sshd", "Incoming connections blocked", "sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/sbin/sshd && sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/sbin/sshd"))
                    net_info.append("❌ Firewall (App): [red]blocking sshd[/red]")
                else:
                    results["firewall"] = {"status": "ok", "message": "Application Firewall allows SSH"}
                    net_info.append("✅ Firewall (App): allows sshd")
        else:
            net_info.append("ℹ️  Firewall: disabled or not detected")

    console.print(Panel("\n".join(net_info), title="[bold]Network & Firewall[/bold]", border_style="blue"))

    other_info: list[str] = []
    
    ok, xattr_check = run_cmd(["xattr", str(ssh_dir)])
    if ok and xattr_check:
        other_info.append("⚠️  Extended attributes on ~/.ssh (may cause issues)")
        other_info.append(f"   [dim]Run: xattr -cr {ssh_dir}[/dim]")

    log_files = [Path("/var/log/system.log"), Path("/var/log/auth.log")]
    for lf in log_files:
        if lf.exists():
            ok, tail = run_cmd(["tail", "-n", "50", str(lf)])
            if ok:
                errors = [line for line in tail.split("\n") if any(k in line.lower() for k in ["error", "failed", "refused", "denied"]) and "ssh" in line.lower()]
                if errors:
                    other_info.append(f"⚠️  Recent SSH errors in {lf.name}: {len(errors)}")
                else:
                    other_info.append(f"✅ {lf.name}: no recent SSH errors")
            break
    
    if not any(lf.exists() for lf in log_files):
        ok, log_show = run_cmd(["log", "show", "--predicate", "process == 'sshd'", "--last", "10m", "--style", "compact"])
        if ok and log_show:
            errors = [line for line in log_show.split("\n") if any(k in line.lower() for k in ["error", "failed", "refused", "denied"])]
            if errors:
                other_info.append(f"⚠️  Recent SSH errors in unified log: {len(errors)}")
                other_info.append("   [dim]View with: log show --predicate 'process == \"sshd\"' --last 1h[/dim]")
            else:
                other_info.append("✅ Unified log: no recent SSH errors")

    if other_info:
        console.print(Panel("\n".join(other_info), title="[bold]Additional[/bold]", border_style="blue"))

    if issues:
        fix_table = Table(title="Issues & Fixes", box=box.ROUNDED, show_lines=True, title_style="bold red")
        fix_table.add_column("Issue", style="yellow", width=25)
        fix_table.add_column("Impact", style="white", width=35)
        fix_table.add_column("Fix Command", style="green", width=55)
        for issue, impact, fix in issues:
            fix_table.add_row(issue, impact, fix)
        console.print(fix_table)

        fix_script_path = Path("/tmp/ssh_fix.sh")
        script_lines = ["#!/bin/bash", "set -e", "", "# SSH Fix Script - Generated by ssh_debug_darwin", f"# {len(issues)} issue(s) to fix", ""]
        for issue, _impact, fix in issues:
            script_lines.append(f"# Fix: {issue}")
            script_lines.append(fix)
            script_lines.append("")
        script_lines.append("echo 'All fixes applied. Re-run ssh_debug_darwin to verify.'")
        fix_script_path.write_text("\n".join(script_lines), encoding="utf-8")
        fix_script_path.chmod(0o755)

        console.print(Panel(f"[bold yellow]⚠️  {len(issues)} issue(s) found[/bold yellow]\n\nFix script generated: [cyan]{fix_script_path}[/cyan]\nRun: [green]sudo bash {fix_script_path}[/green]", title="[bold]Summary[/bold]", border_style="yellow"))
    else:
        conn_info = f"👤 {current_user}  🖥️  {hostname}  🔌 :{ssh_port}"
        if ip_addresses:
            conn_info += f"\n\n[bold]Connect:[/bold] ssh {current_user}@{ip_addresses[0]}"
        console.print(Panel(f"[bold green]✅ All checks passed[/bold green]\n\n{conn_info}", title="[bold]Ready[/bold]", border_style="green"))

    return results


if __name__ == "__main__":
    ssh_debug_darwin()
