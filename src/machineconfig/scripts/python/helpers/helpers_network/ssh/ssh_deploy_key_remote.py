from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich import box

from machineconfig.utils.ssh import SSH


console = Console()


def deploy_key_to_remote(remote_target: str, pubkey_path: Path, password: Optional[str]) -> bool:
    """Deploy a public key to a remote machine's authorized_keys.
    
    Works for any combination of local/remote OS (Linux, macOS, Windows).
    Password is prompted once if not provided and key-based auth fails.
    
    Returns True on success, False on failure.
    """
    console.print(Panel(f"🔐 Deploying key to remote: [cyan]{remote_target}[/cyan]\n📄 Key: [green]{pubkey_path}[/green]", title="[bold blue]Remote SSH Key Deployment[/bold blue]", border_style="blue"))
    
    if not pubkey_path.exists():
        console.print(Panel(f"❌ Public key not found: {pubkey_path}", title="[bold red]Error[/bold red]", border_style="red"))
        return False
    
    pubkey_content = pubkey_path.read_text(encoding="utf-8").strip()
    if not pubkey_content:
        console.print(Panel("❌ Public key file is empty", title="[bold red]Error[/bold red]", border_style="red"))
        return False
    
    try:
        ssh = SSH(host=remote_target, username=None, hostname=None, ssh_key_path=None, password=password, port=22, enable_compression=False)
    except Exception as err:
        console.print(Panel(f"❌ Failed to connect to {remote_target}\n{err}", title="[bold red]Connection Error[/bold red]", border_style="red"))
        return False
    
    try:
        remote_os = ssh.remote_specs.get("system", "Linux")
        console.print(f"🖥️  Detected remote OS: [cyan]{remote_os}[/cyan]")
        
        if remote_os == "Windows":
            result = _deploy_to_windows_remote(ssh, pubkey_content)
        else:
            result = _deploy_to_unix_remote(ssh, pubkey_content)
        
        if result:
            console.print(Panel(f"✅ Key successfully deployed to [green]{ssh.get_remote_repr(add_machine=True)}[/green]", title="[bold green]Success[/bold green]", border_style="green", box=box.DOUBLE_EDGE))
        return result
    finally:
        ssh.close()


def _deploy_to_unix_remote(ssh: SSH, pubkey_content: str) -> bool:
    """Deploy key to Linux or macOS remote."""
    check_cmd = f'''
if [ -f ~/.ssh/authorized_keys ]; then
    if grep -qF "{pubkey_content}" ~/.ssh/authorized_keys 2>/dev/null; then
        echo "KEY_EXISTS"
    else
        echo "KEY_NOT_FOUND"
    fi
else
    echo "FILE_NOT_FOUND"
fi
'''
    resp = ssh.run_shell_cmd_on_remote(command=check_cmd, verbose_output=False, description="Checking existing keys", strict_stderr=False, strict_return_code=False)
    status = resp.op.strip()
    
    if status == "KEY_EXISTS":
        console.print("⚠️  [yellow]Key already exists on remote, skipping[/yellow]")
        return True
    
    if status == "FILE_NOT_FOUND":
        console.print("📁 Creating ~/.ssh directory and authorized_keys file")
        deploy_cmd = f'''
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "{pubkey_content}" > ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
echo "DEPLOYED"
'''
    else:
        console.print("➕ Appending key to existing authorized_keys")
        deploy_cmd = f'''
echo "{pubkey_content}" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
echo "DEPLOYED"
'''
    
    resp = ssh.run_shell_cmd_on_remote(command=deploy_cmd, verbose_output=False, description="Deploying SSH key", strict_stderr=False, strict_return_code=False)
    
    if "DEPLOYED" in resp.op:
        console.print("🔑 Key deployed successfully")
        _attempt_sshd_restart_unix(ssh)
        return True
    else:
        console.print(Panel(f"❌ Deployment failed\nOutput: {resp.op}\nError: {resp.err}", title="[bold red]Error[/bold red]", border_style="red"))
        return False


def _attempt_sshd_restart_unix(ssh: SSH) -> None:
    """Attempt to restart sshd on Linux/macOS. Non-fatal if it fails."""
    console.print("🔄 Attempting to restart SSH service...")
    
    restart_commands = ["sudo systemctl restart sshd 2>/dev/null || sudo systemctl restart ssh 2>/dev/null || sudo service ssh restart 2>/dev/null || sudo launchctl kickstart -k system/com.openssh.sshd 2>/dev/null || echo 'RESTART_SKIPPED'"]
    
    resp = ssh.run_shell_cmd_on_remote(command=restart_commands[0], verbose_output=False, description="Restarting SSH", strict_stderr=False, strict_return_code=False)
    
    if "RESTART_SKIPPED" in resp.op:
        console.print("⚠️  [yellow]Could not restart SSH service (may require manual restart or sudo password)[/yellow]")
    else:
        console.print("✅ SSH service restarted")


def _deploy_to_windows_remote(ssh: SSH, pubkey_content: str) -> bool:
    """Deploy key to Windows remote using Python script execution."""
    python_code = f'''
from pathlib import Path
import subprocess
import sys

sshd_dir = Path("C:/ProgramData/ssh")
admin_auth_keys = sshd_dir / "administrators_authorized_keys"
sshd_config = sshd_dir / "sshd_config"
key_content = """{pubkey_content}"""

if admin_auth_keys.exists():
    existing = admin_auth_keys.read_text(encoding="utf-8")
    if key_content in existing:
        print("KEY_EXISTS")
        sys.exit(0)
    if not existing.endswith("\\n"):
        existing += "\\n"
    admin_auth_keys.write_text(existing + key_content + "\\n", encoding="utf-8")
else:
    sshd_dir.mkdir(parents=True, exist_ok=True)
    admin_auth_keys.write_text(key_content + "\\n", encoding="utf-8")

icacls_cmd = f'icacls "{{admin_auth_keys}}" /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"'
subprocess.run(icacls_cmd, shell=True, check=False)

if sshd_config.exists():
    config_text = sshd_config.read_text(encoding="utf-8")
    if "#PubkeyAuthentication" in config_text:
        config_text = config_text.replace("#PubkeyAuthentication", "PubkeyAuthentication")
        sshd_config.write_text(config_text, encoding="utf-8")

subprocess.run("powershell -Command Restart-Service sshd -Force", shell=True, check=False)
print("DEPLOYED")
'''
    
    console.print("🪟 Deploying to Windows remote via Python script...")
    resp = ssh.run_py_remotely(python_code=python_code, uv_with=None, uv_project_dir=None, description="Deploying SSH key to Windows", verbose_output=False, strict_stderr=False, strict_return_code=False)
    
    if "KEY_EXISTS" in resp.op:
        console.print("⚠️  [yellow]Key already exists on remote, skipping[/yellow]")
        return True
    elif "DEPLOYED" in resp.op:
        console.print("🔑 Key deployed successfully to Windows remote")
        return True
    else:
        console.print(Panel(f"❌ Windows deployment failed\nOutput: {resp.op}\nError: {resp.err}", title="[bold red]Error[/bold red]", border_style="red"))
        return False


def deploy_multiple_keys_to_remote(remote_target: str, pubkey_paths: list[Path], password: Optional[str]) -> bool:
    """Deploy multiple public keys to a remote machine. Opens connection once."""
    console.print(Panel(f"🔐 Deploying {len(pubkey_paths)} key(s) to remote: [cyan]{remote_target}[/cyan]", title="[bold blue]Remote SSH Key Deployment[/bold blue]", border_style="blue"))
    
    all_keys_content: list[str] = []
    for p in pubkey_paths:
        if not p.exists():
            console.print(f"⚠️  [yellow]Skipping non-existent key: {p}[/yellow]")
            continue
        content = p.read_text(encoding="utf-8").strip()
        if content:
            all_keys_content.append(content)
            console.print(f"📄 Loaded: [green]{p.name}[/green]")
    
    if not all_keys_content:
        console.print(Panel("❌ No valid keys to deploy", title="[bold red]Error[/bold red]", border_style="red"))
        return False
    
    try:
        ssh = SSH(host=remote_target, username=None, hostname=None, ssh_key_path=None, password=password, port=22, enable_compression=False)
    except Exception as err:
        console.print(Panel(f"❌ Failed to connect to {remote_target}\n{err}", title="[bold red]Connection Error[/bold red]", border_style="red"))
        return False
    
    try:
        remote_os = ssh.remote_specs.get("system", "Linux")
        console.print(f"🖥️  Detected remote OS: [cyan]{remote_os}[/cyan]")
        
        success_count = 0
        for key_content in all_keys_content:
            if remote_os == "Windows":
                if _deploy_to_windows_remote(ssh, key_content):
                    success_count += 1
            else:
                if _deploy_to_unix_remote(ssh, key_content):
                    success_count += 1
        
        if success_count == len(all_keys_content):
            console.print(Panel(f"✅ All {success_count} key(s) deployed to [green]{ssh.get_remote_repr(add_machine=True)}[/green]", title="[bold green]Success[/bold green]", border_style="green", box=box.DOUBLE_EDGE))
            return True
        else:
            console.print(Panel(f"⚠️  Deployed {success_count}/{len(all_keys_content)} keys", title="[bold yellow]Partial Success[/bold yellow]", border_style="yellow"))
            return success_count > 0
    finally:
        ssh.close()
