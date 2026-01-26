from pathlib import Path
import subprocess


def run_cmd(cmd: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return result.returncode == 0, result.stdout.strip()
    except FileNotFoundError:
        return False, ""


def check_sshd_installed() -> tuple[bool, str]:
    sshd_paths = ["/usr/sbin/sshd", "/usr/bin/sshd", "/sbin/sshd", "/opt/homebrew/sbin/sshd", "/usr/local/sbin/sshd"]
    for path in sshd_paths:
        if Path(path).exists():
            return True, path
    ok, which_out = run_cmd(["which", "sshd"])
    if ok and which_out:
        return True, which_out
    return False, ""
