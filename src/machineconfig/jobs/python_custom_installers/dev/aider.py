from typing import Optional
from machineconfig.utils.schemas.installer.installer_types import InstallerData
import platform

config_dict: InstallerData = {
    "appName": "aider-chat",
    "repoURL": "https://github.com/paul-gauthier/aider",
    "doc": "Aider Chat",
    "filenameTemplate": {"amd64": {"windows": "aider-chat-{}.exe", "linux": "aider-chat-{}.deb", "macos": ""}, "arm64": {"windows": "", "linux": "", "macos": ""}},
    "stripVersion": True,
    "exeName": "aider-chat",
}


def main(version: Optional[str] = None):
    print(f"""
{"=" * 150}
🤖 AIDER INSTALLER | Installing AI code assistant
💻 Platform: {platform.system()}
🔄 Version: {"latest" if version is None else version}
{"=" * 150}
""")

    install_script = "uv tool install --force --python python3.12 aider-chat@latest"

    print(f"""
{"=" * 150}
✅ SUCCESS | Installation command prepared:
📄 Command: {install_script}
{"=" * 150}
""")

    return install_script


if __name__ == "__main__":
    pass
