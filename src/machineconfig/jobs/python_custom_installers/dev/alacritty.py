"""alacritty
"""

import platform
from typing import Optional


config_dict = {
        "repo_url": "CUSTOM",
        "doc": "Terminal Console",
        "filename_template_windows_amd_64": "",
        "filename_template_linux_amd_64": "",
        "strip_v": False,
        "exe_name": "alacritty"
    }


def main(version: Optional[str]):
    print(f"""
{'=' * 70}
🖥️  ALACRITTY INSTALLER | Installing GPU-accelerated terminal emulator
💻 Platform: {platform.system()}
🔄 Version: {'latest' if version is None else version}
{'=' * 70}
""")
    
    _ = version
    if platform.system() == "Windows":
        print("🪟 Installing Alacritty on Windows using Cargo...")
        program = """

cargo install alacritty
mkdir -p ~/.config/alacritty/themes
git clone https://github.com/alacritty/alacritty-theme ~/.config/alacritty/themes

"""
    elif platform.system() == "Linux":
        print("🐧 Installing Alacritty on Linux using Cargo...")
        program = """


cargo install alacritty
mkdir -p ~/.config/alacritty/themes
git clone https://github.com/alacritty/alacritty-theme ~/.config/alacritty/themes

"""
    else:
        error_msg = f"Unsupported platform: {platform.system()}"
        print(f"""
{'⚠️' * 20}
❌ ERROR | {error_msg}
{'⚠️' * 20}
""")
        raise NotImplementedError(error_msg)
        
    print(f"""
{'=' * 70}
ℹ️  INFO | Installation will proceed with the following steps:
1️⃣  Install Alacritty using Cargo
2️⃣  Create config directories
3️⃣  Clone theme repository
{'=' * 70}
""")
    
    # _res = Terminal(stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).run_script(script=program, shell="default").print(desc="Running custom installer", capture=True)
    # run script here as it requires user input
    return program


if __name__ == "__main__":
    pass

