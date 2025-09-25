"""
This script Takes away all config files from the computer, place them in one directory
`dotfiles`, and create symlinks to those files from thier original locations.

"""

from rich.console import Console

from machineconfig.utils.path_reduced import PathExtended as PathExtended
from machineconfig.utils.links import symlink_func, symlink_copy
from machineconfig.utils.options import display_options
from machineconfig.utils.source_of_truth import LIBRARY_ROOT, REPO_ROOT
from machineconfig.utils.utils2 import read_toml
from machineconfig.profile.shell import create_default_shell_profile

import platform
import os
import ctypes
import subprocess
from typing import Optional, Any, TypedDict

system = platform.system()  # Linux or Windows
ERROR_LIST: list[Any] = []  # append to this after every exception captured.
SYSTEM = system.lower()


def get_other_systems(current_system: str) -> list[str]:
    all_systems = ["linux", "windows", "darwin"]
    return [s for s in all_systems if s != current_system.lower()]


OTHER_SYSTEMS = get_other_systems(SYSTEM)


class SymlinkMapper(TypedDict):
    this: str
    to_this: str
    contents: Optional[bool]


def apply_mapper(choice: Optional[str] = None):
    symlink_mapper: dict[str, dict[str, SymlinkMapper]] = read_toml(LIBRARY_ROOT.joinpath("profile/mapper.toml"))
    prioritize_to_this = True
    exclude: list[str] = []  # "wsl_linux", "wsl_windows"

    program_keys_raw: list[str] = list(symlink_mapper.keys())
    program_keys: list[str] = []
    for program_key in program_keys_raw:
        if program_key in exclude or any([another_system in program_key for another_system in OTHER_SYSTEMS]):
            continue
        else:
            program_keys.append(program_key)

    program_keys.sort()
    if choice is None:
        choice_selected = display_options(msg="Which symlink to create?", options=program_keys + ["all", "none(EXIT)"], default="none(EXIT)", fzf=True, multi=True)
        assert isinstance(choice_selected, list)
        if len(choice_selected) == 1 and choice_selected[0] == "none(EXIT)":
            return  # terminate function.
        elif len(choice_selected) == 1 and choice_selected[0] == "all":
            choice_selected = "all"  # i.e. program_keys = program_keys
        # overwrite = display_options(msg="Overwrite existing source file?", options=["yes", "no"], default="yes") == "yes"
        from rich.prompt import Confirm

        prioritize_to_this = Confirm.ask("Overwrite existing source file?", default=True)
    else:
        choice_selected = choice

    if isinstance(choice_selected, str):
        if str(choice_selected) == "all" and system == "Windows":
            if os.name == "nt":
                try:
                    is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                except Exception:
                    is_admin = False
            else:
                is_admin = False
            if not is_admin:
                print(f"""
{"*" * 80}
⚠️  WARNING: Administrator privileges required
{"*" * 80}
""")
                raise RuntimeError("Run terminal as admin and try again, otherwise, there will be too many popups for admin requests and no chance to terminate the program.")
        elif choice_selected == "all":
            print(f"""
🔍 Processing all program keys:
{program_keys}
""")
            pass  # i.e. program_keys = program_keys
        else:
            program_keys = [choice_selected]
    else:
        program_keys = choice_selected

    for program_key in program_keys:
        print(f"\n🔄 Processing {program_key} symlinks...")
        for file_key, file_map in symlink_mapper[program_key].items():
            this = PathExtended(file_map["this"])
            to_this = PathExtended(file_map["to_this"].replace("REPO_ROOT", REPO_ROOT.as_posix()).replace("LIBRARY_ROOT", LIBRARY_ROOT.as_posix()))
            if "contents" in file_map:
                try:
                    for a_target in to_this.expanduser().search("*"):
                        symlink_func(this=this.joinpath(a_target.name), to_this=a_target, prioritize_to_this=prioritize_to_this)
                except Exception as ex:
                    print(f"❌ Config error: {program_key} | {file_key} | missing keys 'this ==> to_this'. {ex}")
            if "copy" in file_map:
                try:
                    symlink_copy(this=this, to_this=to_this, prioritize_to_this=prioritize_to_this)
                except Exception as ex:
                    print(f"❌ Config error: {program_key} | {file_key} | {ex}")
            else:
                try:
                    symlink_func(this=this, to_this=to_this, prioritize_to_this=prioritize_to_this)
                except Exception as ex:
                    print(f"❌ Config error: {program_key} | {file_key} | missing keys 'this ==> to_this'. {ex}")

            if program_key == "ssh" and system == "Linux":  # permissions of ~/dotfiles/.ssh should be adjusted
                try:
                    print("\n🔒 Setting secure permissions for SSH files...")
                    subprocess.run("chmod 700 ~/.ssh/", check=True)
                    subprocess.run("chmod 700 ~/dotfiles/creds/.ssh/", check=True)  # may require sudo
                    subprocess.run("chmod 600 ~/dotfiles/creds/.ssh/*", check=True)
                    print("✅ SSH permissions set successfully")
                except Exception as e:
                    ERROR_LIST.append(e)
                    print(f"❌ Error setting SSH permissions: {e}")

    if system == "Linux":
        print("\n📜 Setting executable permissions for scripts...")
        subprocess.run(f"chmod +x {LIBRARY_ROOT.joinpath(f'scripts/{system.lower()}')} -R", shell=True, capture_output=True, text=True)
        print("✅ Script permissions updated")

    if len(ERROR_LIST) > 0:
        print(f"""
{"*" * 80}
❗ ERRORS ENCOUNTERED DURING PROCESSING
{"*" * 80}
{ERROR_LIST}
{"*" * 80}
""")
    else:
        print(f"""
{"*" * 80}
✅ All symlinks created successfully!
{"*" * 80}
""")


def main(choice: Optional[str] = None):
    console = Console()
    print("\n")

    console.rule("[bold blue]🔗 CREATING SYMLINKS 🔗")
    apply_mapper(choice=choice)

    print("\n")
    console.rule("[bold green]🐚 CREATING SHELL PROFILE 🐚")
    create_default_shell_profile()

    print(f"""
{"=" * 80}
✨ Configuration setup complete! ✨
{"=" * 80}
""")


if __name__ == "__main__":
    pass
