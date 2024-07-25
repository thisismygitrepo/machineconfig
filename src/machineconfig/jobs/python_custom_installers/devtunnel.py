
"""devtunnel
as per https://learn.microsoft.com/en-us/azure/developer/dev-tunnels/get-started?tabs=windows
"""

import platform
from typing import Optional


config_dict = {
        "repo_url": "CUSTOM",
        "doc": "devtunnel secure introspectable tunnels to localhost",
        "filename_template_windows_amd_64": "",
        "filename_template_linux_amd_64": "",
        "strip_v": False,
        "exe_name": "devtunnel"
    }


def main(version: Optional[str]):
    _ = version
    if platform.system() == "Windows":
        program = "winget install Microsoft.devtunnel"
    elif platform.system() == "Linux":
        program = """
curl -sL https://aka.ms/DevTunnelCliInstall | bash
"""
    else:
        raise NotImplementedError("unsupported platform")
    return program


if __name__ == "__main__":
    pass
