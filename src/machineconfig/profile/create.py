
"""
This script Takes away all config files from the computer, place them in one directory
`dotfiles`, and create symlinks to those files from thier original locations.
"""

import crocodile.toolbox as tb
from crocodile.environment import DotFiles, system, PathVar, UserName  # ProgramFiles, WindowsApps  # , exe
from machineconfig.utils.utils import symlink, LIBRARY_ROOT, REPO_ROOT, display_options
# import os
import subprocess
from rich.console import Console


ERROR_LIST = []  # append to this after every exception captured.
CONFIG_ROOT = LIBRARY_ROOT.parent.parent.joinpath("settings")
OTHER_SYSTEM = "windows" if system == "Linux" else "linux"
SYSTEM = system.lower()


# =================== SYMLINKS ====================================


def link_ssh(overwrite=True):
    """The function can link aribtrary number of files without linking the directory itself (which is not doable in toml config file)"""
    path = tb.P.home().joinpath(".ssh")
    target = DotFiles.joinpath("creds/.ssh")
    for item in target.search("*"):
        # if "authorized_keys" in item: continue
        symlink(path.joinpath(item.name), item, prioritize_to_this=overwrite)
    if system == "Linux":  # permissions of ~/dotfiles/.ssh should be adjusted
        try:
            subprocess.run(f"chmod 700 ~/.ssh/")
            subprocess.run(f"chmod 700 {target.collapseuser().as_posix()}/")  # may require sudo
            subprocess.run(f"chmod 600 {target.collapseuser().as_posix()}/*")
        except Exception as e:
            ERROR_LIST.append(e)
            print("Caught error", e)


def link_aws(overwrite=True):
    path = tb.P.home().joinpath(".aws")
    target = DotFiles.joinpath("aws/.aws")
    for item in target.search("*"): symlink(path.joinpath(item.name), item, prioritize_to_this=overwrite)


def main_symlinks(choice=None):
    symlink_mapper = LIBRARY_ROOT.joinpath("profile/mapper.toml").readit()
    symlink_mapper['wsl_windows']['home']["to_this"] = symlink_mapper['wsl_windows']['home']["to_this"].replace("username", UserName)
    symlink_mapper['wsl_linux']['home']["to_this"] = symlink_mapper['wsl_linux']['home']["to_this"].replace("username", UserName)

    overwrite = True
    exclude = ["autostart_windows"]  # "wsl_linux", "wsl_windows"

    program_keys_raw = list(symlink_mapper.keys()) + ["aws", "ssh"]
    program_keys = []
    for program_key in program_keys_raw:
        if program_key in exclude or OTHER_SYSTEM in program_key:
            # print(f"Skipping {program_key} for {system}")
            continue
        else: program_keys.append(program_key)

    program_keys.sort()
    if choice is None:
        choice = display_options(msg="Which symlink to create?", options=program_keys + ["all", "none"], default="none", fzf=True, multi=True)
        if str(choice) == "none": return

        overwrite = display_options(msg="Overwrite existing source file?", options=["yes", "no"], default="yes") == "yes"

    if isinstance(choice, str):
        if str(choice) == "all" and system == "Windows" and not tb.Terminal.is_user_admin():
            print("*" * 200)
            raise RuntimeError(f"Run terminal as admin and try again, otherwise, there will be too many popups for admin requests and no chance to terminate the program.")
        elif choice == "all": pass  # i.e. program_keys = program_keys
        else: program_keys = [choice]
    elif isinstance(choice, list): program_keys = choice
    else: raise ValueError(f"Choice must be a string or a list of strings, not {type(choice)}")

    for program_key in program_keys:
        if program_key == "aws":
            link_aws(overwrite=overwrite)
            continue
        elif program_key == "ssh":
            link_ssh(overwrite=overwrite)
            continue
        for file_key, file_map in symlink_mapper[program_key].items():
            try: symlink(this=file_map['this'], to_this=file_map['to_this'].replace("REPO_ROOT", REPO_ROOT.as_posix()).replace("LIBRARY_ROOT", LIBRARY_ROOT.as_posix()), prioritize_to_this=overwrite)
            except Exception as ex: print("Config error: ", program_key, file_key, "missing keys 'this ==> to_this'.", ex)

    if system == "Linux": tb.Terminal().run(f'chmod +x {LIBRARY_ROOT.joinpath(f"scripts/{system.lower()}")} -R')


# --------------------------------------- SHELL PROFILE --------------------------------------------------------
# The following is not a symlink creation, but modification of shell profile by additing dirs to PATH
# Shell profile is either in dotfiles and is synced (as in Windows), hence no need for update, or is updated on the fly (for Linux)
# for windows it won't change the profile, if the profile was modified already e.g. due to syncing


def get_shell_profile_path():
    if system == "Windows": profile_path = tb.Terminal().run("$profile", shell="pwsh").op2path()
    elif system == "Linux": profile_path = tb.P("~/.bashrc").expanduser()
    else: raise ValueError(f"Not implemented for this system {system}")
    print(f"Working on shell profile `{profile_path}`")
    return profile_path


def main_env_path(choice=None, profile_path=None):
    env_path = LIBRARY_ROOT.joinpath("profile/env_path.toml").readit()
    dirs = env_path[f'path_{system.lower()}']['extension']

    print(f"Current PATH: ", "\n============")
    tb.P.get_env().PATH.print()

    if choice is None:
        choice = display_options(msg="Which directory to add?", options=dirs + ["all", "none"], default="none")
        if str(choice) != "all": dirs = [choice]
    if choice == "none": return

    addition = PathVar.append_temporarily(dirs=dirs)
    profile_path = profile_path or get_shell_profile_path()
    profile_path.copy(name=profile_path.name + f".orig_" + tb.randstr())
    profile_path.modify_text(addition, addition, replace_line=False, notfound_append=True)


def main_add_sources_to_shell_profile(profile_path=None, choice=None):
    sources = LIBRARY_ROOT.joinpath("profile/sources.toml").readit()[system.lower()]['files']

    if choice is None:
        choice = display_options(msg="Which patch to add?", options=sources + ["all", "none"], default="none")
        if str(choice) != "all": sources = [choice]
    if choice == "none": return

    profile_path = profile_path or get_shell_profile_path()
    profile = profile_path.read_text()

    for a_file in sources:
        file = a_file.replace("REPO_ROOT", REPO_ROOT.as_posix()).replace("LIBRARY_ROOT", LIBRARY_ROOT.as_posix())
        file = tb.P(file).collapseuser()  # this makes the shell profile interuseable across machines.
        file = file.as_posix() if system == "Linux" else str(file)
        if file not in profile:
            if system == "Windows": profile += f"\n. {file}"
            elif system == "Linux": profile += f"\nsource {file}"
            else: raise ValueError(f"Not implemented for this system {system}")
        else: print(f"SKIPPED source `{file}`, it is already sourced in shell profile.")
    profile_path.write_text(profile)


def main_add_patches_to_shell_profile(profile_path=None, choice=None):
    patches: list[tb.P] = list(LIBRARY_ROOT.joinpath(f"profile/patches/{system.lower()}").search())

    if choice is None:
        choice = display_options(msg="Which patch to add?", options=list(patches) + ["all", "none"], default="none")
    if choice == "none": return None
    elif str(choice) == "all": pass  # i.e. patches = patches
    elif isinstance(choice, (str, tb.P)): patches = [tb.P(choice)]
    else: raise ValueError(f"Choice must be a string or a list of strings, not {type(choice)}")

    profile_path = profile_path or get_shell_profile_path()
    profile = profile_path.read_text()

    for patch_path in patches:
        patch = patch_path.read_text()
        if patch in profile: print(f"Skipping `{patch_path.name}`; patch already in profile")
        else: profile += "\n" + patch

    if system == "Linux":
        res = tb.Terminal().run("cat /proc/version").op
        if "microsoft" in res.lower() or "wsl" in res.lower():
            profile += "\ncd ~"  # this is to make sure that the current dir is not in the windows file system, which is terribly slow and its a bad idea to be there anyway.

    profile_path.write_text(profile)


def main(choice=None):
    console = Console()
    print("\n")
    console.rule(f"CREATING SYMLINKS")

    # the only common choice among all programs below is "all".
    main_symlinks(choice=choice)

    # print("\n")
    # console.rule(f"ADDING ENV PATH")
    # main_env_path(choice=choice)
    # print("\n")
    # console.rule(f"ADDING SOURCES TO SHELL PROFILE")
    # main_add_sources_to_shell_profile(choice=choice)
    # print("\n")
    # console.rule(f"ADDING PATCHES TO SHELL PROFILE")
    # main_add_patches_to_shell_profile(choice=choice)

    profile_path = get_shell_profile_path()
    profile = profile_path.read_text()
    source = f". {LIBRARY_ROOT.joinpath('settings/shells/pwsh/init.ps1').collapseuser()}" if system == "Windows" else f"source {LIBRARY_ROOT.joinpath('settings/shells/bash/init.sh')}"
    if source in profile: print(f"Skipping sourcing init script; already in profile")
    else:
        profile += "\n" + source + "\n"
        if system == "Linux":
            res = tb.Terminal().run("cat /proc/version").op
            if "microsoft" in res.lower() or "wsl" in res.lower():
                profile += "\ncd ~"  # this is to make sure that the current dir is not in the windows file system, which is terribly slow and its a bad idea to be there anyway.
        profile_path.write_text(profile)


if __name__ == '__main__':
    pass
