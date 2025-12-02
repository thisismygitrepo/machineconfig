import os
import platform
import stat
import shutil
import subprocess
from pathlib import Path, PureWindowsPath


def ensure_relative_path(requested: Path | str) -> Path:
    path = Path(requested)
    if path.is_absolute():
        raise ValueError("paths must be relative to the home directory")
    if any(part == ".." for part in path.parts):
        raise ValueError("paths must stay within the home directory")
    return path


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    shutil.rmtree(path)


def ensure_wsl_environment() -> None:
    if os.environ.get("WSL_DISTRO_NAME"):
        return
    if "microsoft" in platform.release().lower():
        return
    raise RuntimeError("copy_when_inside_wsl must run inside WSL")


def ensure_windows_environment() -> None:
    if os.name != "nt":
        raise RuntimeError("copy_when_inside_windows must run inside Windows")
    if os.environ.get("WSL_DISTRO_NAME"):
        raise RuntimeError("copy_when_inside_windows must run inside Windows")


def ensure_linux_environment() -> None:
    if platform.system() != "Linux":
        raise RuntimeError("change_ssh_port requires Linux environment")


def infer_windows_home_from_permissions(windows_username: str | None) -> Path:
    base_dir = Path("/mnt/c/Users")
    try:
        entries = list(base_dir.iterdir())
    except FileNotFoundError as exc:
        raise RuntimeError("unable to find /mnt/c/Users") from exc
    if windows_username:
        candidate = base_dir / windows_username
        if candidate.is_dir():
            return candidate
        raise RuntimeError(f"specified Windows user directory not found: {candidate}")
    candidates: list[Path] = []
    for entry in entries:
        if not entry.is_dir():
            continue
        if entry.name.lower() == "public" or entry.name.lower() == "all users":
            continue
        try:
            mode = stat.S_IMODE(entry.stat().st_mode)
        except OSError:
            continue
        if mode == 0o777:
            candidates.append(entry)
    if len(candidates) != 1:
        wsl_user = os.environ.get("USER") or os.environ.get("LOGNAME")
        if wsl_user:
            for candidate in candidates:
                if candidate.name == wsl_user:
                    return candidate
        non_default = [c for c in candidates if c.name.lower() not in ("default", "default user")]
        if len(non_default) == 1:
            return non_default[0]
        options = ", ".join(sorted(candidate.name for candidate in candidates)) or "none"
        raise RuntimeError(f"unable to infer Windows home directory (candidates: {options})")
    return candidates[0]


def resolve_windows_home_from_wsl(windows_username: str | None) -> Path:
    if windows_username:
        return infer_windows_home_from_permissions(windows_username)
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        windows_path = PureWindowsPath(user_profile)
        drive = windows_path.drive
        if drive:
            drive_letter = drive.rstrip(":").lower()
            tail = Path(*windows_path.parts[1:])
            candidate = Path("/mnt") / drive_letter / tail
            if candidate.exists():
                return candidate
    return infer_windows_home_from_permissions(windows_username)


def decode_wsl_output(raw_bytes: bytes) -> str:
    try:
        return raw_bytes.decode("utf-16-le")
    except UnicodeDecodeError:
        return raw_bytes.decode()


def get_single_wsl_distribution() -> str:
    process = subprocess.run(["wsl.exe", "-l"], capture_output=True, text=False, check=True)
    stdout = decode_wsl_output(process.stdout).replace("\ufeff", "")
    distributions: list[str] = []
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line or line.lower().startswith("windows subsystem for linux"):
            continue
        normalized = line.lstrip("* ").replace("(Default)", "").strip()
        if normalized:
            distributions.append(normalized)
    if len(distributions) != 1:
        raise RuntimeError("unable to pick a single WSL distribution")
    return distributions[0]


def resolve_wsl_home_on_windows() -> Path:
    distribution = get_single_wsl_distribution()
    home_root = Path(rf"\\wsl$\{distribution}\home")
    try:
        entries = list(home_root.iterdir())
    except FileNotFoundError as exc:
        raise RuntimeError(f"unable to locate WSL home directories for {distribution}") from exc
    except OSError as exc:
        raise RuntimeError(f"unable to inspect WSL home directories for {distribution}") from exc
    user_dirs = [entry for entry in entries if entry.is_dir()]
    if len(user_dirs) != 1:
        options = ", ".join(sorted(entry.name for entry in user_dirs)) or "none"
        raise RuntimeError(f"unable to infer WSL user directory (candidates: {options})")
    return user_dirs[0]


def quote_for_powershell(path: Path) -> str:
    return "'" + str(path).replace("'", "''") + "'"


def run_windows_copy_command(source_path: Path, target_path: Path) -> None:
    source_is_dir = source_path.is_dir()
    parent_literal = quote_for_powershell(target_path.parent)
    source_literal = quote_for_powershell(source_path)
    target_literal = quote_for_powershell(target_path)
    script = (
        "$ErrorActionPreference = 'Stop'; "
        f"New-Item -ItemType Directory -Path {parent_literal} -Force | Out-Null; "
        f"Copy-Item -LiteralPath {source_literal} -Destination {target_literal}"
        f"{' -Recurse' if source_is_dir else ''} -Force"
    )
    print(f"Copying {source_path} to {target_path}")
    subprocess.run(["powershell.exe", "-NoLogo", "-NoProfile", "-Command", script], check=True)


def ensure_symlink(link_path: Path, target_path: Path) -> bool:
    if not target_path.exists():
        raise FileNotFoundError(target_path)
    if link_path.is_symlink():
        existing_target = Path(os.path.realpath(link_path))
        desired_target = Path(os.path.realpath(target_path))
        if os.path.normcase(str(existing_target)) == os.path.normcase(str(desired_target)):
            return False
        link_path.unlink()
    elif link_path.exists():
        raise FileExistsError(link_path)
    link_path.symlink_to(target_path, target_is_directory=True)
    return True


def parse_port_spec(port_spec: str) -> list[int]:
    ports: list[int] = []
    for part in port_spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            range_parts = part.split("-", maxsplit=1)
            start = int(range_parts[0].strip())
            end = int(range_parts[1].strip())
            if start > end:
                raise ValueError(f"Invalid port range: {part} (start > end)")
            ports.extend(range(start, end + 1))
        else:
            ports.append(int(part))
    return ports


def normalize_port_spec_for_firewall(port_spec: str) -> tuple[str, str]:
    """Validates and normalizes port spec for New-NetFirewallRule -LocalPort parameter.
    Returns (normalized_spec, human_readable_description).
    New-NetFirewallRule natively supports ranges (e.g. '5000-5020') and comma-separated values.
    """
    parts: list[str] = []
    for raw_part in port_spec.split(","):
        part = raw_part.strip()
        if not part:
            continue
        if "-" in part:
            range_parts = part.split("-", maxsplit=1)
            start = int(range_parts[0].strip())
            end = int(range_parts[1].strip())
            if start < 1 or start > 65535 or end < 1 or end > 65535:
                raise ValueError(f"Port numbers must be between 1 and 65535: {part}")
            if start > end:
                raise ValueError(f"Invalid port range: {part} (start > end)")
            parts.append(f"{start}-{end}")
        else:
            port = int(part)
            if port < 1 or port > 65535:
                raise ValueError(f"Invalid port number: {port}")
            parts.append(str(port))
    if not parts:
        raise ValueError("No valid ports provided")
    normalized = ",".join(parts)
    description = normalized.replace(",", ", ")
    return normalized, description
