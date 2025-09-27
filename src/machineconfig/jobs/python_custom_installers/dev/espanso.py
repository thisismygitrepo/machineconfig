"""
A text expander is a program that detects when you type a specific keyword and replaces it with something else

https://github.com/espanso/espanso
"""

from typing import Optional
from machineconfig.utils.schemas.installer.installer_types import InstallerData

config_dict: InstallerData = {
    "appName": "espanso",
    "repoURL": "CUSTOM",
    "doc": "A text expander.",
}


def main(version: Optional[str]):
    print(f"""
{"=" * 150}
⚡ ESPANSO INSTALLER | Setting up text expansion tool
🔄 Version: {"latest" if version is None else version}
🔗 Source: https://github.com/espanso/espanso
{"=" * 150}
""")

    _ = version
    import platform

    config_dict["repoURL"] = "https://github.com/espanso/espanso"
    if platform.system() == "Windows":
        print("🪟 Installing Espanso on Windows...")
    elif platform.system() in ["Linux", "Darwin"]:
        if platform.system() == "Linux":
            import os

            env = os.environ["XDG_SESSION_TYPE"]
            if env == "wayland":
                print(f"""
{"=" * 150}
🖥️  DISPLAY SERVER | Wayland detected
📦 Using Wayland-specific package
{"=" * 150}
""")
                config_dict["filenameTemplate"]["amd64"]["linux"] = "espanso-debian-wayland-amd64.deb"
            else:
                print(f"""
{"=" * 150}
🖥️  DISPLAY SERVER | X11 detected
📦 Using X11-specific package
{"=" * 150}
""")
                config_dict["filenameTemplate"]["amd64"]["linux"] = "espanso-debian-x11-amd64.deb"
        else:  # Darwin/macOS
            print("🍎 Installing Espanso on macOS...")
            config_dict["filenameTemplate"]["amd64"]["macos"] = "Espanso.dmg"
    else:
        error_msg = f"Unsupported platform: {platform.system()}"
        print(f"""
{"⚠️" * 20}
❌ ERROR | {error_msg}
{"⚠️" * 20}
""")
        raise NotImplementedError(error_msg)

    print("🚀 Installing Espanso using installer...")
    from machineconfig.utils.installer_utils.installer_class import Installer

    installer = Installer(config_dict)
    installer.install(version=None)

    config = """
espanso service register
espanso start
espanso install actually-all-emojis
    """

    print(f"""
{"=" * 150}
✅ SUCCESS | Espanso installation completed
📋 Post-installation steps:
1️⃣  Register Espanso as a service
2️⃣  Start the Espanso service
3️⃣  Install the emoji package
{"=" * 150}
""")

    return config
