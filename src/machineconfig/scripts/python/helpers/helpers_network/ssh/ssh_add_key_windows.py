from pathlib import Path
import subprocess


def add_ssh_key_windows(path_to_key: Path) -> None:
    sshd_dir = Path("C:/ProgramData/ssh")
    admin_auth_keys = sshd_dir / "administrators_authorized_keys"
    sshd_config = sshd_dir / "sshd_config"
    key_content = path_to_key.read_text(encoding="utf-8").strip()
    if admin_auth_keys.exists():
        existing = admin_auth_keys.read_text(encoding="utf-8")
        if not existing.endswith("\n"):
            existing += "\n"
        admin_auth_keys.write_text(existing + key_content + "\n", encoding="utf-8")
    else:
        admin_auth_keys.write_text(key_content + "\n", encoding="utf-8")
    icacls_cmd = f'icacls "{admin_auth_keys}" /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"'
    subprocess.run(icacls_cmd, shell=True, check=True)
    if sshd_config.exists():
        config_text = sshd_config.read_text(encoding="utf-8")
        config_text = config_text.replace("#PubkeyAuthentication", "PubkeyAuthentication")
        sshd_config.write_text(config_text, encoding="utf-8")
    subprocess.run("Restart-Service sshd -Force", shell=True, check=True)
