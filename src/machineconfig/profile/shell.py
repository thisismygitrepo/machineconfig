"""shell
"""

from crocodile.environment import PathVar
from machineconfig.utils.utils2 import randstr
from crocodile.file_management import P
from crocodile.meta import Terminal
from machineconfig.utils.utils import LIBRARY_ROOT, REPO_ROOT, display_options
import platform
from typing import Optional
from rich.console import Console
from rich.panel import Panel


system = platform.system()

console = Console()
BOX_WIDTH = 100  # Define BOX_WIDTH or get it from a config

# --------------------------------------- SHELL PROFILE --------------------------------------------------------
# modification of shell profile by additing dirs to PATH
# Shell profile is either in dotfiles and is synced (as in Windows), hence no need for update, or is updated on the fly (for Linux)
# for windows it won't change the profile, if the profile was modified already e.g. due to syncing


def create_default_shell_profile():
    profile_path = get_shell_profile_path()
    profile = profile_path.read_text()
    if system == "Windows": source = f". {LIBRARY_ROOT.joinpath('settings/shells/pwsh/init.ps1').collapseuser().to_str().replace('~', '$HOME')}"
    else: source = f"source {LIBRARY_ROOT.joinpath('settings/shells/bash/init.sh').collapseuser().to_str().replace('~', '$HOME')}"

    if source in profile: 
        console.print(Panel("🔄 PROFILE | Skipping init script sourcing - already present in profile", title="[bold blue]Profile[/bold blue]", border_style="blue"))
    else:
        console.print(Panel("📝 PROFILE | Adding init script sourcing to profile", title="[bold blue]Profile[/bold blue]", border_style="blue"))
        profile += "\n" + source + "\n"
        if system == "Linux":
            res = Terminal().run("cat /proc/version").op
            if "microsoft" in res.lower() or "wsl" in res.lower():
                profile += "\ncd ~"  # this is to make sure that the current dir is not in the windows file system, which is terribly slow and its a bad idea to be there anyway.
                console.print("📌 WSL detected - adding 'cd ~' to profile to avoid Windows filesystem")
        profile_path.create(parents_only=True).write_text(profile)
        console.print(Panel("✅ Profile updated successfully", title="[bold blue]Profile[/bold blue]", border_style="blue"))


def get_shell_profile_path():
    if system == "Windows":
        obj = Terminal().run("$PROFILE", shell="pwsh")
        res = obj.op2path()
        if isinstance(res, P): profile_path = res
        else:
            obj.print(capture=False)
            raise ValueError(f"Could not get profile path for Windows. Got {res}")
    elif system == "Linux": profile_path = P("~/.bashrc").expanduser()
    else: raise ValueError(f"Not implemented for this system {system}")
    console.print(Panel(f"🐚 SHELL PROFILE | Working with path: `{profile_path}`", title="[bold blue]Shell Profile[/bold blue]", border_style="blue"))
    return profile_path


def main_env_path(choice: Optional[str] = None, profile_path: Optional[str] = None):
    env_path = LIBRARY_ROOT.joinpath("profile/env_path.toml").readit()
    dirs = env_path[f'path_{system.lower()}']['extension']

    console.print(Panel("🔍 ENVIRONMENT | Current PATH variables:", title="[bold blue]Environment[/bold blue]", border_style="blue"))

    if choice is None:
        tmp = display_options(msg="Which directory to add?", options=dirs + ["all", "none(EXIT)"], default="none(EXIT)")
        assert isinstance(tmp, str), f"Choice must be a string or a list of strings, not {type(choice)}"
        choice = tmp
        if str(choice) != "all": dirs = [choice]
    if choice == "none(EXIT)": return

    console.print(f"\n📌 Adding directories to PATH: {dirs}")
    addition = PathVar.append_temporarily(dirs=dirs)
    profile_path_obj = P(profile_path) if isinstance(profile_path, str) else get_shell_profile_path()
    profile_path_obj.copy(name=profile_path_obj.name + ".orig_" + randstr())
    console.print(f"💾 Created backup of profile: {profile_path_obj.name}.orig_*")
    profile_path_obj.modify_text(addition, addition, replace_line=False, notfound_append=True)
    console.print(Panel("✅ PATH variables added to profile successfully", title="[bold blue]Environment[/bold blue]", border_style="blue"))


def main_add_sources_to_shell_profile(profile_path: Optional[str] = None, choice: Optional[str] = None):
    sources: list[str] = LIBRARY_ROOT.joinpath("profile/sources.toml").readit()[system.lower()]['files']

    console.print(Panel("🔄 Adding sources to shell profile", title="[bold blue]Sources[/bold blue]", border_style="blue"))

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
            if system == "Windows": 
                profile += f"\n. {file}"
                console.print(f"➕ Added PowerShell source: {file}")
            elif system == "Linux": 
                profile += f"\nsource {file}"
                console.print(f"➕ Added Bash source: {file}")
            else: raise ValueError(f"Not implemented for this system {system}")
        else: 
            console.print(f"⏭️  Source already present: {file}")
    
    profile_path_obj.write_text(profile)
    console.print(Panel("✅ Shell profile updated with sources", title="[bold blue]Sources[/bold blue]", border_style="blue"))


def main_add_patches_to_shell_profile(profile_path: Optional[str] = None, choice: Optional[str] = None):
    patches: list[str] = list(LIBRARY_ROOT.joinpath(f"profile/patches/{system.lower()}").search().apply(lambda x: x.as_posix()))
    
    console.print(Panel("🩹 Adding patches to shell profile", title="[bold blue]Patches[/bold blue]", border_style="blue"))
    
    if choice is None:
        choice_chosen = display_options(msg="Which patch to add?", options=list(patches) + ["all", "none(EXIT)"], default="none(EXIT)", multi=False)
        assert isinstance(choice_chosen, str), f"Choice must be a string or a list of strings, not {type(choice)}"
        choice = choice_chosen
    if choice == "none(EXIT)": return None
    elif str(choice) == "all": 
        console.print("📌 Adding all patches to profile")
    else: 
        patches = [choice]
        console.print(f"📌 Adding selected patch: {choice}")

    profile_path_obj = P(profile_path) if isinstance(profile_path, str) else get_shell_profile_path()
    profile = profile_path_obj.read_text()

    for patch_path in patches:
        patch_path_obj = P(patch_path)
        patch = patch_path_obj.read_text()
        if patch in profile: 
            console.print(f"⏭️  Patch already present: {patch_path_obj.name}")
        else: 
            profile += "\n" + patch
            console.print(f"➕ Added patch: {patch_path_obj.name}")

    if system == "Linux":
        res = Terminal().run("cat /proc/version").op
        if "microsoft" in res.lower() or "wsl" in res.lower():
            profile += "\ncd ~"  # this is to make sure that the current dir is not in the windows file system, which is terribly slow and its a bad idea to be there anyway.
            console.print("📌 WSL detected - adding 'cd ~' to profile to avoid Windows filesystem")

    profile_path_obj.write_text(profile)
    console.print(Panel("✅ Shell profile updated with patches", title="[bold blue]Patches[/bold blue]", border_style="blue"))


if __name__ == '__main__':
    pass
