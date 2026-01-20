from pathlib import Path
import subprocess


def run_powershell(cmd: str) -> tuple[bool, str]:
    result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, check=False)
    return result.returncode == 0, result.stdout.strip()


def check_sshd_binary_exists() -> tuple[bool, str]:
    sshd_locations = [
        Path("C:/Windows/System32/OpenSSH/sshd.exe"),
        Path("C:/Program Files/OpenSSH/sshd.exe"),
        Path("C:/Program Files (x86)/OpenSSH/sshd.exe"),
    ]
    for loc in sshd_locations:
        if loc.exists():
            return True, str(loc)
    ok, which_out = run_powershell("Get-Command sshd -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source")
    if ok and which_out:
        return True, which_out
    return False, ""


def detect_openssh() -> tuple[str, Path | None, Path | None]:
    capability_sshd = Path("C:/Windows/System32/OpenSSH/sshd.exe")
    winget_sshd = Path("C:/Program Files/OpenSSH/sshd.exe")
    programdata_config = Path("C:/ProgramData/ssh")
    capability_config = Path("C:/ProgramData/ssh")
    if capability_sshd.exists():
        return ("capability", capability_sshd, capability_config)
    if winget_sshd.exists():
        return ("winget", winget_sshd, programdata_config)
    return ("not_found", None, None)
