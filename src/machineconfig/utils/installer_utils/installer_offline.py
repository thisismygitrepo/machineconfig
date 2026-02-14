from pathlib import Path
from typing import Iterable

UV_TOOL_BINARIES: list[str] = [
        "devops", "cloud", "agents", "sessions", "ftpx", "fire", "croshell", "utils", "msearch", "explore",
]
UV_TOOL_NAME = "machineconfig"
UV_TOOLS_ROOT = Path.home().joinpath(".local/share/uv/tools")
UV_PYTHON_ROOT = Path.home().joinpath(".local/share/uv/python")

BUN_BINARIES: list[str] = [
    "bun",
    "bunx",
]
BINARIES: list[str] = [
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




def _read_uv_python_home(tool_root: Path) -> Path | None:
    pyvenv_cfg = tool_root.joinpath("pyvenv.cfg")
    if not pyvenv_cfg.exists():
        return None
    for line in pyvenv_cfg.read_text(encoding="utf-8").splitlines():
        if line.startswith("home = "):
            home_path = line.split("=", 1)[1].strip()
            if home_path:
                return Path(home_path)
    return None


def _read_uv_python_bin_name(tool_root: Path) -> str | None:
    python_link = tool_root.joinpath("bin/python")
    if not python_link.is_symlink():
        return None
    try:
        target = python_link.readlink()
    except OSError:
        return None
    target_path = target if target.is_absolute() else (python_link.parent / target)
    return target_path.name if target_path.name else None


def _collect_uv_tool_links(install_path: Path, tool_root: Path) -> list[str]:
    if not install_path.exists():
        return []
    tool_root_resolved = tool_root.resolve()
    links: list[str] = []
    for entry in install_path.iterdir():
        if not entry.is_symlink():
            continue
        try:
            target = entry.readlink()
        except OSError:
            continue
        target_path = target if target.is_absolute() else (entry.parent / target)
        try:
            resolved = target_path.resolve()
        except OSError:
            resolved = target_path
        if str(resolved).startswith(str(tool_root_resolved)):
            links.append(entry.name)
    return sorted(set(links))


def _write_uv_manifest(res_root: Path, python_dir: str, python_bin: str, link_names: Iterable[str]) -> None:
    manifest_path = res_root.joinpath("uv_bundle/uv_manifest.env")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        f"""TOOL_NAME={UV_TOOL_NAME}
PYTHON_DIR={python_dir}
PYTHON_BIN={python_bin}
""",
        encoding="utf-8",
    )
    links_path = res_root.joinpath("uv_bundle/uv_links.txt")
    links_path.write_text("\n".join(link_names) + "\n", encoding="utf-8")




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
        tool_root = UV_TOOLS_ROOT.joinpath(UV_TOOL_NAME)
        if tool_root.exists():
            python_home = _read_uv_python_home(tool_root)
            python_bin = _read_uv_python_bin_name(tool_root)
            if python_home is None or python_bin is None:
                print(f"Warning: uv tool {tool_root} missing python info, skipping uv export.")
            else:
                python_root = python_home.parent
                links = _collect_uv_tool_links(install_path=install_path, tool_root=tool_root)
                if len(links) == 0:
                    links = [name for name in UV_TOOL_BINARIES if tool_root.joinpath("bin", name).exists()]
                    if tool_root.joinpath("bin/machineconfig").exists():
                        links.append("machineconfig")
                    if tool_root.joinpath("bin/mcfg").exists():
                        links.append("mcfg")
                uv_tools_dst = res_root.joinpath("uv_bundle/tools")
                uv_python_dst = res_root.joinpath("uv_bundle/python")
                shutil.copytree(tool_root, uv_tools_dst.joinpath(UV_TOOL_NAME), symlinks=True)
                if python_root.exists():
                    shutil.copytree(python_root, uv_python_dst.joinpath(python_root.name), symlinks=True)
                    _write_uv_manifest(res_root=res_root, python_dir=python_root.name, python_bin=python_bin, link_names=links)
                else:
                    print(f"Warning: uv python root {python_root} missing, skipping uv python export.")
        else:
            print(f"Warning: uv tool {tool_root} not found, skipping uv export.")
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
        sh_script = """#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
BINS_DIR="$SCRIPT_DIR/binaries"
CONFIGS_DIR="$SCRIPT_DIR/configs"
INSTALL_PATH="${INSTALL_PATH:-$HOME/.local/bin}"
CONFIG_ROOT="${CONFIG_ROOT:-$HOME/.config/machineconfig}"
UV_HOME="${UV_HOME:-$HOME/.local/share/uv}"
LOCAL_BIN="${LOCAL_BIN:-$HOME/.local/bin}"
UV_BUNDLE_DIR="$SCRIPT_DIR/uv_bundle"
UV_MANIFEST="$UV_BUNDLE_DIR/uv_manifest.env"
UV_LINKS="$UV_BUNDLE_DIR/uv_links.txt"
UV_FALLBACK_LINKS="devops cloud agents sessions ftpx fire croshell utils msearch explore machineconfig mcfg"

if [ -d "$BINS_DIR" ]; then
    mkdir -p "$INSTALL_PATH"
    for src_bin in "$BINS_DIR"/*; do
        bin_name="$(basename "$src_bin")"
        dst_bin="$INSTALL_PATH/$bin_name"
        if [ -f "$dst_bin" ] && { [ "$bin_name" = "uv" ] || [ "$bin_name" = "uvx" ]; }; then
            printf "%s\n" "Skipping $bin_name: already exists at $dst_bin"
            continue
        fi
        cp -f "$src_bin" "$dst_bin"
        chmod +x "$dst_bin" 2>/dev/null || true
    done
else
    printf "%s\n" "Warning: $BINS_DIR not found, skipping binaries"
fi

if [ -d "$CONFIGS_DIR" ]; then
    mkdir -p "$CONFIG_ROOT"
    cp -R -f "$CONFIGS_DIR"/* "$CONFIG_ROOT"/ 2>/dev/null || true
else
    printf "%s\n" "Warning: $CONFIGS_DIR not found, skipping configs"
fi

if [ -f "$UV_MANIFEST" ]; then
    . "$UV_MANIFEST"
    TOOL_SRC="$UV_BUNDLE_DIR/tools/$TOOL_NAME"
    PY_SRC="$UV_BUNDLE_DIR/python/$PYTHON_DIR"
    TOOL_DST="$UV_HOME/tools/$TOOL_NAME"
    PY_DST="$UV_HOME/python/$PYTHON_DIR"
    if [ -d "$TOOL_SRC" ]; then
        mkdir -p "$UV_HOME/tools"
        rm -rf "$TOOL_DST"
        cp -R -f "$TOOL_SRC" "$UV_HOME/tools/"
        chmod -R +x "$TOOL_DST/bin" 2>/dev/null || true
    else
        printf "%s\n" "Warning: $TOOL_SRC not found, skipping uv tool restore"
    fi
    if [ -d "$PY_SRC" ]; then
        mkdir -p "$UV_HOME/python"
        if [ -d "$PY_DST" ]; then
            printf "%s\n" "Skipping uv python: $PY_DST already exists"
        else
            cp -R -f "$PY_SRC" "$UV_HOME/python/"
            chmod -R +x "$PY_DST/bin" 2>/dev/null || true
        fi
    else
        printf "%s\n" "Warning: $PY_SRC not found, skipping uv python restore"
    fi
    if [ -d "$TOOL_DST" ] && [ -d "$PY_DST" ]; then
        if [ -f "$TOOL_DST/pyvenv.cfg" ]; then
            sed -i.bak "s|^home = .*|home = $PY_DST/bin|" "$TOOL_DST/pyvenv.cfg" && rm -f "$TOOL_DST/pyvenv.cfg.bak"
        fi
        if [ -n "${PYTHON_BIN:-}" ] && [ -f "$PY_DST/bin/$PYTHON_BIN" ]; then
            ln -sf "$PY_DST/bin/$PYTHON_BIN" "$TOOL_DST/bin/python"
            ln -sf python "$TOOL_DST/bin/python3"
            ln -sf python "$TOOL_DST/bin/$PYTHON_BIN"
        fi
        for file in "$TOOL_DST/bin"/*; do
            if [ -f "$file" ] && head -n 1 "$file" 2>/dev/null | grep -q python; then
                sed -i.bak "1s|^#!.*|#!$TOOL_DST/bin/python3|" "$file" && rm -f "$file.bak"
            fi
        done
    fi
    if [ -d "$TOOL_DST" ]; then
        mkdir -p "$LOCAL_BIN"
        while IFS= read -r link_name; do
            [ -z "$link_name" ] && continue
            target="$TOOL_DST/bin/$link_name"
            if [ -f "$target" ]; then
                ln -sf "$target" "$LOCAL_BIN/$link_name"
            else
                printf "%s\n" "Warning: $target not found, skipping link"
            fi
        done < "${UV_LINKS:-/dev/null}"
        if [ ! -f "$UV_LINKS" ]; then
            for link_name in $UV_FALLBACK_LINKS; do
                target="$TOOL_DST/bin/$link_name"
                if [ -f "$target" ]; then
                    ln -sf "$target" "$LOCAL_BIN/$link_name"
                fi
            done
        fi
    fi
fi
"""
        install_sh = res_root.joinpath("install.sh")
        install_sh.write_text(sh_script, encoding="utf-8")
        install_sh.chmod(0o755)
    elif system_name == "Windows":
        ps1_script = """$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BinariesDir = Join-Path $ScriptDir "binaries"
$ConfigsDir = Join-Path $ScriptDir "configs"
$InstallPath = $(if ($env:INSTALL_PATH) { $env:INSTALL_PATH } else { Join-Path $env:LOCALAPPDATA "Microsoft" "WindowsApps" })
$ConfigRoot = $(if ($env:CONFIG_ROOT) { $env:CONFIG_ROOT } else { Join-Path $env:USERPROFILE ".config" "machineconfig" })

if (Test-Path $BinariesDir) {
    New-Item -ItemType Directory -Force -Path $InstallPath | Out-Null
    Get-ChildItem -Path $BinariesDir -File | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination $InstallPath -Force
    }
} else {
    Write-Host "Warning: $BinariesDir not found, skipping binaries"
}

if (Test-Path $ConfigsDir) {
    New-Item -ItemType Directory -Force -Path $ConfigRoot | Out-Null
    Copy-Item -Path (Join-Path $ConfigsDir "*") -Destination $ConfigRoot -Recurse -Force
} else {
    Write-Host "Warning: $ConfigsDir not found, skipping configs"
}
"""
        res_root.joinpath("install.ps1").write_text(ps1_script, encoding="utf-8")
    archive_base = res_root.parent.joinpath(res_root.name)
    shutil.make_archive(archive_base.as_posix(), "zip", root_dir=res_root)
    shutil.rmtree(res_root)


if __name__ == "__main__":
    export()
