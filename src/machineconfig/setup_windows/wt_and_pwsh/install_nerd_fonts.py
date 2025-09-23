"""
setup file for each shell can be found in $profile. The settings.json is the config file for Terminal.
https://glitchbone.github.io/vscode-base16-term/#/3024

"""

from machineconfig.utils.path_reduced import PathExtended as PathExtended
from machineconfig.utils.source_of_truth import LIBRARY_ROOT
from machineconfig.utils.installer_utils.installer_class import Installer
import subprocess
from typing import Iterable


nerd_fonts = {
    "repo_url": "https://github.com/ryanoasis/nerd-fonts",
    "doc": "Nerd Fonts is a project that patches developer targeted fonts with a high number of glyphs (icons)",
    "filename_template_windows_amd_64": "CascadiaCode.zip",
    "filename_template_linux_amd_64": "CascadiaCode.zip",
    "strip_v": False,
    "exe_name": "nerd_fonts",
}


# Patterns to match any installed variant (NF, Nerd Font, Mono, Propo, style weights) of Cascadia/Caskaydia
# We'll compile them at runtime for flexibility. Keep them simple to avoid false positives.
REQUIRED_FONT_PATTERNS: tuple[str, ...] = (r"caskaydiacove.*(nf|nerd ?font)", r"cascadiacode.*(nf|nerd ?font)")


def _list_installed_fonts() -> list[str]:
    """Return list of installed font file base names (without extension) on Windows.

    Uses PowerShell to enumerate c:\\windows\\fonts because Python on *nix host can't rely on that path.
    If PowerShell call fails (e.g. running on non-Windows), returns empty list so install proceeds.
    """
    try:
        # Query only base names to make substring matching simpler; remove underscores like the PS script does.
        cmd = ["powershell.exe", "-NoLogo", "-NonInteractive", "-Command", "Get-ChildItem -Path C:/Windows/Fonts -File | Select-Object -ExpandProperty BaseName"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)  # noqa: S603 S607 (trusted command)
        fonts = [x.strip().replace("_", "") for x in res.stdout.splitlines() if x.strip() != ""]
        return fonts
    except Exception as exc:  # noqa: BLE001
        print(f"⚠️ Could not enumerate installed fonts (continuing with install). Reason: {exc}")
        return []


def _missing_required_fonts(installed_fonts: Iterable[str]) -> list[str]:
    import re

    installed_norm = [f.lower().replace(" ", "") for f in installed_fonts]
    missing: list[str] = []
    for pattern in REQUIRED_FONT_PATTERNS:
        regex = re.compile(pattern)
        if not any(regex.search(f) for f in installed_norm):
            missing.append(pattern)
    return missing


def install_nerd_fonts() -> None:
    print(f"\n{'=' * 80}\n📦 INSTALLING NERD FONTS 📦\n{'=' * 80}")
    installed = _list_installed_fonts()
    missing = _missing_required_fonts(installed)
    if len(missing) == 0:
        print("✅ Required Nerd Fonts already installed. Skipping download & install.")
        return
    print(f"🔍 Missing fonts detected: {', '.join(missing)}. Proceeding with installation...")
    print("🔍 Downloading Nerd Fonts package...")
    folder, _version_to_be_installed = Installer.from_dict(d=nerd_fonts, name="nerd_fonts").download(version=None)

    print("🧹 Cleaning up unnecessary files...")
    [p.delete(sure=True) for p in folder.search("*Windows*")]
    [p.delete(sure=True) for p in folder.search("*readme*")]
    [p.delete(sure=True) for p in folder.search("*LICENSE*")]

    print("⚙️  Installing fonts via PowerShell...")
    file = PathExtended.tmpfile(suffix=".ps1")
    file.parent.mkdir(parents=True, exist_ok=True)
    raw_content = LIBRARY_ROOT.joinpath("setup_windows/wt_and_pwsh/install_fonts.ps1").read_text(encoding="utf-8").replace(r".\fonts-to-be-installed", str(folder))
    # PowerShell 5.1 can choke on certain unicode chars in some locales; keep ASCII only.
    content = "".join(ch for ch in raw_content if ord(ch) < 128)
    file.write_text(content, encoding="utf-8")
    try:
        subprocess.run(rf"powershell.exe -executionpolicy Bypass -nologo -noninteractive -File {str(file)}", check=True)
    except subprocess.CalledProcessError as cpe:
        print(f"💥 Font installation script failed (continuing without abort): {cpe}")
        return

    print("🗑️  Cleaning up temporary files...")
    folder.delete(sure=True)
    print(f"\n✅ Nerd Fonts installation complete! ✅\n{'=' * 80}")


def main():
    print(f"\n{'=' * 80}\n🎨 POWERSHELL THEME SETUP 🎨\n{'=' * 80}")
    install_nerd_fonts()
    print(f"\n✅ All PowerShell theme components installed successfully! ✅\n{'=' * 80}")


if __name__ == "__main__":
    pass
