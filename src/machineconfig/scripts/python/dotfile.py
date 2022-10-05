
import argparse
import crocodile.toolbox as tb
from machineconfig.profile.create import symlink


def main():
    parser = argparse.ArgumentParser(description='FTP client')

    parser.add_argument("file", help="file/folder path.", default="")
    parser.add_argument("dest", help=f"destination folder", default="")
    # FLAGS
    parser.add_argument("--overwrite", "-o", help="Overwrite.", action="store_true")  # default is False

    args = parser.parse_args()
    orig_path = tb.P(args.file).expanduser().absolute()
    new_path = tb.P(args.dest).expanduser().absolute().create().joinpath(orig_path.name)

    symlink(this=orig_path, to_this=new_path, overwrite=args.overwrite)

    print(f"Map completed. To enshrine this mapping, add the following line to the mapper.toml file:")
    print("nano ~/code/machineconfig/src/machineconfig/symlinks/mapper.toml")
    print(f"""
[{new_path.parent.name}]
{orig_path.trunk} = {{ this = '{orig_path.collapseuser()}', to_this = '{new_path.collapseuser()}' }}
""")


if __name__ == '__main__':
    main()
