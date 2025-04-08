"""Tmate
"""
import argparse
import configparser
from pathlib import Path
import random
import string
import os


def main():
    print(f"""
╔{'═' * 60}╗
║ 📡 Tmate Session Launcher
╚{'═' * 60}╝
""")
    
    print("🔐 Loading credentials...")
    creds = configparser.ConfigParser()
    creds.read(Path.home().joinpath('dotfiles/creds/tmate/creds.ini'))
    print("✅ Credentials loaded")

    parser = argparse.ArgumentParser(description='Tmate launcher')
    random_sess = random.choices(list(string.digits + string.ascii_letters), k=20)
    _ = random_sess
    parser.add_argument("sess_name", help="session name (new only with random string will be chosen if not passed)", default=None)

    args = parser.parse_args()

    print(f"🔍 Looking up session configuration: {args.sess_name}")
    sess_name = creds['sessions_names'][args.sess_name]
    api_key = creds['keys']['api_key']
    
    print(f"""
╭{'─' * 60}╮
│ 🚀 Starting tmate session: {sess_name}
╰{'─' * 60}╯
""")
    
    res = f"tmate -a ~/.ssh/authorized_keys -k {api_key} -n {sess_name} -F"
    print("⚙️  Running: tmate with configured API key and session name")
    os.system(res)
    
    print("✅ Tmate session ended")


if __name__ == '__main__':
    main()
