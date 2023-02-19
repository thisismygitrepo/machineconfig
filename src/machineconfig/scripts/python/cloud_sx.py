
import crocodile.toolbox as tb
import argparse
# import subprocess


def args_parser():
    parser = argparse.ArgumentParser(description='Cloud Management CLI.')

    # positional argument
    parser.add_argument("cloud", help="rclone cloud profile name.")
    parser.add_argument("file", help="file/folder path.")
    # FLAGS
    parser.add_argument("--zip", "-z", help="Zip before sending.", action="store_true")  # default is False
    parser.add_argument("--encrypt", "-e", help="Encrypt before sending.", action="store_true")  # default is False
    parser.add_argument("--relative_to_home", "-r", help="set remote path as home relative local path.", action="store_true")  # default is False
    parser.add_argument("--os_specific", "-o", help="OS specific path (relevant only when relative flag is raised as well.", action="store_true")
    parser.add_argument("--share", "-s", help="Share file.", action="store_true")
    # optional argument
    parser.add_argument("--remote_dir", "-d", help="Remote directory to send to.", default="")
    parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    parser.add_argument("--pwd", "-p", help="Password for encryption", default=None)

    args = parser.parse_args()
    res = tb.P(args.file).to_cloud(cloud=args.cloud, zip=args.zip, rel2home=args.relative_to_home,
                                   share=args.share, key=args.key, pwd=args.pwd, encrypt=args.encrypt, os_specific=args.os_specific,)
    if args.share: print(res.as_url_str())


if __name__ == "__main__":
    args_parser()
