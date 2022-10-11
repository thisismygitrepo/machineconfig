
from crocodile.comms.gdrive import GDriveAPI
from crocodile.file_management import P
import argparse


def main():
    parser = argparse.ArgumentParser(description='FTP client')

    # positional argument
    parser.add_argument("file", help="file/folder path.", default="")
    # FLAGS
    # parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--zip_first", "-z", help="Zip before sending.", action="store_true")  # default is False
    parser.add_argument("--encrypt_first", "-e", help="Encrypt before sending.", action="store_true")  # default is False
    parser.add_argument("--relative_to_home", "-R", help="Zip before sending.", action="store_true")  # default is False
    parser.add_argument("--share", "-s", help="Share file.", action="store_true")
    # optional argument
    parser.add_argument("--remote_dir", "-d", help="Remote directory to send to.", default="")
    parser.add_argument("--google_account", "-a", help="Google Account.", default=None)
    parser.add_argument("--project", "-P", help="Project Name", default=None)
    parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    parser.add_argument("--pwd", "-p", help="Password for encryption", default=None)

    args = parser.parse_args()
    api = GDriveAPI(account=args.google_account, project=args.project)

    if args.share: res = api.upload_and_share(local_path=args.file, rel2home=args.relative_to_home,
                                              zip_first=args.zip_first, encrypt_first=args.encrypt_first, key=args.key, pwd=args.pwd)
    else: res = api.upload(local_path=args.file, remote_dir=args.remote_dir, rel2home=args.relative_to_home,
                           zip_first=args.zip_first, encrypt_first=args.encrypt_first, key=args.key, pwd=args.pwd)  # , args.recursive, args.zipFirst)
    print(res)


if __name__ == "__main__":
    main()
