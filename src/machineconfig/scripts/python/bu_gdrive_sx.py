

from crocodile.comms.gdrive import GDriveAPI
from crocodile.file_management import *
import argparse


def process_file(args):
    file = P(args.file).expanduser().absolute()
    if args.zip_first: file = P(file).zip()
    if args.encrypt_first:
        tmp = file
        file = P(tmp).encrypt(key=args.key, pwd=args.pwd)
        if args.zip_first: tmp.delete(sure=True)
    # path = path.zip_n_encrypt(key=None, inplace=False, verbose=True, content=False)
    return file


def main():
    parser = argparse.ArgumentParser(description='FTP client')

    # positional argument
    parser.add_argument("file", help="file/folder path.", default="")
    # FLAGS
    # parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--zip_first", "-z", help="Zip before sending.", action="store_true")  # default is False
    parser.add_argument("--encrypt_first", "-e", help="Encrypt before sending.", action="store_true")  # default is False
    parser.add_argument("--relative_to_home", "-R", help="Zip before sending.", action="store_true")  # default is False

    # optional argument
    parser.add_argument("--remote_dir", "-d", help="Remote directory to send to.", default="")
    parser.add_argument("--google_account", "-a", help="Google Account.", default=None)
    parser.add_argument("--project", "-P", help="Project Name", default=None)
    parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    parser.add_argument("--pwd", "-p", help="Password for encryption", default=None)

    args = parser.parse_args()

    file = process_file(args)
    api = GDriveAPI(account=args.google_account, project=args.project)
    res = api.upload(local_path=file, remote_dir=args.remote_dir)  # , args.recursive, args.zipFirst)

    if args.zip_first or args.encrypt_first:
        P(file).delete(sure=True)
    _ = res


if __name__ == "__main__":
    main()
