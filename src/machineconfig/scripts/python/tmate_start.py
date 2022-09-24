
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
    parser.add_argument("sess_name", help=f"session name", default=random.choices((string.digits + string.ascii_letters).split(''), k=20))

    args = parser.parse_args()
    sess_name = creds['sesssions_names'][args.sess_name]
    api_key = creds['keys']['api_key']
    res = f"tmate -a ~/.ssh/authorized_keys -k {api_key} -n {sess_name} -F"
    os.system(res)


if __name__ == '__main__':
    main()
