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
    "exe_name": "ngrok",
}


def main(version: Optional[str]):
    print(f"""
{"=" * 150}
🔄 NGROK INSTALLER | Setting up secure tunnels to localhost
💻 Platform: {platform.system()}
{"=" * 150}
""")

    _ = version
    if platform.system() == "Windows":
        print("🪟 Installing ngrok using winget on Windows...")
        program = "winget install ngrok.ngrok --source winget"
    elif platform.system() in ["Linux", "Darwin"]:
        print("🐧 Installing ngrok using apt/nala on Linux...")
        # as per https://ngrok.com/docs/getting-started/?os=linux
        program = """

curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | \
sudo tee /etc/apt/sources.list.d/ngrok.list && \
sudo nala update && sudo nala install ngrok
"""
    else:
        error_msg = f"Unsupported platform: {platform.system()}"
        print(f"""
{"⚠️" * 20}
❌ ERROR | {error_msg}
{"⚠️" * 20}
""")
        raise NotImplementedError(error_msg)

    print(f"""
{"=" * 150}
⚠️  SECURITY WARNING | ngrok has been flagged by some antivirus engines
🛡️  Use at your own risk - flagged by 35% of antivirus engines
{"=" * 150}
""")
    return program


if __name__ == "__main__":
    pass
