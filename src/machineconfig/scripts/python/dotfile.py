"""Like yadm and dotter."""

from machineconfig.utils.path_reduced import PathExtended as PathExtended
from machineconfig.utils.links import symlink_func
from machineconfig.utils.source_of_truth import LIBRARY_ROOT, REPO_ROOT
import argparse


def main():
    parser = argparse.ArgumentParser(description="FTP client")

    parser.add_argument("file", help="file/folder path.", default="")
    # FLAGS
    parser.add_argument("--overwrite", "-o", help="Overwrite.", action="store_true")  # default is False
    # optional
    parser.add_argument("-d", "--dest", help="destination folder", default="")

    args = parser.parse_args()
    orig_path = PathExtended(args.file).expanduser().absolute()
    if args.dest == "":
        if "Local" in str(orig_path):
            junction = orig_path.split(at="Local", sep=-1)[1]
        elif "Roaming" in str(orig_path):
            junction = orig_path.split(at="Roaming", sep=-1)[1]
        elif ".config" in str(orig_path):
            junction = orig_path.split(at=".config", sep=-1)[1]
        else:
            junction = orig_path.rel2home()
        new_path = PathExtended(REPO_ROOT).joinpath(junction)
    else:
        dest_path = PathExtended(args.dest).expanduser().absolute()
        dest_path.mkdir(parents=True, exist_ok=True)
        new_path = dest_path.joinpath(orig_path.name)

    symlink_func(this=orig_path, to_this=new_path, prioritize_to_this=args.overwrite)

    print("""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ ✅ Symbolic Link Created Successfully
┃
┃ 🔄 To enshrine this mapping, add the following to mapper.toml:
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
    print(f"""
📝 Edit configuration file: nano {PathExtended(LIBRARY_ROOT)}/symlinks/mapper.toml

[{new_path.parent.name}]
{orig_path.name.split(".")[0]} = {{ this = '{orig_path.collapseuser().as_posix()}', to_this = '{new_path.collapseuser().as_posix()}' }}
""")


if __name__ == "__main__":
    main()
