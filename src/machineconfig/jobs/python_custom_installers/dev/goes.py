"""
natural language to API
https://github.com/ShishirPatil/gorilla
"""

# import subprocess

config_dict = {"repo_url": "CUSTOM", "doc": "natural language to API", "filename_template_windows_amd_64": "", "filename_template_linux_amd_64": "", "strip_v": False, "exe_name": "goex"}

ve_name = "goex"


def main():
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

    return install_script


if __name__ == "__main__":
    pass
