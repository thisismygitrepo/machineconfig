
from crocodile.comms.gdrive import GDriveAPI
# from crocodile.file_management import P
import argparse


def main(google_account, project, file, encrypt_first, z, relative_to_home, remote_dir, share, key, pwd):
    api = GDriveAPI(account=google_account, project=project)

    if share: res = api.upload_and_share(local_path=file, rel2home=relative_to_home,
                                         zip_first=z, encrypt_first=encrypt_first, key=key, pwd=pwd)
    else: res = api.upload(local_path=file, remote_dir=remote_dir, rel2home=relative_to_home,
                           zip_first=z, encrypt_first=encrypt_first, key=key, pwd=pwd)  # , recursive, zipFirst)
    print(res)


def args_parser():
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
    main(google_account=args.google_account, project=args.project, file=args.file, z=args.zip_first, relative_to_home=args.relative_to_home, remote_dir=args.remote_dir, share=args.share, key=args.key, pwd=args.pwd, encrypt_first=args.encrypt_first)


if __name__ == "__main__":
    args_parser()
