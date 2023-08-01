
import crocodile.toolbox as tb
import argparse
from machineconfig.scripts.python.cloud_sync import parse_cloud_source_target


def arg_parser():
    parser = argparse.ArgumentParser(description='Cloud Download CLI.')

    # positional argument
    parser.add_argument("source", help="file/folder path to be taken from here.", default=None)
    parser.add_argument("target", help="file/folder path to be be sent to here.", default=None)
    # FLAGS
    # parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--encrypt", "-e", help="Decrypt after receiving.", action="store_true")  # default is False
    parser.add_argument("--zip", "-z", help="unzip after receiving.", action="store_true")  # default is False
    parser.add_argument("--overwrite", "-w", help="Overwrite existing file.", action="store_true")  # default is False
    parser.add_argument("--share", "-s", help="Share file / directory", action="store_true")  # default is False
    # optional argument
    parser.add_argument("--relative_to_home", "-r", help="Relative to `myhome` folder", action="store_true")  # default is False
    parser.add_argument("--root", "-R", help="Remote root.", default="myhome")  # default is False
    parser.add_argument("--os_specific", "-o", help="OS specific path (relevant only when relative flag is raised as well.", action="store_true")

    parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    parser.add_argument("--pwd", "-p", help="Password for encryption", default=None)

    args = parser.parse_args()
    cloud, source, target = parse_cloud_source_target(args)

    # if args.cloud is None:
    #     _path = tb.P.home().joinpath("dotfiles/machineconfig/setup/rclone_remote")
    #     try: cloud = _path.read_text().replace("\n", "")
    #     except FileNotFoundError:
    #         print(f"No cloud profile found @ {_path}, please set one up or provide one via the --cloud flag.")
    #         return ""
    # else: cloud = args.cloud
    if cloud in source:
        tb.P(target).from_cloud(cloud=cloud,
                                unzip=args.zip, decrypt=args.encrypt, overwrite=args.overwrite,
                                pwd=args.pwd, key=args.key,
                                rel2home=args.relative_to_home, os_specific=args.os_specific, root=args.root)
    elif cloud in target:
        res = tb.P(source).to_cloud(cloud=cloud, zip=args.zip, rel2home=args.relative_to_home, root=args.root,
                                        share=args.share, key=args.key, pwd=args.pwd, encrypt=args.encrypt, os_specific=args.os_specific,)
        if args.share: print(res.as_url_str())
    else:
        raise ValueError(f"Cloud `{cloud}` not found in source or target.")


if __name__ == "__main__":
    arg_parser()
