"""wezterm installer
"""

import platform
from typing import Optional


config_dict = {
        "repo_url": "CUSTOM",
        "doc": "cli for wezterm",
        "filename_template_windows_amd_64": "",
        "filename_template_linux_amd_64": "",
        "strip_v": False,
        "exe_name": "wezterm"
}


def main(version: Optional[str]):
    print(f"""
{'═' * 70}
🖥️  WEZTERM INSTALLER | Modern, GPU-accelerated terminal emulator
💻 Platform: {platform.system()}
🔄 Version: {'latest' if version is None else version}
{'═' * 70}
""")
    
    _ = version
    if platform.system() == "Windows":
        error_msg = "WezTerm installation not supported on Windows through this installer"
        print(f"""
{'⚠️' * 20}
❌ ERROR | {error_msg}
💡 TIP: Please download and install manually from the WezTerm website
{'⚠️' * 20}
""")
        raise NotImplementedError(error_msg)
    elif platform.system() == "Linux":
        print("""
🐧 LINUX SETUP | Installing WezTerm terminal emulator using installation script...
""")
        import machineconfig.jobs.python_custom_installers as module
        from pathlib import Path
        program = Path(module.__file__).parent.joinpath("scripts/linux/wezterm.sh").read_text(encoding="utf-8")
    else:
        error_msg = f"Unsupported platform: {platform.system()}"
        print(f"""
{'⚠️' * 20}
❌ ERROR | {error_msg}
{'⚠️' * 20}
""")
        raise NotImplementedError(error_msg)
    
    print(f"""
{'═' * 70}
ℹ️  INFO | WezTerm Features:
⚡ GPU-accelerated rendering
🎨 Full color emoji support
🧩 Multiplexing with panes and tabs
⚙️  Lua configuration
📦 Cross-platform support
🔌 Plugin system
{'═' * 70}
""")
    
    # _res = Terminal(stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).run_script(script=program, shell="default").print(desc="Running custom installer", capture=True)
    # run script here as it requires user input
    return program


if __name__ == "__main__":
    pass
