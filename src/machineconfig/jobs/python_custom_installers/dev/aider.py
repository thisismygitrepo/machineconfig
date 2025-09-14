from typing import Optional
import platform

config_dict = {"repo_url": "CUSTOM", "doc": "Aider Chat", "filename_template_windows_amd_64": "aider-chat-{}.exe", "filename_template_linux_amd_64": "aider-chat-{}.deb", "strip_v": True, "exe_name": "aider-chat"}


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
