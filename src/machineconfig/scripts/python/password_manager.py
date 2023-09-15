
"""PM
"""

import subprocess
import clipboard
import argparse
import time
from typing import Optional


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="name of the password to retrieve")

    args = parser.parse_args()
    pwd = subprocess.run(["bw", "get", "password", args.name], capture_output=True, check=True, shell=True).stdout.decode().strip()

    try:
        totp: str = subprocess.run(["bw", "get", "totp", args.name], capture_output=True, check=True, shell=True).stdout.decode().strip()
        clipboard.copy(totp)
        print(f"✅ TOTP {args.name} copied to clipboard 🖇️.")
        time.sleep(0.8)  # can't write quickly again, it down't work.
    except subprocess.CalledProcessError:
        print(f"❌ TOTP {args.name} not found.")

    clipboard.copy(pwd)
    print(f"✅ Password {args.name} copied to clipboard 🖇️.")


def main_installer(version: Optional[str] = None):
    """Bitwarden CLI installer
    "~/AppData/Roaming/Bitwarden CLI/data.json";
    npm install -g @bitwarden/cli
    """
    import crocodile.toolbox as tb
    import platform
    _ = version
    if platform.system() == "Windows":
        res = tb.P(r"https://vault.bitwarden.com/download/?app=cli&platform=windows").download().unzip(inplace=True)
        res.search("bw.exe").move(tb.P.get_env().WindowsApps)
        res.delete(sure=True)
    elif platform.system() == "Linux":
        raise NotImplementedError("Linux not implemented yet")
    return None


if __name__ == '__main__':
    main()
