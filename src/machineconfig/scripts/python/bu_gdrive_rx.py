

from crocodile.comms.gdrive import GDriveAPI
# from crocodile.file_management import P
import argparse


def main(google_account, project, file, unzip, relative_to_home, decrypt, key, pwd, local_dir):
    api = GDriveAPI(account=google_account, project=project)

    if "http" in file: path = api.download(furl=file, local_dir=local_dir, rel2home=relative_to_home)  # , recursive, zipFirst)
    else:
        file = file
        path = api.download(fpath=file, local_dir=local_dir, rel2home=relative_to_home, decrypt=decrypt, unzip=unzip, key=key, pwd=pwd)  # , recursive, zipFirst)
    print(path)


def arg_parser():
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
    main(google_account=args.google_account, project=args.project, file=args.file,
         unzip=args.unzip, relative_to_home=args.relative_to_home, decrypt=args.decrypt, key=args.key, pwd=args.pwd, local_dir=args.local_dir)


if __name__ == "__main__":
    arg_parser()
