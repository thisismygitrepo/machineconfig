
import argparse
import configparser
from pathlib import Path
import random
import string
import os


def main():
    creds = configparser.ConfigParser()
    creds.read(Path.home().joinpath('dotfiles/creds/tmate/creds.ini'))

    parser = argparse.ArgumentParser(description='Tmate launcher')
    parser.add_argument("sess_name", help=f"session name (new only with random string will be chosen if not passed)", default=random.choices(list(string.digits + string.ascii_letters), k=20))

    args = parser.parse_args()
    sess_name = creds['sessions_names'][args.sess_name]
    api_key = creds['keys']['api_key']
    res = f"tmate -a ~/.ssh/authorized_keys -k {api_key} -n {sess_name} -F"
    os.system(res)


if __name__ == '__main__':
    main()
