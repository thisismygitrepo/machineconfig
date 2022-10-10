
import argparse
import crocodile.toolbox as tb
from machineconfig.profile.create import symlink


def main():
    parser = argparse.ArgumentParser(description='FTP client')

    parser.add_argument("file", help="file/folder path.", default="")
    # FLAGS
    parser.add_argument("--overwrite", "-o", help="Overwrite.", action="store_true")  # default is False
    # optional
    parser.add_argument("-d", "--dest", help=f"destination folder", default="")

    args = parser.parse_args()
    orig_path = tb.P(args.file).expanduser().absolute()
    if args.dest == "":
        if "Local" in orig_path: junction = orig_path.split(at="Local", sep=-1)[1]
        elif "Roaming" in orig_path: junction = orig_path.split(at="Roaming", sep=-1)[1]
        elif ".config" in orig_path: junction = orig_path.split(at=".config", sep=-1)[1]
        else: junction = orig_path.rel2home()
        new_path = tb.P.home().joinpath("code/machineconfig/settings", junction)
    else: new_path = tb.P(args.dest).expanduser().absolute().create().joinpath(orig_path.name)

    symlink(this=orig_path, to_this=new_path, overwrite=args.overwrite)

    print(f"Map completed. To enshrine this mapping, add the following line to the mapper.toml file:")
    print("nano ~/code/machineconfig/src/machineconfig/symlinks/mapper.toml")
    print(f"""
[{new_path.parent.name}]
{orig_path.trunk} = {{ this = '{orig_path.collapseuser().as_posix()}', to_this = '{new_path.collapseuser().as_posix()}' }}
""")


if __name__ == '__main__':
    main()
