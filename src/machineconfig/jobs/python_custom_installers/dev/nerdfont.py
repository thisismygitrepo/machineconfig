"""nerfont installer"""

import platform
from typing import Optional
from machineconfig.utils.schemas.installer.installer_types import InstallerData


config_dict: InstallerData = {
    "appName": "nerdfont",
    "repoURL": "CUSTOM",
    "doc": "lightweight containerization",
    "filenameTemplate": {"amd64": {"windows": "", "linux": "", "macos": ""}, "arm64": {"windows": "", "linux": "", "macos": ""}},
    "stripVersion": False,
    "exeName": "nerdfont",
}


def main(version: Optional[str]):
    print(f"""
{"=" * 150}
🔤 NERD FONTS INSTALLER | Installing programming fonts with icons
💻 Platform: {platform.system()}
🔄 Version: {"latest" if version is None else version}
{"=" * 150}
""")

    _ = version
    if platform.system() == "Windows":
        error_msg = "Nerd Fonts installation not supported on Windows through this installer"
        print(f"""
{"⚠️" * 20}
❌ ERROR | {error_msg}
💡 TIP: Please download and install manually from https://www.nerdfonts.com
{"⚠️" * 20}
""")
        raise NotImplementedError(error_msg)
    elif platform.system() in ["Linux", "Darwin"]:
        print("🐧 Installing Nerd Fonts on Linux using installation script...")
        import machineconfig.jobs.python_custom_installers as module
        from pathlib import Path

        program = Path(module.__file__).parent.joinpath("scripts/linux/nerdfont.sh").read_text(encoding="utf-8")
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
ℹ️  INFO | Nerd Fonts features:
🎨 Programming fonts patched with icons
🔣 Includes icons from popular sets (FontAwesome, Devicons, etc.)
🖥️  Perfect for terminals and coding environments
🧰 Works with many terminal applications and editors
{"=" * 150}
""")

    # _res = Terminal(stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).run_script(script=program, shell="default").print(desc="Running custom installer", capture=True)
    # run script here as it requires user input
    return program


if __name__ == "__main__":
    pass
