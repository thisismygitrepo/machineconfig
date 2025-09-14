"""lvim"""

from machineconfig.utils.terminal import Terminal
import subprocess
import platform
from typing import Optional


_ = Terminal, subprocess
# as per https://www.lunarvim.org/docs/installation


config_dict = {"repo_url": "CUSTOM", "doc": "Terminal text editor based on neovim.", "filename_template_windows_amd_64": "", "filename_template_linux_amd_64": "", "strip_v": False, "exe_name": "lvim"}


def main(version: Optional[str]):
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

    # _res = Terminal(stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).run_script(script=program, shell="default").print(desc="Running custom installer", capture=True)
    # run script here as it requires user input
    return program


if __name__ == "__main__":
    pass
