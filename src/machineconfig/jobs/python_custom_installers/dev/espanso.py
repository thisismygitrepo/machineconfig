

"""
A text expander is a program that detects when you type a specific keyword and replaces it with something else

https://github.com/espanso/espanso
"""

from typing import Optional

config_dict = {
        "repo_url": "CUSTOM",
        "doc": "A text expander.",
        "filename_template_windows_amd_64": "Espanso-Win-Installer-x86_64.exe",
        "filename_template_linux_amd_64": "",
        "strip_v": False,
        "exe_name": "espanso"
    }


def main(version: Optional[str]):
    _ = version
    import platform
    config_dict["repo_url"] = "https://github.com/espanso/espanso"
    if platform.system() == "Windows":
        pass
    elif platform.system() == "Linux":
        import os
        env = os.environ["XDG_SESSION_TYPE"]
        if env == "wayland":
            print("Wayland detected".center(80, "="))
            config_dict["filename_template_linux_amd_64"] = "espanso-debian-wayland-amd64.deb"
        else:
            print("X11 detected".center(80, "="))
            config_dict["filename_template_linux_amd_64"] = "espanso-debian-x11-amd64.deb"
    else:
        raise NotImplementedError(f"Unsupported platform: {platform.system()}")
    
    from machineconfig.utils.installer import Installer
    installer = Installer.from_dict(config_dict, name="espanso")
    installer.install(version=None)
    config = """
espanso service register
espanso start
espanso install actually-all-emojis
    """
    return config
