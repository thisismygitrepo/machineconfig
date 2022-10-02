
import argparse
import configparser
from pathlib import Path
import random
import string
import os


def get_conn_string(sess_name):
    creds = configparser.ConfigParser()
    creds.read(Path.home().joinpath('dotfiles/creds/tmate/creds.ini'))
    sess_name = creds['sessions_names'][sess_name]
    user_name = creds['keys']['username']
    return f"{user_name}/{sess_name}@sgp1.tmate.io"


def main():
    parser = argparse.ArgumentParser(description='Tmate launcher')
    parser.add_argument("sess_name", help=f"session name", default=random.choices(list(string.digits + string.ascii_letters), k=20))
    args = parser.parse_args()
    os.system(f"ssh {get_conn_string(args.sess_name)}")


if __name__ == '__main__':
    main()
