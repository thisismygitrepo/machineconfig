"""lvim"""

from machineconfig.utils.terminal import Terminal
import subprocess
import platform
from typing import Optional
from machineconfig.utils.schemas.installer.installer_types import InstallerData


_ = Terminal, subprocess
# as per https://www.lunarvim.org/docs/installation


def main(installer_data: InstallerData, version: Optional[str]):
    _ = installer_data
    print(f"""
{"=" * 150}
🌙 LUNARVIM INSTALLER | Setting up Neovim-based IDE
🔄 Version: {"latest" if version is None else version}
📚 Branch: release-1.4/neovim-0.9
{"=" * 150}
""")

    _ = version
    if platform.system() == "Windows":
        print("🪟 Installing LunarVim on Windows...")
        program = """

pwsh -c "`$LV_BRANCH='release-1.4/neovim-0.9'; iwr https://raw.githubusercontent.com/LunarVim/LunarVim/release-1.4/neovim-0.9/utils/installer/install.ps1 -UseBasicParsing | iex"

"""
    elif platform.system() in ["Linux", "Darwin"]:
        system_name = "Linux" if platform.system() == "Linux" else "macOS"
        print(f"🐧 Installing LunarVim on {system_name}...")
        program = """

LV_BRANCH='release-1.4/neovim-0.9' bash <(curl -s https://raw.githubusercontent.com/LunarVim/LunarVim/release-1.4/neovim-0.9/utils/installer/install.sh)

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
ℹ️  INFO | LunarVim features:
📝 IDE-like experience for Neovim
🔌 Built-in plugin management
🛠️  LSP configuration out of the box
🔍 Powerful fuzzy finding
⚙️  Simple and unified configuration
{"=" * 150}

⚠️  NOTE: The installer will prompt for user input during installation.
""")

    print("🔄 EXECUTING | Running LunarVim installation...")
    try:
        # Run with shell=True and allow interaction for user input
        subprocess.run(program, shell=True, check=True)
        print("✅ LunarVim installation completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed with exit code {e.returncode}")
        raise


if __name__ == "__main__":
    pass
