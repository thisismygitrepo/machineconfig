
"""
This script Takes away all config files from the computer, place them in one directory
`dotfiles`, and create symlinks to those files from thier original locations.
"""

import crocodile.toolbox as tb
from crocodile.environment import DotFiles, system, PathVar, UserName  # ProgramFiles, WindowsApps  # , exe
from machineconfig.utils.utils import symlink, LIBRARY_ROOT, REPO_ROOT, display_options
# import os
import subprocess


ERROR_LIST = []  # append to this after every exception captured.
CONFIG_ROOT = LIBRARY_ROOT.parent.parent.joinpath("settings")
OTHER_SYSTEM = "windows" if system == "Linux" else "linux"

# =================== SYMLINKS ====================================


def link_ssh(overwrite=True):
    """The function can link aribtrary number of files without linking the directory itself (which is not doable in toml config file)"""
    path = tb.P.home().joinpath(".ssh")
    target = DotFiles.joinpath(".ssh")
    for item in target.search("*"):
        # if "authorized_keys" in item: continue
        symlink(path.joinpath(item.name), item, overwrite=overwrite)
    if system == "Linux":  # permissions of ~/dotfiles/.ssh should be adjusted
        try:
            subprocess.run("chmod 700 ~/dotfiles/.ssh/")  # may require sudo
            subprocess.run("chmod 600 ~/dotfiles/.ssh/*")
        except Exception as e:
            ERROR_LIST.append(e)
            print("Caught error", e)


def link_aws(overwrite=True):
    path = tb.P.home().joinpath(".aws")
    target = DotFiles.joinpath("aws/.aws")
    for item in target.search("*"): symlink(path.joinpath(item.name), item, overwrite=overwrite)


def main_symlinks():
    symlink_mapper = LIBRARY_ROOT.joinpath("profile/mapper.toml").readit()
    symlink_mapper['wsl_windows']['home']["to_this"] = symlink_mapper['wsl_windows']['home']["to_this"].replace("username", UserName)
    symlink_mapper['wsl_linux']['home']["to_this"] = symlink_mapper['wsl_linux']['home']["to_this"].replace("username", UserName)

    overwrite = True
    exclude = ["autostart_windows"]  # "wsl_linux", "wsl_windows"

    program_keys = list(symlink_mapper.keys()) + ["aws", "ssh"]
    choice = display_options(msg="Which symlink to create?", options=program_keys + ["all"], default="all")
    if str(choice) == "all":
        if system == "Windows" and not tb.Terminal.is_user_admin():
            print("*" * 200)
            raise RuntimeError(f"Run terminal as admin and try again, otherwise, there will be too many popups for admin requests and no chance to terminate the program.")
    else: program_keys = [choice]

    for program_key in program_keys:
        if program_key == "aws":
            link_aws(overwrite=overwrite)
            continue
        elif program_key == "ssh":
            link_ssh(overwrite=overwrite)
            continue
        if program_key in exclude or OTHER_SYSTEM in program_key:
            print(f"Skipping {program_key} for {system}")
            continue
        for file_key, file_map in symlink_mapper[program_key].items():
            try: symlink(this=file_map['this'], to_this=file_map['to_this'].replace("REPO_ROOT", REPO_ROOT.as_posix()).replace("LIBRARY_ROOT", LIBRARY_ROOT.as_posix()), overwrite=overwrite)
            except Exception as ex: print("Config error: ", program_key, file_key, "missing keys 'this ==> to_this'.", ex)

    if system == "Linux": tb.Terminal().run(f'chmod +x {LIBRARY_ROOT.joinpath(f"scripts/{system.lower()}")} -R')


# --------------------------------------- SHELL PROFILE --------------------------------------------------------
# The following is not a symlink creation, but modification of shell profile by additing dirs to PATH
# Shell profile is either in dotfiles and is synced (as in Windows), hence no need for update, or is updated on the fly (for Linux)
# for windows it won't change the profile, if the profile was modified already e.g. due to syncing


def get_shell_profile_path():
    if system == "Windows": profile_path = tb.Terminal().run("$profile", shell="pwsh").as_path
    elif system == "Linux": profile_path = tb.P("~/.bashrc").expanduser()
    else: raise ValueError(f"Not implemented for this system {system}")
    print(f"Working on shell profile `{profile_path}`")
    return profile_path


def main_env_path(profile_path=None):
    env_path = LIBRARY_ROOT.joinpath("profile/env_path.toml").readit()
    dirs = env_path[f'path_{system.lower()}']['extension']
    addition = PathVar.append_temporarily(dirs=dirs)
    profile_path = profile_path or get_shell_profile_path()
    profile_path.copy(name=profile_path.name + f".orig_" + tb.randstr())
    profile_path.modify_text(addition, addition, replace_line=False, notfound_append=True)


def main_add_sources_to_shell_profile(profile_path=None):
    sources = LIBRARY_ROOT.joinpath("profile/sources.toml").readit()

    profile_path = profile_path or get_shell_profile_path()
    profile = profile_path.read_text()

    for a_file in sources[system.lower()]['files']:
        file = a_file.replace("REPO_ROOT", REPO_ROOT.as_posix()).replace("LIBRARY_ROOT", LIBRARY_ROOT.as_posix())
        file = tb.P(file).collapseuser().as_posix()  # this makes the shell profile interuseable across machines.
        if file in profile:
            if system == "Windows": profile += f"\n. {file}"
            elif system == "Linux": profile += f"\nsource {file}"
            else: raise ValueError(f"Not implemented for this system {system}")
        else: print(f"SKIPPING source `{file}`, it is already sourced in shell profile.")
    profile_path.write_text(profile)


def main_add_patches_to_shell_profile(profile_path=None):
    patches = LIBRARY_ROOT.joinpath(f"profile/patches/{system.lower()}").search()

    choice = display_options(msg="Which patch to add?", options=patches.list + ["all"], default="all")
    if str(choice) == "all": patches = patches
    else: patches = [choice]

    profile_path = profile_path or get_shell_profile_path()
    profile = profile_path.read_text()

    for patch_path in patches:
        patch = patch_path.read_text()
        if patch in profile: print(f"Skipping `{patch_path.name}`; patch already in profile")
        else: profile += "\n" + patch
    profile_path.write_text(profile)


def main():
    print("\n")
    print(f"CREATING SYMLINKS".center(80, "-"))
    main_symlinks()
    print("\n")
    print(f"ADDING ENV PATH".center(80, "-"))
    main_env_path()
    print("\n")
    print(f"ADDING SOURCES TO SHELL PROFILE".center(80, "-"))
    main_add_sources_to_shell_profile()
    print("\n")
    print(f"ADDING PATCHES TO SHELL PROFILE".center(80, "-"))
    main_add_patches_to_shell_profile()


if __name__ == '__main__':
    pass
