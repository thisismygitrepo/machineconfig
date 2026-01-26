

from platform import system
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import os
import re

from machineconfig.scripts.python.helpers.helpers_network.ssh.ssh_debug_linux_utils import check_sshd_installed, detect_package_manager, run_cmd


console = Console()


def ssh_debug_linux() -> dict[str, dict[str, str | bool]]:
    current_os = system()
    if current_os == "Darwin":
        from machineconfig.scripts.python.helpers.helpers_network.ssh.ssh_debug_darwin import ssh_debug_darwin
        return ssh_debug_darwin()
    if current_os != "Linux":
        raise NotImplementedError(f"ssh_debug_linux is only supported on Linux and macOS, not {current_os}")

    results: dict[str, dict[str, str | bool]] = {}
    issues: list[tuple[str, str, str]] = []
    current_user = os.environ.get("USER", os.environ.get("USERNAME", "unknown"))
    ssh_port = "22"
    ip_addresses: list[str] = []

    ok, hostname = run_cmd(["hostname"])
    hostname = hostname if ok else "unknown"

    install_info: list[str] = []
    sshd_installed, sshd_path = check_sshd_installed()
    _pkg_manager, install_cmd = detect_package_manager()
    if not sshd_installed:
        results["installation"] = {"status": "error", "message": "OpenSSH Server not installed"}
        issues.append(("sshd not installed", "Cannot accept incoming SSH connections", install_cmd))
        install_info.append("❌ OpenSSH Server: [red]NOT INSTALLED[/red]")
        install_info.append(f"   [dim]Install with: {install_cmd}[/dim]")
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
    ssh_ok, _ = run_cmd(["systemctl", "is-active", "ssh"])
    sshd_ok, _ = run_cmd(["systemctl", "is-active", "sshd"])
    if ssh_ok or sshd_ok:
        svc_name = "ssh" if ssh_ok else "sshd"
        results["ssh_service"] = {"status": "ok", "message": f"{svc_name} running"}
        svc_info.append(f"✅ Service: [green]{svc_name} running[/green]")
    else:
        results["ssh_service"] = {"status": "error", "message": "sshd not running"}
        issues.append(("sshd not running", "No SSH daemon = no connections", "sudo systemctl start ssh && sudo systemctl enable ssh"))
        svc_info.append("❌ Service: [red]not running[/red]")

    console.print(Panel("\n".join(svc_info), title="[bold]Service[/bold]", border_style="blue"))

    net_info: list[str] = []
    ok, ip_out = run_cmd(["ip", "addr", "show"])
    if ok:
        ip_addresses = re.findall(r'inet\s+(\d+\.\d+\.\d+\.\d+)/\d+.*scope\s+global', ip_out)
        if ip_addresses:
            net_info.append(f"🌐 IP: [cyan]{', '.join(ip_addresses)}[/cyan]")

    sshd_config_paths = [Path("/etc/ssh/sshd_config"), Path("/etc/sshd_config")]
    sshd_config: Path | None = None
    for p in sshd_config_paths:
        if p.exists():
            sshd_config = p
            break

    sshd_config_d = Path("/etc/ssh/sshd_config.d")
    cloud_init_overrides: dict[str, Path] = {}
    cloud_init_files: list[Path] = []
    if sshd_config_d.exists():
        for conf_file in sorted(sshd_config_d.glob("*.conf")):
            cloud_init_files.append(conf_file)
            try:
                conf_text = conf_file.read_text(encoding="utf-8")
                for line in conf_text.split("\n"):
                    line_stripped = line.strip()
                    if line_stripped and not line_stripped.startswith("#"):
                        key = line_stripped.split()[0] if line_stripped.split() else ""
                        if key:
                            cloud_init_overrides[key] = conf_file
            except Exception:
                pass

    if cloud_init_files:
        cloud_info: list[str] = []
        cloud_info.append(f"⚠️  Found [yellow]{len(cloud_init_files)}[/yellow] override file(s) in /etc/ssh/sshd_config.d/")
        cloud_info.append("   [dim]These files can override settings in the main sshd_config![/dim]")
        for cf in cloud_init_files:
            cloud_info.append(f"   \u2022 [cyan]{cf.name}[/cyan]")
        if cloud_init_overrides:
            overridden_keys = list(cloud_init_overrides.keys())[:5]
            cloud_info.append(f"   Overriding: {', '.join(overridden_keys)}{'...' if len(cloud_init_overrides) > 5 else ''}")
        console.print(Panel("\n".join(cloud_info), title="[bold yellow]Cloud-Init SSH Overrides[/bold yellow]", border_style="yellow"))

    if sshd_config:
        try:
            config_text = sshd_config.read_text(encoding="utf-8")
            port_lines = [line for line in config_text.split("\n") if line.strip().startswith("Port") and not line.strip().startswith("#")]
            if port_lines:
                ssh_port = port_lines[0].split()[1]
            net_info.append(f"🔌 Port: [cyan]{ssh_port}[/cyan]")

            pubkey_lines = [line for line in config_text.split("\n") if "PubkeyAuthentication" in line and not line.strip().startswith("#")]
            pubkey_override_file: Path | None = cloud_init_overrides.get("PubkeyAuthentication")
            if pubkey_override_file:
                try:
                    override_text = pubkey_override_file.read_text(encoding="utf-8")
                    override_pubkey_lines = [line for line in override_text.split("\n") if "PubkeyAuthentication" in line and not line.strip().startswith("#")]
                    if override_pubkey_lines:
                        pubkey_lines = override_pubkey_lines
                except Exception:
                    pass
            if pubkey_lines and "no" in pubkey_lines[-1].lower():
                results["pubkey_auth"] = {"status": "error", "message": "PubkeyAuthentication disabled"}
                fix_target = pubkey_override_file if pubkey_override_file else sshd_config
                issues.append(("PubkeyAuthentication disabled", "Key-based login won't work", f"Edit {fix_target}: set PubkeyAuthentication yes, then sudo systemctl restart ssh"))
                override_note = f" (overridden in {pubkey_override_file.name})" if pubkey_override_file else ""
                net_info.append(f"❌ PubkeyAuthentication: [red]disabled[/red]{override_note}")
            else:
                net_info.append("✅ PubkeyAuthentication: enabled")

            password_lines = [line for line in config_text.split("\n") if "PasswordAuthentication" in line and not line.strip().startswith("#")]
            password_override_file: Path | None = cloud_init_overrides.get("PasswordAuthentication")
            if password_override_file:
                try:
                    override_text = password_override_file.read_text(encoding="utf-8")
                    override_password_lines = [line for line in override_text.split("\n") if "PasswordAuthentication" in line and not line.strip().startswith("#")]
                    if override_password_lines:
                        password_lines = override_password_lines
                except Exception:
                    pass
            if password_lines:
                password_enabled = "yes" in password_lines[-1].lower()
                override_note = f" (from {password_override_file.name})" if password_override_file else ""
                if password_enabled:
                    results["password_auth"] = {"status": "ok", "message": "PasswordAuthentication enabled"}
                    net_info.append(f"✅ PasswordAuthentication: [green]enabled[/green]{override_note}")
                else:
                    results["password_auth"] = {"status": "info", "message": "PasswordAuthentication disabled"}
                    net_info.append(f"ℹ️  PasswordAuthentication: [yellow]disabled[/yellow] (key-only){override_note}")
                    if password_override_file:
                        issues.append((f"PasswordAuth disabled by {password_override_file.name}", "Password login blocked by cloud-init config", f"Edit {password_override_file}: set PasswordAuthentication yes, then sudo systemctl restart ssh"))
            else:
                results["password_auth"] = {"status": "ok", "message": "PasswordAuthentication enabled (default)"}
                net_info.append("✅ PasswordAuthentication: [green]enabled[/green] (default)")

            permit_root = [line for line in config_text.split("\n") if "PermitRootLogin" in line and not line.strip().startswith("#")]
            if permit_root:
                val = permit_root[-1].split()[-1].lower()
                net_info.append(f"ℹ️  PermitRootLogin: {val}")
        except Exception:
            pass

    ok, ss_out = run_cmd(["ss", "-tlnp"])
    if ok:
        listening = [line for line in ss_out.split("\n") if f":{ssh_port}" in line]
        if not listening:
            results["ssh_listening"] = {"status": "error", "message": f"Not listening on {ssh_port}"}
            issues.append((f"Not listening on port {ssh_port}", "No connections possible", "sudo systemctl restart ssh"))
            net_info.append(f"❌ Listening: [red]NOT on port {ssh_port}[/red]")
        elif all("127.0.0.1" in line or "[::1]" in line for line in listening):
            results["ssh_listening"] = {"status": "error", "message": "Localhost only"}
            issues.append(("SSH bound to localhost", "Only local connections", f"Edit {sshd_config}: remove/comment ListenAddress 127.0.0.1"))
            net_info.append("❌ Listening: [red]localhost only[/red]")
        else:
            results["ssh_listening"] = {"status": "ok", "message": f"Listening on {ssh_port}"}
            net_info.append(f"✅ Listening: 0.0.0.0:{ssh_port}")

    fw_checked = False
    ok, ufw_out = run_cmd(["ufw", "status"])
    if ok and "Status: active" in ufw_out:
        fw_checked = True
        if f"{ssh_port}/tcp" in ufw_out.lower() or "ssh" in ufw_out.lower() or f" {ssh_port} " in ufw_out:
            results["firewall"] = {"status": "ok", "message": "UFW allows SSH"}
            net_info.append("✅ Firewall (UFW): allows SSH")
        else:
            results["firewall"] = {"status": "error", "message": "UFW blocking SSH"}
            issues.append(("UFW blocking SSH", "Incoming connections dropped", f"sudo ufw allow {ssh_port}/tcp"))
            net_info.append("❌ Firewall (UFW): [red]blocking SSH[/red]")
            net_info.append("   [dim]Active firewall without SSH rule = blocked[/dim]")

    if not fw_checked:
        ok, fwd_out = run_cmd(["firewall-cmd", "--state"])
        if ok and "running" in fwd_out.lower():
            fw_checked = True
            ok2, svc_out = run_cmd(["firewall-cmd", "--list-services"])
            if ok2 and "ssh" in svc_out.lower():
                results["firewall"] = {"status": "ok", "message": "firewalld allows SSH"}
                net_info.append("✅ Firewall (firewalld): allows SSH")
            else:
                results["firewall"] = {"status": "error", "message": "firewalld blocking SSH"}
                issues.append(("firewalld blocking SSH", "Incoming connections dropped", "sudo firewall-cmd --permanent --add-service=ssh && sudo firewall-cmd --reload"))
                net_info.append("❌ Firewall (firewalld): [red]blocking SSH[/red]")

    if not fw_checked:
        ok, ipt_out = run_cmd(["iptables", "-L", "INPUT", "-n"])
        if ok and ipt_out:
            has_drop_policy = "policy DROP" in ipt_out or "policy REJECT" in ipt_out
            has_ssh_allow = f"dpt:{ssh_port}" in ipt_out or "dpt:ssh" in ipt_out
            if has_drop_policy and not has_ssh_allow:
                results["firewall"] = {"status": "error", "message": "iptables blocking SSH"}
                issues.append(("iptables blocking SSH", "DROP/REJECT policy without SSH allow", f"sudo iptables -I INPUT -p tcp --dport {ssh_port} -j ACCEPT"))
                net_info.append("❌ Firewall (iptables): [red]DROP policy, no SSH rule[/red]")
                fw_checked = True
            elif has_drop_policy and has_ssh_allow:
                results["firewall"] = {"status": "ok", "message": "iptables allows SSH"}
                net_info.append("✅ Firewall (iptables): allows SSH")
                fw_checked = True

    if not fw_checked:
        net_info.append("ℹ️  Firewall: none detected / not active")

    console.print(Panel("\n".join(net_info), title="[bold]Network & Firewall[/bold]", border_style="blue"))

    other_info: list[str] = []
    hosts_deny = Path("/etc/hosts.deny")
    if hosts_deny.exists():
        try:
            content = hosts_deny.read_text(encoding="utf-8")
            active = [line for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]
            joined = " ".join(active).lower()
            if "sshd" in joined or "all" in joined:
                results["hosts_deny"] = {"status": "error", "message": "hosts.deny blocking"}
                issues.append(("hosts.deny blocking SSH", "TCP wrappers deny before firewall", "Edit /etc/hosts.deny to remove sshd/ALL entries"))
                other_info.append("❌ /etc/hosts.deny: [red]may block SSH[/red]")
            else:
                other_info.append("✅ /etc/hosts.deny: OK")
        except Exception:
            pass

    ok, se_out = run_cmd(["getenforce"])
    if ok and se_out:
        if se_out == "Enforcing":
            other_info.append("ℹ️  SELinux: Enforcing (run [cyan]restorecon -Rv ~/.ssh[/cyan] if issues)")
        else:
            other_info.append(f"ℹ️  SELinux: {se_out}")

    log_files = [Path("/var/log/auth.log"), Path("/var/log/secure")]
    for lf in log_files:
        if lf.exists():
            ok, tail = run_cmd(["tail", "-n", "20", str(lf)])
            if ok:
                errors = [line for line in tail.split("\n") if any(k in line.lower() for k in ["error", "failed", "refused", "denied"]) and "ssh" in line.lower()]
                if errors:
                    other_info.append(f"⚠️  Recent SSH errors in {lf.name}: {len(errors)}")
                else:
                    other_info.append(f"✅ {lf.name}: no recent SSH errors")
            break

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
        script_lines = ["#!/bin/bash", "set -e", "", "# SSH Fix Script - Generated by ssh_debug_linux", f"# {len(issues)} issue(s) to fix", ""]
        for issue, _impact, fix in issues:
            script_lines.append(f"# Fix: {issue}")
            script_lines.append(fix)
            script_lines.append("")
        script_lines.append("echo 'All fixes applied. Re-run ssh_debug_linux to verify.'")
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
    ssh_debug_linux()
