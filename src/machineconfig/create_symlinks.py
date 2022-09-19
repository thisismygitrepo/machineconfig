
"""
This script Takes away all config files from the computer, place them in one directory
`dotfiles`, and create symlinks to those files from thier original locations.
"""

import crocodile.toolbox as tb
from crocodile.environment import DotFiles, get_shell_profiles, system, LocalAppData, AppData, PathVar  # ProgramFiles, WindowsApps  # , exe
from machineconfig.utils.utils import symlink


repo_root = tb.P.home().joinpath(f"code/machineconfig/src/machineconfig")
M_CONFIG = tb.P.home().joinpath("code/machineconfig/settings")


def link_ssh(overwrite=True):
    path = tb.P.home().joinpath(".ssh")
    target = DotFiles.joinpath(".ssh")
    for item in target.search("*"):
        if "authorized_keys" in item: continue
        symlink(path.joinpath(item.name), item, overwrite=overwrite)


def link_aws(overwrite=True):
    path = tb.P.home().joinpath(".aws")
    target = DotFiles.joinpath("aws/.aws")
    for item in target.search("*"): symlink(path.joinpath(item.name), item, overwrite=overwrite)


def link_gitconfig(overwrite=True):
    for config in [".gitconfig", ".git-credentials"]: symlink(tb.P.home().joinpath(config), DotFiles.joinpath(f"settings/{config}"), overwrite=overwrite)


def link_pypi_creds(overwrite=True):
    symlink(tb.P.home().joinpath(".pypirc"), DotFiles.joinpath("creds/.pypirc"), overwrite=overwrite)


def link_powershell(overwrite=True):
    if system == "Linux":
        symlink(this=tb.P.home().joinpath(".inputrc"), to_this=DotFiles.joinpath("shells/bash/.inputrc"), overwrite=overwrite)
    elif system == "Windows":
        for profile_name, profile_path in get_shell_profiles(shell="pwsh").items():
            target = DotFiles.joinpath(f"shells/powershell/{profile_name}/{profile_path.name}")
            symlink(profile_path, target, overwrite=overwrite)


def link_windows_powershell(overwrite=True):
    if system == "Linux": return None
    for profile_name, profile_path in get_shell_profiles(shell="powershell").items():
        target = DotFiles.joinpath(f"shells/windows_powershell/{profile_name}/{profile_path.name}")
        symlink(profile_path, target, overwrite=overwrite)


def link_ipython(overwrite=True):
    path = tb.P.home().joinpath(".ipython/profile_default/ipython_config.py")
    target = DotFiles.joinpath(f"shells/ipython/{path.name}")
    symlink(path, target, overwrite=overwrite)


def link_autostart(overwrite=True):
    file = AppData.joinpath("Microsoft/Windows/Start Menu/Programs/Startup").joinpath("startup_file.cmd")
    symlink(file, repo_root.joinpath(f"jobs/windows/startup_file.cmd").expanduser(), overwrite=overwrite)


def link_scripts(overwrite=True):
    symlink(tb.P.home().joinpath("scripts"), repo_root.joinpath(f"scripts/{system.lower()}"), overwrite=overwrite)
    if system == "Linux": tb.Terminal().run(f'chmod +x {repo_root.joinpath(f"scripts/{system.lower()}")} -R')


def add_to_shell_profile_path(dirs: list):
    # options to make croshell available: define in terminal profile, add to Path, or add to some folder that is already in path, e.g. env.WindowsApps or Scripts folder where python.exe resides.
    # repo_root.joinpath(f"scripts/{system.lower()}/croshell.ps1").symlink_from(folder=exe.parent)  # thus, whenever ve is activated, croshell is available.
    addition = PathVar.append_temporarily(dirs=dirs)
    if system == "Windows": tb.Terminal().run("$profile", shell="pwsh").as_path.modify_text(addition, addition, newline=False, notfound_append=True)
    elif system == "Linux": tb.P("~/.bashrc").expanduser().modify_text(addition, addition, notfound_append=True)
    else: raise ValueError


def link_lf_n_lvim(overwrite=True):
    if system == "Windows":
        for item in ['lfrc', 'icons', 'colors']:
            symlink(this=LocalAppData.joinpath(f"lf/{item}"), to_this=M_CONFIG.joinpath(f"lf/{item}"), overwrite=overwrite)
        # symlink(this=LocalAppData.joinpath(f"nvim/init.vim"), to_this=M_CONFIG.joinpath(f"nvim/init.vim"), overwrite=overwrite)
    else:
        for item in ['lfrc', 'icons', 'colors']:
            symlink(this=tb.P.home().joinpath(f".config/lf/{item}"), to_this=M_CONFIG.joinpath(f"lf_linux/{item}"), overwrite=overwrite)
        # symlink(this=tb.P.home().joinpath(f".config/nvim/init.vim"), to_this=M_CONFIG.joinpath(f"nvim/init.vim"), overwrite=overwrite)


def link_wsl_path_to_windows_path(linux_user, windows_user=None, links=None, run_in_wsl=True):
    links = links or ["data", "dotfiles"]
    windows_user = windows_user or linux_user
    wsl_home = tb.P(fr"\\wsl$\Ubuntu\home\{linux_user}")  # used to reach wsl home from windows shell
    win_home = tb.P(f"/mnt/c/Users/{windows_user}")  # used to read windows home from wsl shell.
    for link in links:
        if run_in_wsl: symlink(this=tb.P.home().joinpath(link), to_this=win_home.joinpath(link))
        else: symlink(this=wsl_home.joinpath(f"{link}"), to_this=tb.P.home().joinpath(link))


def main():
    """create symlinks in default locations to `dotfiles` contents"""
    overwrite = True
    link_gitconfig(overwrite=overwrite)
    link_pypi_creds(overwrite=overwrite)
    link_ipython(overwrite=overwrite)
    link_powershell(overwrite=overwrite)
    link_windows_powershell(overwrite=overwrite)
    link_aws(overwrite=overwrite)
    link_ssh(overwrite=overwrite)
    link_lf_n_lvim(overwrite=overwrite)
    # link_autostart(overwrite=overwrite)
    link_scripts(overwrite=overwrite)

    # The following is not a symlink creation, but modification of shell profile by additing dirs to PATH
    # Shell profile is either in dotfiles and is synced (as in Windows), hence no need for update, or is updated on the fly (for Linux)
    paths = [repo_root.joinpath(f"scripts/{system.lower()}").collapseuser()] + ([r"C:\Program Files (x86)\GnuWin32\bin", r"C:\Program Files\CodeBlocks\MinGW\bin"] if system == "Windows" else [])  # make and gcc are already available on linux
    add_to_shell_profile_path(paths)  # for windows it won't change the profile, if the profile was modified already e.g. due to syncing.
    # this is ambiguous, with which shell is this happening?


if __name__ == '__main__':
    pass
