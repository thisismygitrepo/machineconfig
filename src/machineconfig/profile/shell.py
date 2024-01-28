
"""shell
"""

from crocodile.environment import PathVar
from crocodile.core import randstr
from crocodile.file_management import P
from crocodile.meta import Terminal
from machineconfig.utils.utils import LIBRARY_ROOT, REPO_ROOT, display_options
import platform
from typing import Optional


system = platform.system()

# --------------------------------------- SHELL PROFILE --------------------------------------------------------
# modification of shell profile by additing dirs to PATH
# Shell profile is either in dotfiles and is synced (as in Windows), hence no need for update, or is updated on the fly (for Linux)
# for windows it won't change the profile, if the profile was modified already e.g. due to syncing


def create_default_shell_profile():
    profile_path = get_shell_profile_path()
    profile = profile_path.read_text()
    if system == "Windows": source = f". {LIBRARY_ROOT.joinpath('settings/shells/pwsh/init.ps1').collapseuser().str.replace('~', '$HOME')}"
    else: source = f"source {LIBRARY_ROOT.joinpath('settings/shells/bash/init.sh').collapseuser().str.replace('~', '$HOME')}"

    if source in profile: print(f"Skipping sourcing init script; already in profile")
    else:
        profile += "\n" + source + "\n"
        if system == "Linux":
            res = Terminal().run("cat /proc/version").op
            if "microsoft" in res.lower() or "wsl" in res.lower():
                profile += "\ncd ~"  # this is to make sure that the current dir is not in the windows file system, which is terribly slow and its a bad idea to be there anyway.
        profile_path.create(parents_only=True).write_text(profile)


def get_shell_profile_path():
    if system == "Windows":
        res = Terminal().run("$profile", shell="pwsh").op2path()
        if isinstance(res, P): profile_path = res
        else: raise ValueError(f"Could not get profile path for Windows. Got {res}")
    elif system == "Linux": profile_path = P("~/.bashrc").expanduser()
    else: raise ValueError(f"Not implemented for this system {system}")
    print(f"Working on shell profile `{profile_path}`")
    return profile_path


def main_env_path(choice: Optional[str] = None, profile_path: Optional[str] = None):
    env_path = LIBRARY_ROOT.joinpath("profile/env_path.toml").readit()
    dirs = env_path[f'path_{system.lower()}']['extension']

    print(f"Current PATH: ", "\n============")
    P.get_env().PATH.print()

    if choice is None:
        tmp = display_options(msg="Which directory to add?", options=dirs + ["all", "none(EXIT)"], default="none(EXIT)")
        assert isinstance(tmp, str), f"Choice must be a string or a list of strings, not {type(choice)}"
        choice = tmp
        if str(choice) != "all": dirs = [choice]
    if choice == "none(EXIT)": return

    addition = PathVar.append_temporarily(dirs=dirs)
    profile_path_obj = P(profile_path) if isinstance(profile_path, str) else get_shell_profile_path()
    profile_path_obj.copy(name=profile_path_obj.name + f".orig_" + randstr())
    profile_path_obj.modify_text(addition, addition, replace_line=False, notfound_append=True)


def main_add_sources_to_shell_profile(profile_path: Optional[str] = None, choice: Optional[str] = None):
    sources: list[str] = LIBRARY_ROOT.joinpath("profile/sources.toml").readit()[system.lower()]['files']

    if choice is None:
        choice_obj = display_options(msg="Which patch to add?", options=sources + ["all", "none(EXIT)"], default="none(EXIT)", multi=True)
        if isinstance(choice_obj, str):
            if choice_obj == "all": choice = choice_obj
            elif choice_obj == "none(EXIT)": return
            else: sources = [choice_obj]
        else:  # isinstance(choice_obj, list):
            sources = choice_obj
    elif choice == "none(EXIT)": return

    if isinstance(profile_path, str):
        profile_path_obj = P(profile_path)
    else: profile_path_obj = get_shell_profile_path()
    profile = profile_path_obj.read_text()

    for a_file in sources:
        tmp = a_file.replace("REPO_ROOT", REPO_ROOT.as_posix()).replace("LIBRARY_ROOT", LIBRARY_ROOT.as_posix())
        file = P(tmp).collapseuser()  # this makes the shell profile interuseable across machines.
        file = file.as_posix() if system == "Linux" else str(file)
        if file not in profile:
            if system == "Windows": profile += f"\n. {file}"
            elif system == "Linux": profile += f"\nsource {file}"
            else: raise ValueError(f"Not implemented for this system {system}")
        else: print(f"SKIPPED source `{file}`, it is already sourced in shell profile.")
    profile_path_obj.write_text(profile)


def main_add_patches_to_shell_profile(profile_path: Optional[str] = None, choice: Optional[str] = None):
    patches: list[str] = list(LIBRARY_ROOT.joinpath(f"profile/patches/{system.lower()}").search().apply(lambda x: x.as_posix()))
    if choice is None:
        choice_chosen = display_options(msg="Which patch to add?", options=list(patches) + ["all", "none(EXIT)"], default="none(EXIT)", multi=False)
        assert isinstance(choice_chosen, str), f"Choice must be a string or a list of strings, not {type(choice)}"
        choice = choice_chosen
    if choice == "none(EXIT)": return None
    elif str(choice) == "all": pass  # i.e. patches = patches
    else: patches = [choice]

    profile_path_obj = P(profile_path) if isinstance(profile_path, str) else get_shell_profile_path()
    profile = profile_path_obj.read_text()

    for patch_path in patches:
        patch_path_obj = P(patch_path)
        patch = patch_path_obj.read_text()
        if patch in profile: print(f"Skipping `{patch_path_obj.name}`; patch already in profile")
        else: profile += "\n" + patch

    if system == "Linux":
        res = Terminal().run("cat /proc/version").op
        if "microsoft" in res.lower() or "wsl" in res.lower():
            profile += "\ncd ~"  # this is to make sure that the current dir is not in the windows file system, which is terribly slow and its a bad idea to be there anyway.

    profile_path_obj.write_text(profile)


if __name__ == '__main__':
    pass
