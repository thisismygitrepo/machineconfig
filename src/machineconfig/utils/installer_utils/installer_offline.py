
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import typer


def export() -> None:
    import platform
    import shutil
    # getting os and arch
    os_name = platform.system().lower()
    arch = platform.machine().lower()

    res_root = Path.home().joinpath("tmp_results", f"installer_offline-{os_name}-{arch}")
    if res_root.exists():
        shutil.rmtree(res_root)
    res_root.mkdir(parents=True, exist_ok=True)

    binaries_root = res_root.joinpath("binaries")
    binaries_root.mkdir(parents=True, exist_ok=True)
    configs_root = res_root.joinpath("configs")
    configs_root.mkdir(parents=True, exist_ok=True)

    binaries: list[str] = [
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

    if platform.system() in ["Linux", "Darwin"]:
        from machineconfig.utils.source_of_truth import LINUX_INSTALL_PATH
        for binary in binaries:
            src = Path(LINUX_INSTALL_PATH).joinpath(binary)
            if src.exists():
                dst = binaries_root.joinpath(binary)
                shutil.copy2(src, dst)
                # print(f"Exported {binary} to {dst}")
            else:
                print(f"Warning: {binary} not found in {LINUX_INSTALL_PATH}, skipping export.")
    elif platform.system() == "Windows":
        from machineconfig.utils.source_of_truth import WINDOWS_INSTALL_PATH
        for binary in binaries:
            src = Path(WINDOWS_INSTALL_PATH).joinpath(binary + ".exe")
            if src.exists():
                dst = binaries_root.joinpath(binary + ".exe")
                shutil.copy2(src, dst)
                # print(f"Exported {binary} to {dst}")
            else:
                print(f"Warning: {binary} not found in {WINDOWS_INSTALL_PATH}, skipping export.")
    else:
        print(f"Unsupported platform: {platform.system()}. No binaries exported.")


    from machineconfig.utils.source_of_truth import CONFIG_ROOT
    if CONFIG_ROOT.exists():
        shutil.copytree(CONFIG_ROOT, configs_root, dirs_exist_ok=True)
        print(f"Exported configs from {CONFIG_ROOT} to {configs_root}")
    else:
        print(f"Warning: Config root {CONFIG_ROOT} does not exist, skipping config export.")

        from machineconfig.utils.source_of_truth import LINUX_INSTALL_PATH, WINDOWS_INSTALL_PATH
        if platform.system() in ["Linux", "Darwin"]:
                sh_script = (
                        f"""#!/usr/bin/env sh
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
                )
                res_root.joinpath("install.sh").write_text(sh_script, encoding="utf-8")
        elif platform.system() == "Windows":
                ps1_script = (
                        f"""$ErrorActionPreference = "Stop"

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
                )
                res_root.joinpath("install.ps1").write_text(ps1_script, encoding="utf-8")


def import_binaries_and_configs(zip_path: str, overwrite_configs: bool, overwrite_binaries: bool) -> None:
    zip_path_obj = Path(zip_path)
    if not zip_path_obj.exists():
        print(f"Error: Zip file {zip_path} does not exist.")
        return

    # checking if os and arch match
    import platform
    os_name = platform.system().lower()
    arch = platform.machine().lower()
    file_name = zip_path_obj.stem
    if os_name not in file_name or arch not in file_name:
        print(f"Error: Zip file name {file_name} does not contain expected OS ({os_name}) and architecture ({arch}). Aborting import.")
        return

    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(zip_path_obj.parent)

    # copy binaries to their respective install locations and configs to config location

    extracted_root = zip_path_obj.parent.joinpath(zip_path_obj.stem)
    binaries_root = extracted_root.joinpath("binaries")
    configs_root = extracted_root.joinpath("configs")

    from machineconfig.utils.source_of_truth import CONFIG_ROOT, LINUX_INSTALL_PATH, WINDOWS_INSTALL_PATH
    import shutil
    if binaries_root.exists():
        if platform.system() in ["Linux", "Darwin"]:
            for binary in binaries_root.iterdir():
                dst = Path(LINUX_INSTALL_PATH).joinpath(binary.name)
                if dst.exists() and not overwrite_binaries:
                    print(f"Warning: {dst} already exists and overwrite_binaries is False. Skipping {binary.name}.")
                    continue
                shutil.copy2(binary, dst)
                print(f"Imported {binary.name} to {dst}")
        elif platform.system() == "Windows":
            for binary in binaries_root.iterdir():
                dst = Path(WINDOWS_INSTALL_PATH).joinpath(binary.name)
                if dst.exists() and not overwrite_binaries:
                    print(f"Warning: {dst} already exists and overwrite_binaries is False. Skipping {binary.name}.")
                    continue
                shutil.copy2(binary, dst)
                print(f"Imported {binary.name} to {dst}")
    else:
        print(f"Warning: Binaries folder {binaries_root} does not exist, skipping binary import.")

    if configs_root.exists():
        if CONFIG_ROOT.exists() and not overwrite_configs:
            print(f"Warning: {CONFIG_ROOT} already exists and overwrite_configs is False. Skipping config import.")
        else:
            shutil.copytree(configs_root, CONFIG_ROOT, dirs_exist_ok=True)
            print(f"Imported configs from {configs_root} to {CONFIG_ROOT}")
    else:
        print(f"Warning: Configs folder {configs_root} does not exist, skipping config import.")


def get_app() -> "typer.Typer":
    import typer
    app = typer.Typer(help="Installer Offline - Export and Import binaries and configs for offline installation",
    no_args_is_help=True,

    )
    app.command(name="export", help="[e] Export binaries and configs", 
            no_args_is_help=False, )(export)
    app.command(name="e", help="[e] Export binaries and configs", 
            no_args_is_help=False, hidden=True)(export)
    app.command(name="import", help="[i] Import binaries and configs", 
            no_args_is_help=True, )(import_binaries_and_configs)
    app.command(name="i", help="[i] Import binaries and configs", 
            no_args_is_help=True, hidden=True)(import_binaries_and_configs)
    
    return app


if __name__ == "__main__":
    export()
