from typing import Optional
from machineconfig.utils.schemas.installer.installer_types import InstallerData
import platform

# config_dict: InstallerData = {
#     "appName": "aider-chat",
#     "repoURL": "https://github.com/paul-gauthier/aider",
#     "doc": "Aider Chat",
# }


def main(installer_data: InstallerData, version: Optional[str] = None):
    _ = installer_data
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
