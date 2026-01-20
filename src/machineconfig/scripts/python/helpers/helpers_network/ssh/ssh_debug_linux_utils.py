from pathlib import Path
import subprocess


def run_cmd(cmd: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return result.returncode == 0, result.stdout.strip()
    except FileNotFoundError:
        return False, ""


def check_sshd_installed() -> tuple[bool, str]:
    sshd_paths = ["/usr/sbin/sshd", "/usr/bin/sshd", "/sbin/sshd"]
    for path in sshd_paths:
        if Path(path).exists():
            return True, path
    ok, which_out = run_cmd(["which", "sshd"])
    if ok and which_out:
        return True, which_out
    return False, ""


def detect_package_manager() -> tuple[str, str]:
    if Path("/usr/bin/apt").exists() or Path("/usr/bin/apt-get").exists():
        return "apt", "sudo apt update && sudo apt install -y openssh-server"
    if Path("/usr/bin/dnf").exists():
        return "dnf", "sudo dnf install -y openssh-server"
    if Path("/usr/bin/yum").exists():
        return "yum", "sudo yum install -y openssh-server"
    if Path("/usr/bin/pacman").exists():
        return "pacman", "sudo pacman -S --noconfirm openssh"
    if Path("/usr/bin/zypper").exists():
        return "zypper", "sudo zypper install -y openssh"
    return "unknown", "# Install openssh-server using your package manager"
