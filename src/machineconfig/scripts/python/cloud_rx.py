
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
    parser.add_argument("--overwrite", "-w", help="Overwrite existing file.", action="store_true")  # default is False
    # optional argument
    parser.add_argument("--localpath", "-l", help="Local path to save to.", default=None)
    parser.add_argument("--remote_dir", "-d", help="Remote directory to send to.", default="")
    parser.add_argument("--relative_to_home", "-r", help="Relative to `myhome` folder", action="store_true")  # default is False
    parser.add_argument("--os_specific", "-o", help="OS specific path (relevant only when relative flag is raised as well.", action="store_true")
    parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    parser.add_argument("--pwd", "-p", help="Password for encryption", default=None)

    args = parser.parse_args()

    if args.cloud is None:
        _path = tb.P.home().joinpath("dotfiles/config/setup/rclone_remote")
        try: cloud = _path.read_text().replace("\n", "")
        except FileNotFoundError:
            print(f"No cloud profile found @ {_path}, please set one up or provide one via the --cloud flag.")
            return ""
    else: cloud = args.cloud


    tb.P(args.file).from_cloud(cloud=cloud, localpath=args.localpath,
                               unzip=args.unzip, decrypt=args.decrypt, overwrite=args.overwrite,
                               pwd=args.pwd, key=args.key,
                               rel2home=args.relative_to_home, os_specific=args.os_specific,)


if __name__ == "__main__":
    arg_parser()
