"""alacritty"""

import platform
import subprocess
from typing import Optional
from machineconfig.utils.schemas.installer.installer_types import InstallerData


# config_dict: InstallerData = {"appName": "Alacritty", "repoURL": "CMD", "doc": "Terminal Console"}


def main(installer_data: InstallerData, version: Optional[str]):
    _ = installer_data
    print(f"""
{"=" * 150}
🖥️  ALACRITTY INSTALLER | Installing GPU-accelerated terminal emulator
💻 Platform: {platform.system()}
🔄 Version: {"latest" if version is None else version}
{"=" * 150}
""")

    _ = version
    if platform.system() == "Windows":
        print("🪟 Installing Alacritty on Windows using Cargo...")
        program = """

cargo install alacritty
mkdir -p ~/.config/alacritty/themes
git clone https://github.com/alacritty/alacritty-theme ~/.config/alacritty/themes

"""
    elif platform.system() in ["Linux", "Darwin"]:
        system_name = "Linux" if platform.system() == "Linux" else "macOS"
        print(f"🐧 Installing Alacritty on {system_name} using Cargo...")
        program = """


cargo install alacritty
mkdir -p ~/.config/alacritty/themes
git clone https://github.com/alacritty/alacritty-theme ~/.config/alacritty/themes

"""
    else:
        error_msg = f"Unsupported platform: {platform.system()}"
        print(f"""
{"⚠️" * 20}
❌ ERROR | {error_msg}
{"⚠️" * 20}
""")
        raise NotImplementedError(error_msg)

    print(f"""
{"=" * 150}
ℹ️  INFO | Installation will proceed with the following steps:
1️⃣  Install Alacritty using Cargo
2️⃣  Create config directories
3️⃣  Clone theme repository
{"=" * 150}
""")

    print("🔄 EXECUTING | Running Alacritty installation...")
    try:
        subprocess.run(program, shell=True, text=True, check=True)
        print("✅ Alacritty installation completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed with exit code {e.returncode}")
        raise


if __name__ == "__main__":
    pass
