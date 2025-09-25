"""alacritty"""

import platform
from typing import Optional
from machineconfig.utils.schemas.installer.installer_types import InstallerData


config_dict: InstallerData = {"appName": "Alacritty", "repoURL": "CUSTOM", "doc": "Terminal Console", "filenameTemplate": {"amd64": {"windows": "", "linux": "", "macos": ""}}, "stripVersion": False, "exeName": "alacritty"}


def main(version: Optional[str]):
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

    # _res = Terminal(stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).run_script(script=program, shell="default").print(desc="Running custom installer", capture=True)
    # run script here as it requires user input
    return program


if __name__ == "__main__":
    pass
