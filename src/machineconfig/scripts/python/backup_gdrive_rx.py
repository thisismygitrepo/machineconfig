

from crocodile.comms.gdrive import GDriveAPI
# from crocodile.file_management import *
import argparse


def main():
    parser = argparse.ArgumentParser(description='FTP client')

    # positional argument
    parser.add_argument("file", help="file/folder path.", default="")
    # FLAGS
    # parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False

    # optional argument
    parser.add_argument("--local_dir", "-d", help="Remote directory to send to.", default="")
    parser.add_argument("--google_account", "-a", help="Google Account.", default=None)
    parser.add_argument("--project", "-P", help="Project Name", default=None)
    parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    parser.add_argument("--pwd", "-p", help="Password for encryption", default=None)

    args = parser.parse_args()

    api = GDriveAPI(account=args.google_account, project=args.project)
    res = api.download(fpath=args.file, local_dir=args.local_dir)
    _ = res


if __name__ == "__main__":
    main()
