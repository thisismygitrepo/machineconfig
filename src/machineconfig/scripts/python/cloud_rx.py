
import crocodile.toolbox as tb
import argparse


def arg_parser():
    parser = argparse.ArgumentParser(description='Cloud Download CLI.')

    # positional argument
    parser.add_argument("cloud", help="rclone cloud profile name.")
    parser.add_argument("file", help="file/folder path to be received.", default="")
    # FLAGS
    # parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--decrypt", "-e", help="Decrypt after receiving.", action="store_true")  # default is False
    parser.add_argument("--unzip", "-z", help="unzip after receiving.", action="store_true")  # default is False
    parser.add_argument("--overwrite", "-o", help="Overwrite existing file.", action="store_true")  # default is False
    # optional argument
    parser.add_argument("--remote_dir", "-d", help="Remote directory to send to.", default="")
    parser.add_argument("--relative_to_home", "-r", help="Relative to `myhome` folder", action="store_true")  # default is False
    parser.add_argument("--generic_os", "-g", help="Generic OS path (relevant only when relative flag is raised as well.", action="store_true")
    parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    parser.add_argument("--pwd", "-p", help="Password for encryption", default=None)

    args = parser.parse_args()
    tb.P(args.file).from_cloud(cloud=args.cloud, unzip=args.unzip, decrypt=args.decrypt, overwrite=args.overwrite, pwd=args.pwd, key=args.key,
                               rel2home=args.relative_to_home, generic_os=args.generic_os,)


if __name__ == "__main__":
    arg_parser()
