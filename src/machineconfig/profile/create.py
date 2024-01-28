
"""
This script Takes away all config files from the computer, place them in one directory
`dotfiles`, and create symlinks to those files from thier original locations.

"""


from crocodile.environment import system, UserName  # ProgramFiles, WindowsApps  # , exe
from crocodile.meta import Terminal
from crocodile.file_management import P
from machineconfig.utils.utils import symlink, LIBRARY_ROOT, REPO_ROOT, display_options
from machineconfig.profile.shell import create_default_shell_profile
# import os
import subprocess
from rich.console import Console
from typing import Optional, Any


ERROR_LIST: list[Any] = []  # append to this after every exception captured.
CONFIG_ROOT = LIBRARY_ROOT.parent.parent.joinpath("settings")
OTHER_SYSTEM = "windows" if system == "Linux" else "linux"
SYSTEM = system.lower()


# =================== SYMLINKS ====================================


def symlink_contents(source_dir: P, target_dir: P, overwrite: bool = True):
    for a_target in target_dir.expanduser().search("*"):
        symlink(this=source_dir.joinpath(a_target.name), to_this=a_target, prioritize_to_this=overwrite)


def main_symlinks(choice: Optional[str] = None):
    symlink_mapper = LIBRARY_ROOT.joinpath("profile/mapper.toml").readit()
    symlink_mapper['wsl_windows']['home']["to_this"] = symlink_mapper['wsl_windows']['home']["to_this"].replace("username", UserName)
    symlink_mapper['wsl_linux']['home']["to_this"] = symlink_mapper['wsl_linux']['home']["to_this"].replace("username", UserName)

    overwrite = True
    exclude: list[str] = []  # "wsl_linux", "wsl_windows"

    program_keys_raw: list[str] = list(symlink_mapper.keys())
    program_keys: list[str] = []
    for program_key in program_keys_raw:
        if program_key in exclude or OTHER_SYSTEM in program_key:
            # print(f"Skipping {program_key} for {system}")
            continue
        else: program_keys.append(program_key)

    program_keys.sort()
    if choice is None:
        choice_selected = display_options(msg="Which symlink to create?", options=program_keys + ["all", "none(EXIT)"], default="none(EXIT)", fzf=True, multi=True)
        assert isinstance(choice_selected, list)
        if len(choice_selected) == 1 and choice_selected[0] == "none(EXIT)": return  # terminate function.
        elif len(choice_selected) == 1 and choice_selected[0] == "all": choice_selected = "all"  # i.e. program_keys = program_keys
        # overwrite = display_options(msg="Overwrite existing source file?", options=["yes", "no"], default="yes") == "yes"
        from rich.prompt import Confirm
        overwrite = Confirm.ask("Overwrite existing source file?", default=True)

    else: choice_selected = choice

    if isinstance(choice_selected, str):
        if str(choice_selected) == "all" and system == "Windows" and not Terminal.is_user_admin():
            print("*" * 200)
            raise RuntimeError(f"Run terminal as admin and try again, otherwise, there will be too many popups for admin requests and no chance to terminate the program.")
        elif choice_selected == "all":
            print(f"{program_keys=}")
            pass  # i.e. program_keys = program_keys
        else: program_keys = [choice_selected]
    else: program_keys = choice_selected

    for program_key in program_keys:
        for file_key, file_map in symlink_mapper[program_key].items():
            this = P(file_map['this'])
            to_this = P(file_map['to_this'].replace("REPO_ROOT", REPO_ROOT.as_posix()).replace("LIBRARY_ROOT", LIBRARY_ROOT.as_posix()))
            if "contents" in file_map:
                try: symlink_contents(source_dir=this, target_dir=to_this, overwrite=overwrite)
                except Exception as ex: print("Config error: ", program_key, file_key, "missing keys 'this ==> to_this'.", ex)
            else:
                try: symlink(this=this, to_this=to_this, prioritize_to_this=overwrite)
                except Exception as ex: print("Config error: ", program_key, file_key, "missing keys 'this ==> to_this'.", ex)

            if program_key == "ssh" and system == "Linux":  # permissions of ~/dotfiles/.ssh should be adjusted
                try:
                    subprocess.run(f"chmod 700 ~/.ssh/", check=True)
                    subprocess.run(f"chmod 700 ~/dotfiles/creds/.ssh/", check=True)  # may require sudo
                    subprocess.run(f"chmod 600 ~/dotfiles/creds/.ssh//*", check=True)
                except Exception as e:
                    ERROR_LIST.append(e)
                    print("Caught error", e)

    if system == "Linux": Terminal().run(f'chmod +x {LIBRARY_ROOT.joinpath(f"scripts/{system.lower()}")} -R')


def main(choice: Optional[str] = None):
    console = Console()
    print("\n")
    console.rule(f"CREATING SYMLINKS")
    main_symlinks(choice=choice)

    print("\n")
    console.rule(f"CREATING SYMLINKS")
    create_default_shell_profile()


if __name__ == '__main__':
    pass
