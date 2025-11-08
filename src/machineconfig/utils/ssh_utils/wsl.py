import os
import platform
import stat
import shutil
import subprocess
from pathlib import Path, PureWindowsPath


def _ensure_relative_path(requested: Path | str) -> Path:
    path = Path(requested)
    if path.is_absolute():
        raise ValueError("paths must be relative to the home directory")
    if any(part == ".." for part in path.parts):
        raise ValueError("paths must stay within the home directory")
    return path


def _remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    shutil.rmtree(path)


def _ensure_wsl_environment() -> None:
    if os.environ.get("WSL_DISTRO_NAME"):
        return
    if "microsoft" in platform.release().lower():
        return
    raise RuntimeError("copy_when_inside_wsl must run inside WSL")


def _ensure_windows_environment() -> None:
    if os.name != "nt":
        raise RuntimeError("copy_when_inside_windows must run inside Windows")
    if os.environ.get("WSL_DISTRO_NAME"):
        raise RuntimeError("copy_when_inside_windows must run inside Windows")


def _infer_windows_home_from_permissions() -> Path:
    base_dir = Path("/mnt/c/Users")
    try:
        entries = list(base_dir.iterdir())
    except FileNotFoundError as exc:
        raise RuntimeError("unable to find /mnt/c/Users") from exc
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
        options = ", ".join(sorted(candidate.name for candidate in candidates)) or "none"
        raise RuntimeError(f"unable to infer Windows home directory (candidates: {options})")
    return candidates[0]


def _resolve_windows_home_from_wsl() -> Path:
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
    return _infer_windows_home_from_permissions()


def _decode_wsl_output(raw_bytes: bytes) -> str:
    try:
        return raw_bytes.decode("utf-16-le")
    except UnicodeDecodeError:
        return raw_bytes.decode()


def _get_single_wsl_distribution() -> str:
    process = subprocess.run(["wsl.exe", "-l"], capture_output=True, text=False, check=True)
    stdout = _decode_wsl_output(process.stdout).replace("\ufeff", "")
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


def _resolve_wsl_home_on_windows() -> Path:
    distribution = _get_single_wsl_distribution()
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


def _quote_for_powershell(path: Path) -> str:
    return "'" + str(path).replace("'", "''") + "'"


def _run_windows_copy_command(source_path: Path, target_path: Path) -> None:
    source_is_dir = source_path.is_dir()
    parent_literal = _quote_for_powershell(target_path.parent)
    source_literal = _quote_for_powershell(source_path)
    target_literal = _quote_for_powershell(target_path)
    script = (
        "$ErrorActionPreference = 'Stop'; "
        f"New-Item -ItemType Directory -Path {parent_literal} -Force | Out-Null; "
        f"Copy-Item -LiteralPath {source_literal} -Destination {target_literal}"
        f"{' -Recurse' if source_is_dir else ''} -Force"
    )
    print(f"Copying {source_path} to {target_path}")
    subprocess.run(
        ["powershell.exe", "-NoLogo", "-NoProfile", "-Command", script],
        check=True,
    )


def _ensure_symlink(link_path: Path, target_path: Path) -> None:
    if not target_path.exists():
        raise FileNotFoundError(target_path)
    if link_path.is_symlink():
        existing_target = Path(os.path.realpath(link_path))
        desired_target = Path(os.path.realpath(target_path))
        if os.path.normcase(str(existing_target)) == os.path.normcase(str(desired_target)):
            return
        link_path.unlink()
    elif link_path.exists():
        raise FileExistsError(link_path)
    link_path.symlink_to(target_path, target_is_directory=True)


def copy_when_inside_wsl(source: Path | str, target: Path | str, overwrite: bool) -> None:
    _ensure_wsl_environment()
    source_relative = _ensure_relative_path(source)
    target_relative = _ensure_relative_path(target)
    source_path = Path.home() / source_relative
    target_path = _resolve_windows_home_from_wsl() / target_relative
    if not source_path.exists():
        raise FileNotFoundError(source_path)
    if target_path.exists():
        if not overwrite:
            raise FileExistsError(target_path)
        _remove_path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if source_path.is_dir():
        shutil.copytree(source_path, target_path, dirs_exist_ok=False)
        return
    print(f"Copying {source_path} to {target_path}")
    shutil.copy2(source_path, target_path)


def copy_when_inside_windows(source: Path | str, target: Path | str, overwrite: bool) -> None:
    _ensure_windows_environment()
    source_relative = _ensure_relative_path(source)
    target_relative = _ensure_relative_path(target)
    source_path = Path.home() / source_relative
    target_path = _resolve_wsl_home_on_windows() / target_relative
    if not source_path.exists():
        raise FileNotFoundError(source_path)
    if target_path.exists():
        if not overwrite:
            raise FileExistsError(target_path)
        _remove_path(target_path)
    _run_windows_copy_command(source_path, target_path)


def link_wsl_and_windows() -> None:
    system = platform.system()
    if system == "Darwin":
        raise RuntimeError("link_wsl_and_windows is not designed for macOS")
    try:
        _ensure_wsl_environment()
    except RuntimeError:
        try:
            _ensure_windows_environment()
        except RuntimeError as exc:
            raise RuntimeError("link_wsl_and_windows must run inside Windows or WSL") from exc
        target_path = _resolve_wsl_home_on_windows()
        link_path = Path.home() / "wsl"
        _ensure_symlink(link_path, target_path)
        return
    target_path = _resolve_windows_home_from_wsl()
    link_path = Path.home() / "win"
    _ensure_symlink(link_path, target_path)


if __name__ == "__main__":
    copy_when_inside_wsl(Path("projects/source.txt"), Path("windows_projects/source.txt"), True)
    copy_when_inside_windows(Path("documents/example.txt"), Path("linux_documents/example.txt"), True)