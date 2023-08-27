
"""expose a local server behind a NAT or firewall to the internet"""

import platform
import crocodile.toolbox as tb
from typing import Optional


def main(version: Optional[str] = None):
    file = tb.P.home().joinpath("dotfiles/creds/tokens/ngrok")
    if file.exists():
        auth_token = file.read_text()
    else:
        auth_token = input("Enter your ngrok auth token: ")
        file.write_text(auth_token)
    _ = version
    if platform.system() == 'Windows':
        program = f"""
winget install --Id Ngrok.Ngrok
ngrok config add-authtoken {auth_token}
"""
    elif platform.system() == 'Linux':
        program = f"""
# get the latest from here: https://ngrok.com/download
curl https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz --output ~/Downloads/ngrok-v3-stable-linux-amd64.tgz
sudo tar xvzf ~/Downloads/ngrok-v3-stable-linux-amd64.tgz -C /usr/local/bin
ngrok config add-authtoken {auth_token}
"""
    else:
        raise NotImplementedError(f"Platform {platform.system()} not implemented")
    return program


if __name__ == '__main__':
    pass
