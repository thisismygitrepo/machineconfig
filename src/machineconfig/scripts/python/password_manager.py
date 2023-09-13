
"""PM
"""

import subprocess
import clipboard
import argparse
import time


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


if __name__ == '__main__':
    main()
