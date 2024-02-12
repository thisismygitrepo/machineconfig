
# from machineconfig.utils.installer import get_latest_release
# 
# from crocodile.meta import Terminal
from typing import Optional

# https://docs.docker.com/desktop/install/ubuntu/
# https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository
# https://stackoverflow.com/questions/41133455/docker-repository-does-not-have-a-release-file-on-running-apt-get-update-on-ubun


# url = r"https://github.com/koute/bytehound"
# fname = r"bytehound-x86_64-unknown-linux-gnu.tgz"
__doc__ = """Docker Desltop for Ubuntu as per https://docs.docker.com/desktop/install/ubuntu/"""


def main(version: Optional[str] = None):
    _ = version
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
    return code


if __name__ == '__main__':
    pass
