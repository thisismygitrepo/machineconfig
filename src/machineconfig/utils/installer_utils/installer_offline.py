
from pathlib import Path


BINARIES: list[str] = [
    "devops", "cloud", "agents", "sessions", "ftpx", "fire", "croshell", "utils", "msearch", "explore",
    "bat",
    "cpz",
    "duckdb",
    "gitcs",
    "hyperfine",
    "lazysql",
    "procs",
    "rmz",
    "tv",
    "watchexec",
    "zellij",
    "broot",
    "delta",
    "fastfetch",
    "gitui",
    "jq",
    "lsd",
    "rainfrog",
    "rusty-rain",
    "uv",
    "ya",
    "zoxide",
    "btm",
    "diskonaut",
    "fd",
    "glow",
    "lazydocker",
    "miniserve",
    "rg",
    "starship",
    "uvx",
    "yazi",
    "cpufetch",
    "dua",
    "fzf",
    "hx",
    "lazygit",
    "ouch",
    "rga",
    "tere",
    "viu",
    "yq",
]


def export() -> None:
    import platform
    import shutil

    os_name = platform.system().lower()
    arch = platform.machine().lower()
    system_name = platform.system()

    res_root = Path.home().joinpath("tmp_results", f"installer_offline-{os_name}-{arch}")
    if res_root.exists():
        shutil.rmtree(res_root)
    res_root.mkdir(parents=True, exist_ok=True)

    binaries_root = res_root.joinpath("binaries")
    binaries_root.mkdir(parents=True, exist_ok=True)
    configs_root = res_root.joinpath("configs")
    configs_root.mkdir(parents=True, exist_ok=True)

    from machineconfig.utils.source_of_truth import CONFIG_ROOT, LINUX_INSTALL_PATH, WINDOWS_INSTALL_PATH

    if system_name in ["Linux", "Darwin"]:
        install_path = Path(LINUX_INSTALL_PATH)
        for binary in BINARIES:
            src = install_path.joinpath(binary)
            if src.exists():
                dst = binaries_root.joinpath(binary)
                shutil.copy2(src, dst)
            else:
                print(f"Warning: {binary} not found in {LINUX_INSTALL_PATH}, skipping export.")
    elif system_name == "Windows":
        install_path = Path(WINDOWS_INSTALL_PATH)
        for binary in BINARIES:
            src = install_path.joinpath(f"{binary}.exe")
            if src.exists():
                dst = binaries_root.joinpath(f"{binary}.exe")
                shutil.copy2(src, dst)
            else:
                print(f"Warning: {binary} not found in {WINDOWS_INSTALL_PATH}, skipping export.")
    else:
        print(f"Unsupported platform: {system_name}. No binaries exported.")

    if CONFIG_ROOT.exists():
        shutil.copytree(CONFIG_ROOT, configs_root, dirs_exist_ok=True)
        print(f"Exported configs from {CONFIG_ROOT} to {configs_root}")
    else:
        print(f"Warning: Config root {CONFIG_ROOT} does not exist, skipping config export.")

    if system_name in ["Linux", "Darwin"]:
        sh_script = f"""#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
BINS_DIR="$SCRIPT_DIR/binaries"
CONFIGS_DIR="$SCRIPT_DIR/configs"
INSTALL_PATH="{LINUX_INSTALL_PATH}"
CONFIG_ROOT="{CONFIG_ROOT}"

if [ -d "$BINS_DIR" ]; then
    mkdir -p "$INSTALL_PATH"
    cp -f "$BINS_DIR"/* "$INSTALL_PATH"/ 2>/dev/null || true
else
    printf "%s\n" "Warning: $BINS_DIR not found, skipping binaries"
fi

if [ -d "$CONFIGS_DIR" ]; then
    mkdir -p "$CONFIG_ROOT"
    cp -R -f "$CONFIGS_DIR"/* "$CONFIG_ROOT"/ 2>/dev/null || true
else
    printf "%s\n" "Warning: $CONFIGS_DIR not found, skipping configs"
fi
"""
        res_root.joinpath("install.sh").write_text(sh_script, encoding="utf-8")
    elif system_name == "Windows":
        ps1_script = f"""$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BinariesDir = Join-Path $ScriptDir "binaries"
$ConfigsDir = Join-Path $ScriptDir "configs"
$InstallPath = "{WINDOWS_INSTALL_PATH}"
$ConfigRoot = "{CONFIG_ROOT}"

if (Test-Path $BinariesDir) {{
    New-Item -ItemType Directory -Force -Path $InstallPath | Out-Null
    Get-ChildItem -Path $BinariesDir -File | ForEach-Object {{
        Copy-Item -Path $_.FullName -Destination $InstallPath -Force
    }}
}} else {{
    Write-Host "Warning: $BinariesDir not found, skipping binaries"
}}

if (Test-Path $ConfigsDir) {{
    New-Item -ItemType Directory -Force -Path $ConfigRoot | Out-Null
    Copy-Item -Path (Join-Path $ConfigsDir "*") -Destination $ConfigRoot -Recurse -Force
}} else {{
    Write-Host "Warning: $ConfigsDir not found, skipping configs"
}}
"""
        res_root.joinpath("install.ps1").write_text(ps1_script, encoding="utf-8")

    archive_base = res_root.parent.joinpath(res_root.name)
    shutil.make_archive(archive_base.as_posix(), "zip", root_dir=res_root)
    shutil.rmtree(res_root)


if __name__ == "__main__":
    export()
