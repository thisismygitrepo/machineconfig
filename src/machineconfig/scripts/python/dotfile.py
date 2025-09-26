"""Like yadm and dotter."""

from machineconfig.utils.path_extended import PathExtended as PathExtended
from machineconfig.utils.links import symlink_func
from machineconfig.utils.source_of_truth import LIBRARY_ROOT, REPO_ROOT
from typing import Annotated
import typer


def main(
    file: Annotated[str, typer.Argument(help="file/folder path.")],
    overwrite: Annotated[bool, typer.Option("--overwrite", "-o", help="Overwrite.")] = False,
    dest: Annotated[str, typer.Option("--dest", "-d", help="destination folder")] = "",
) -> None:
    orig_path = PathExtended(file).expanduser().absolute()
    if dest == "":
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
        dest_path = PathExtended(dest).expanduser().absolute()
        dest_path.mkdir(parents=True, exist_ok=True)
        new_path = dest_path.joinpath(orig_path.name)

    symlink_func(this=orig_path, to_this=new_path, prioritize_to_this=overwrite)

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


def arg_parser() -> None:
    typer.run(main)


if __name__ == "__main__":
    arg_parser()
