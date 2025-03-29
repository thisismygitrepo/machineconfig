

from typing import Optional
import platform

config_dict = {
    "repo_url": "CUSTOM",
    "doc": "Aider Chat",
    "filename_template_windows_amd_64": "aider-chat-{}.exe",
    "filename_template_linux_amd_64": "aider-chat-{}.deb",
    "strip_v": True,
    "exe_name": "aider-chat"
}


def main(version: Optional[str] = None):
    install_script = "uv tool install --force --python python3.12 aider-chat@latest"
    return install_script


if __name__ == '__main__':
    pass

