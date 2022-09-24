
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
    parser.add_argument("sess_name", help=f"session name", default=random.choices(list(string.digits + string.ascii_letters), k=20))

    args = parser.parse_args()
    sess_name = creds['sessions_names'][args.sess_name]
    user_name = creds['keys']['username']
    res = f"ssh {user_name}/{sess_name}@sgp1.tmate.io"
    os.system(res)


if __name__ == '__main__':
    main()
