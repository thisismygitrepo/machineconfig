

from pathlib import Path
from typing import Optional
# import typer


"""
reference:
# https://github.com/tsl0922/ttyd/wiki/Serving-web-fonts
# -t "fontFamily=CaskaydiaCove" bash
# --terminal-type xterm-kitty

"""


def share_terminal(port: int, password: Optional[str]) -> None:
    if password is None:
        pwd_path = Path.home().joinpath("dotfiles/creds/passwords/quick_password")
        if pwd_path.exists():
            password = pwd_path.read_text(encoding="utf-8").strip()
        else:
            raise ValueError("Password not provided and default password file does not exist.")

    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8',80))
    local_ip_v4 = s.getsockname()[0]
    s.close()

    print(f"\n🌐 Access your terminal at: http://{local_ip_v4}:{port}\n")

    code = f"""
#!/bin/bash
uv run --python 3.13 --with machineconfig install -ttyd

ttyd --writable -t enableSixel=true --port {port} --credential "$USER:{password}" -t 'theme={"background": "black"}' bash

"""
    import subprocess
    subprocess.run(code, shell=True, check=True)
