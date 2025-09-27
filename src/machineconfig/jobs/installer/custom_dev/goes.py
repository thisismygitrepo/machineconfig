"""natural language to API
https://github.com/    print("🔄 EXECUTING | Running Go installation...")
    try:
        subprocess.run(install_script, shell=True, text=True, check=True)
        print("✅ Go installation completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed with exit code {e.returncode}")
        raisel/gorilla
"""

import subprocess
from machineconfig.utils.schemas.installer.installer_types import InstallerData

# config_dict: InstallerData = {
#     "appName": "Gorilla",
#     "repoURL": "https://github.com/ShishirPatil/gorilla",
#     "doc": "natural language to API",
# }

ve_name = "goex"


def main(installer_data: InstallerData):
    _ = installer_data
    print(f"""
{"=" * 150}
🦍 GORILLA INSTALLER | Natural language to API converter
🌐 Source: https://github.com/ShishirPatil/gorilla
📦 Virtual Environment: {ve_name}
{"=" * 150}
""")

    print("🔄 Preparing installation script...")
    install_script = """

cd ~/code/foreign
git clone https://github.com/ShishirPatil/gorilla --depth 1
cd gorilla/goex
uv sync
    """

    print(f"""
{"=" * 150}
📋 INSTALLATION STEPS:
1️⃣  Creating Python 3.13 virtual environment: {ve_name}
2️⃣  Cloning Gorilla repository to ~/code/foreign
3️⃣  Installing Gorilla in development mode
{"=" * 150}

✅ Installation script prepared successfully!
""")

    print("🔄 EXECUTING | Running Gorilla installation...")
    try:
        subprocess.run(install_script, shell=True, text=True, check=True)
        print("✅ Gorilla installation completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed with exit code {e.returncode}")
        raise


if __name__ == "__main__":
    pass
