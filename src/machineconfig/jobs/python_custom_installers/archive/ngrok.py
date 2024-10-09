
"""ngrok

flagged as virus by 35% of antivirus engines
"""

import platform
from typing import Optional


config_dict = {
        "repo_url": "CUSTOM",
        "doc": "ngrok secure introspectable tunnels to localhost",
        "filename_template_windows_amd_64": "ngrok-stable-windows-amd64.zip",
        "filename_template_linux_amd_64": "ngrok-stable-linux-amd64.zip",
        "strip_v": False,
        "exe_name": "ngrok"
    }


def main(version: Optional[str]):
    _ = version
    if platform.system() == "Windows":
        program = "winget install ngrok.ngrok --source winget"
    elif platform.system() == "Linux":
        # as per https://ngrok.com/docs/getting-started/?os=linux
        program = """

curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | \
sudo tee /etc/apt/sources.list.d/ngrok.list && \
sudo apt update && sudo apt install ngrok
"""
    else:
        raise NotImplementedError("unsupported platform")
    return program


if __name__ == "__main__":
    pass
