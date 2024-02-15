
"""Like yadm and dotter.
"""


from crocodile.file_management import P
from machineconfig.profile.create import symlink
from machineconfig.utils.utils import LIBRARY_ROOT, REPO_ROOT
import argparse


def main():
    parser = argparse.ArgumentParser(description='FTP client')

    parser.add_argument("file", help="file/folder path.", default="")
    # FLAGS
    parser.add_argument("--overwrite", "-o", help="Overwrite.", action="store_true")  # default is False
    # optional
    parser.add_argument("-d", "--dest", help=f"destination folder", default="")

    args = parser.parse_args()
    orig_path = P(args.file).expanduser().absolute()
    if args.dest == "":
        if "Local" in orig_path: junction = orig_path.split(at="Local", sep=-1)[1]
        elif "Roaming" in orig_path: junction = orig_path.split(at="Roaming", sep=-1)[1]
        elif ".config" in orig_path: junction = orig_path.split(at=".config", sep=-1)[1]
        else: junction = orig_path.rel2home()
        new_path = REPO_ROOT.joinpath(junction)
    else: new_path = P(args.dest).expanduser().absolute().create().joinpath(orig_path.name)

    symlink(this=orig_path, to_this=new_path, prioritize_to_this=args.overwrite)

    print(f"Map completed. To enshrine this mapping, add the following line to the mapper.toml file:")
    print(f"nano {LIBRARY_ROOT}/symlinks/mapper.toml")
    print(f"""
[{new_path.parent.name}]
{orig_path.trunk} = {{ this = '{orig_path.collapseuser().as_posix()}', to_this = '{new_path.collapseuser().as_posix()}' }}
""")


if __name__ == '__main__':
    main()
