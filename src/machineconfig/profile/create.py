
"""
This script Takes away all config files from the computer, place them in one directory
`dotfiles`, and create symlinks to those files from thier original locations.
"""

import crocodile.toolbox as tb
from crocodile.environment import DotFiles, system, PathVar, UserName  # ProgramFiles, WindowsApps  # , exe
from machineconfig.utils.utils import symlink
# import os
import subprocess


ERROR_LIST = []  # append to this after every exception captured.
REPO_ROOT = tb.P.home().joinpath(f"code/machineconfig/src/machineconfig")
CONFIG_ROOT = tb.P.home().joinpath("code/machineconfig/settings")


# =================== SYMLINKS ====================================

def link_ssh(overwrite=True):
    """The function can link aribtrary number of files without linking the directory itself (which is not doable in toml config file)"""
    path = tb.P.home().joinpath(".ssh")
    target = DotFiles.joinpath(".ssh")
    for item in target.search("*"):
        if "authorized_keys" in item: continue
        symlink(path.joinpath(item.name), item, overwrite=overwrite)
    if system == "Linux":  # permissions of ~/dotfiles/.ssh should be adjusted
        try:
            subprocess.run("chmod 700 ~/dotfiles/.ssh")  # may require sudo
            subprocess.run("chmod 600 ~/dotfiles/.ssh/*")
        except Exception as e:
            ERROR_LIST.append(e)
            print("Caught error", e)


def link_aws(overwrite=True):
    path = tb.P.home().joinpath(".aws")
    target = DotFiles.joinpath("aws/.aws")
    for item in target.search("*"): symlink(path.joinpath(item.name), item, overwrite=overwrite)


def add_to_shell_profile_path(dirs: list):
    addition = PathVar.append_temporarily(dirs=dirs)
    if system == "Windows": tb.Terminal().run("$profile", shell="pwsh").as_path.modify_text(addition, addition, newline=False, notfound_append=True)
    elif system == "Linux": tb.P("~/.bashrc").expanduser().modify_text(addition, addition, notfound_append=True)
    else: raise ValueError


def main_symlinks():
    symlink_mapper = tb.P("~/code/machineconfig/src/machineconfig/symlinks/mapper.toml").readit()
    symlink_mapper['wsl_windows']['home']["to_this"] = symlink_mapper['wsl_windows']['home']["to_this"].replace("username", UserName)
    symlink_mapper['wsl_linux']['home']["to_this"] = symlink_mapper['wsl_linux']['home']["to_this"].replace("username", UserName)

    overwrite = True
    exclude = ["startup_windows", "wsl_linux", "wsl_windows"]
    for program_key in symlink_mapper.keys():
        if program_key in exclude or f"{system.lower()}" not in program_key: continue
        for file_key, file_map in symlink_mapper[program_key].items():
            try: symlink(this=file_map['this'], to_this=file_map['to_this'], overwrite=overwrite)
            except KeyError: print("Config error: ", program_key, file_key, "missing keys 'this ==> to_this'.")

    link_aws(overwrite=overwrite)
    link_ssh(overwrite=overwrite)
    if system == "Linux": tb.Terminal().run(f'chmod +x {REPO_ROOT.joinpath(f"scripts/{system.lower()}")} -R')


def main_env_path():
    env_path = tb.P("~/code/machineconfig/src/machineconfig/symlinks/env_path.toml").readit()
    # The following is not a symlink creation, but modification of shell profile by additing dirs to PATH
    # Shell profile is either in dotfiles and is synced (as in Windows), hence no need for update, or is updated on the fly (for Linux)
    # for windows it won't change the profile, if the profile was modified already e.g. due to syncing
    add_to_shell_profile_path(env_path[f'path_{system.lower()}']['extension'])


def main():
    main_symlinks()
    main_env_path()


if __name__ == '__main__':
    pass