

from crocodile.comms.gdrive import GDriveAPI
# from crocodile.file_management import *
import argparse


def process_file(args, path):
    if args.decrypt:
        path = path.decrypt(key=args.key, pwd=args.pwd, inplace=True)
    if args.unzip:
        path = path.unzip(inplace=True, verbose=True, overwrite=True, content=True)
    return path


def main():
    parser = argparse.ArgumentParser(description='FTP client')

    # positional argument
    parser.add_argument("file", help="file/folder path.", default="")
    # FLAGS
    # parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--relative_to_home", "-R", help="Download to a directory to make it relative to home.", action="store_true")  # default is False
    parser.add_argument("--decrypt", "-e", help="decrypt file.", action="store_true")  # default is False
    parser.add_argument("--unzip", "-z", help="unzip file.", action="store_true")  # default is False

    # optional argument
    parser.add_argument("--local_dir", "-d", help="Remote directory to send to.", default="")

    parser.add_argument("--google_account", "-a", help="Google Account.", default=None)
    parser.add_argument("--project", "-P", help="Project Name", default=None)

    parser.add_argument("--key", "-k", help="Key for decryption", default=None)
    parser.add_argument("--pwd", "-p", help="Password for decryption", default=None)

    args = parser.parse_args()

    api = GDriveAPI(account=args.google_account, project=args.project)
    if "http" in args.file: path = api.download(furl=args.file, local_dir=args.local_dir, rel2home=args.relative_to_home)  # , args.recursive, args.zipFirst)
    else: path = api.download(fpath=args.file, local_dir=args.local_dir, rel2home=args.relative_to_home)  # , args.recursive, args.zipFirst)
    path = process_file(args, path)
    print(path)


if __name__ == "__main__":
    main()
