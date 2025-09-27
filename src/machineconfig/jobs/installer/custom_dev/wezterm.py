"""wezterm installer"""

import platform
import subprocess
from typing import Optional

from machineconfig.utils.schemas.installer.installer_types import InstallerData


# config_dict: InstallerData = {"appName": "Wezterm", "repoURL": "CMD", "doc": "Modern, GPU-accelerated terminal emulator"}


def main(installer_data: InstallerData, version: Optional[str]):
    _ = installer_data
    print(f"""
{"═" * 150}
🖥️  WEZTERM INSTALLER | Modern, GPU-accelerated terminal emulator
💻 Platform: {platform.system()}
🔄 Version: {"latest" if version is None else version}
{"═" * 150}
""")

    _ = version
    if platform.system() == "Windows":
        error_msg = "WezTerm installation not supported on Windows through this installer"
        print(f"""
{"⚠️" * 20}
❌ ERROR | {error_msg}
💡 TIP: Please download and install manually from the WezTerm website
{"⚠️" * 20}
""")
        raise NotImplementedError(error_msg)
    elif platform.system() in ["Linux", "Darwin"]:
        system_name = "LINUX" if platform.system() == "Linux" else "MACOS"
        print(f"""
🐧 {system_name} SETUP | Installing WezTerm terminal emulator...
""")
        import machineconfig.jobs.installer as module
        from pathlib import Path

        if platform.system() == "Linux":
            program = Path(module.__file__).parent.joinpath("linux_scripts/wezterm.sh").read_text(encoding="utf-8")
        else:  # Darwin/macOS
            program = "brew install --cask wezterm"
    else:
        error_msg = f"Unsupported platform: {platform.system()}"
        print(f"""
{"⚠️" * 20}
❌ ERROR | {error_msg}
{"⚠️" * 20}
""")
        raise NotImplementedError(error_msg)

    print(f"""
{"═" * 150}
ℹ️  INFO | WezTerm Features:
⚡ GPU-accelerated rendering
🎨 Full color emoji support
🧩 Multiplexing with panes and tabs
⚙️  Lua configuration
📦 Cross-platform support
🔌 Plugin system
{"═" * 150}
""")

    print("🔄 EXECUTING | Running WezTerm installation...")
    try:
        subprocess.run(program, shell=True, text=True, check=True)
        print("✅ WezTerm installation completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed with exit code {e.returncode}")
        raise


if __name__ == "__main__":
    pass
