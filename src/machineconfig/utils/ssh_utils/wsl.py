import platform
import re
import shutil
import subprocess
from pathlib import Path

from machineconfig.utils.ssh_utils.wsl_helper import (
    ensure_relative_path,
    remove_path,
    ensure_wsl_environment,
    ensure_windows_environment,
    ensure_linux_environment,
    resolve_windows_home_from_wsl,
    resolve_wsl_home_on_windows,
    run_windows_copy_command,
    ensure_symlink,
    normalize_port_spec_for_firewall,
)


def copy_when_inside_wsl(source: Path | str, target: Path | str, overwrite: bool, windows_username: str | None) -> None:
    ensure_wsl_environment()
    source_relative = ensure_relative_path(source)
    target_relative = ensure_relative_path(target)
    source_path = Path.home() / source_relative
    target_path = resolve_windows_home_from_wsl(windows_username) / target_relative
    if not source_path.exists():
        raise FileNotFoundError(source_path)
    if target_path.exists():
        if not overwrite:
            raise FileExistsError(target_path)
        remove_path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if source_path.is_dir():
        shutil.copytree(source_path, target_path, dirs_exist_ok=False)
        return
    print(f"Copying {source_path} to {target_path}")
    shutil.copy2(source_path, target_path)


def copy_when_inside_windows(source: Path | str, target: Path | str, overwrite: bool) -> None:
    ensure_windows_environment()
    source_relative = ensure_relative_path(source)
    target_relative = ensure_relative_path(target)
    source_path = Path.home() / source_relative
    target_path = resolve_wsl_home_on_windows() / target_relative
    if not source_path.exists():
        raise FileNotFoundError(source_path)
    if target_path.exists():
        if not overwrite:
            raise FileExistsError(target_path)
        remove_path(target_path)
    run_windows_copy_command(source_path, target_path)


def link_wsl_and_windows(windows_username: str | None) -> None:
    system = platform.system()
    if system == "Darwin":
        raise RuntimeError("link_wsl_and_windows is not designed for macOS")
    try:
        ensure_wsl_environment()
    except RuntimeError:
        try:
            ensure_windows_environment()
        except RuntimeError as exc:
            raise RuntimeError("link_wsl_and_windows must run inside Windows or WSL") from exc
        print("🔗 Running inside Windows, linking to WSL home...")
        target_path = resolve_wsl_home_on_windows()
        link_path = Path.home() / "wsl"
        created = ensure_symlink(link_path, target_path)
        if created:
            print(f"✅ Created symlink: {link_path} -> {target_path}")
        else:
            print(f"✅ Symlink already exists: {link_path} -> {target_path}")
        return
    print("🔗 Running inside WSL, linking to Windows home...")
    target_path = resolve_windows_home_from_wsl(windows_username)
    link_path = Path.home() / "win"
    created = ensure_symlink(link_path, target_path)
    if created:
        print(f"✅ Created symlink: {link_path} -> {target_path}")
    else:
        print(f"✅ Symlink already exists: {link_path} -> {target_path}")


def open_wsl_port(ports_spec: str) -> None:
    ensure_windows_environment()
    normalized_ports, description = normalize_port_spec_for_firewall(ports_spec)
    rule_name = f"WSL Ports {description}"
    # Build PowerShell array syntax for -LocalPort parameter (e.g., @('3000-4000','8080'))
    port_parts = normalized_ports.split(",")
    ps_array = "@(" + ",".join(f"'{p}'" for p in port_parts) + ")"
    script = f"New-NetFirewallRule -DisplayName '{rule_name}' -Direction Inbound -LocalPort {ps_array} -Protocol TCP -Action Allow"
    print(f"🔥 Opening firewall for ports: {description}...")
    result = subprocess.run(["powershell.exe", "-NoLogo", "-NoProfile", "-Command", script], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Firewall rule created for ports: {description}")
    else:
        print(f"❌ Failed to create firewall rule: {result.stderr.strip()}")


def change_ssh_port(port: int) -> None:
    ensure_linux_environment()
    if port < 1 or port > 65535:
        raise ValueError(f"Invalid port number: {port}")

    sshd_config = Path("/etc/ssh/sshd_config")
    if not sshd_config.exists():
        raise FileNotFoundError(f"SSH config file not found: {sshd_config}")

    print(f"🔧 Changing SSH port to {port}...")

    content = sshd_config.read_text()
    new_content = re.sub(r"^#?\s*Port\s+\d+", f"Port {port}", content, flags=re.MULTILINE)
    if f"Port {port}" not in new_content:
        new_content = f"Port {port}\n" + new_content

    print(f"📝 Updating {sshd_config}...")
    result = subprocess.run(["sudo", "tee", str(sshd_config)], input=new_content.encode(), capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to update sshd_config: {result.stderr.decode()}")
    print(f"✅ Updated {sshd_config}")

    override_dir = Path("/etc/systemd/system/ssh.socket.d")
    override_file = override_dir / "override.conf"
    override_content = f"""[Socket]
ListenStream=
ListenStream={port}
"""
    print(f"📝 Creating systemd socket override at {override_file}...")
    subprocess.run(["sudo", "mkdir", "-p", str(override_dir)], check=True)
    result = subprocess.run(["sudo", "tee", str(override_file)], input=override_content.encode(), capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to create override file: {result.stderr.decode()}")
    print("✅ Created systemd socket override")

    print("🔄 Restarting SSH services...")
    subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
    subprocess.run(["sudo", "systemctl", "restart", "ssh.socket"], check=False)
    subprocess.run(["sudo", "service", "ssh", "restart"], check=False)
    print(f"✅ SSH port changed to {port}")
    print(f"⚠️  Remember to open port {port} in Windows Firewall if running in WSL")


if __name__ == "__main__":
    copy_when_inside_wsl(Path("projects/source.txt"), Path("windows_projects/source.txt"), overwrite=True, windows_username=None)
    copy_when_inside_windows(Path("documents/example.txt"), Path("linux_documents/example.txt"), overwrite=True)
