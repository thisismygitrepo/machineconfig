"""
Installer
"""

# from machineconfig.utils.installer import get_latest_release
from typing import Optional

# https://docs.docker.com/desktop/install/ubuntu/
# https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository
# https://stackoverflow.com/questions/41133455/docker-repository-does-not-have-a-release-file-on-running-apt-get-update-on-ubun


# url = r"https://github.com/koute/bytehound"
# fname = r"bytehound-x86_64-unknown-linux-gnu.tgz"


config_dict = {
    "repo_url": "CUSTOM",
    "doc": """Docker Desktop for Ubuntu as per https://docs.docker.com/desktop/install/ubuntu/""",
    "filename_template_windows_amd_64": "gh_{}_windows_amd64.zip",
    "filename_template_linux_amd_64": "gh_{}_linux_amd64.tar.gz",
    "strip_v": True,
    "exe_name": "docker",
}


def main(version: Optional[str]):
    print(f"""
{"=" * 150}
🐳 DOCKER DESKTOP | Installing Docker Desktop for Ubuntu
🔄 Version: {"latest" if version is None else version}
📚 Source: https://docs.docker.com/desktop/install/ubuntu/
{"=" * 150}
""")

    _ = version

    print("""
📋 Installation steps:
1️⃣  Adding Docker's official GPG key
2️⃣  Adding repository to Apt sources
3️⃣  Updating package lists
4️⃣  Installing Docker components
""")

    code = """
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

"""
    print(f"""
{"=" * 150}
ℹ️  INFO | After installation:
🔹 Run 'sudo docker run hello-world' to verify installation
🔹 Add your user to the docker group with 'sudo usermod -aG docker $USER'
🔹 Log out and back in to apply group changes
{"=" * 150}
""")

    return code


if __name__ == "__main__":
    pass
