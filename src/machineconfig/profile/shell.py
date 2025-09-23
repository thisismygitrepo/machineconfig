"""shell"""

from machineconfig.utils.path_reduced import PathExtended as PathExtended
from machineconfig.utils.source_of_truth import LIBRARY_ROOT

import platform
import os
import subprocess
from rich.console import Console
from rich.panel import Panel


system = platform.system()
sep = ";" if system == "Windows" else ":"  # PATH separator, this is special for PATH object, not to be confused with PathExtended.sep (normal paths), usually / or \
PATH = os.environ["PATH"].split(sep)  # this is a list of paths in PATH variable, not a crocodile.file_management.P object.
console = Console()
BOX_WIDTH = 100  # Define BOX_WIDTH or get it from a config


def get_shell_profile_path() -> PathExtended:
    if system == "Windows":
        result = subprocess.run(["pwsh", "-Command", "$PROFILE"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        if result.returncode == 0 and result.stdout.strip():
            profile_path = PathExtended(result.stdout.strip())
        else:
            print(f"Command failed with return code {result.returncode}")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            raise ValueError(f"""Could not get profile path for Windows. Got stdout: {result.stdout}, stderr: {result.stderr}""")
    elif system == "Linux":
        profile_path = PathExtended("~/.bashrc").expanduser()
    else:
        raise ValueError(f"""Not implemented for this system {system}""")
    console.print(Panel(f"""🐚 SHELL PROFILE | Working with path: `{profile_path}`""", title="[bold blue]Shell Profile[/bold blue]", border_style="blue"))
    return profile_path


def create_default_shell_profile() -> None:
    shell_profile_path = get_shell_profile_path()
    shell_profile = shell_profile_path.read_text(encoding="utf-8")
    if system == "Windows":
        source = f""". {str(PathExtended(LIBRARY_ROOT).joinpath("settings/shells/pwsh/init.ps1").collapseuser()).replace("~", "$HOME")}"""
    else:
        source = f"""source {str(PathExtended(LIBRARY_ROOT).joinpath("settings/shells/bash/init.sh").collapseuser()).replace("~", "$HOME")}"""
    if source in shell_profile:
        console.print(Panel("🔄 PROFILE | Skipping init script sourcing - already present in profile", title="[bold blue]Profile[/bold blue]", border_style="blue"))
    else:
        console.print(Panel("📝 PROFILE | Adding init script sourcing to profile", title="[bold blue]Profile[/bold blue]", border_style="blue"))
        shell_profile += "\n" + source + "\n"
        if system == "Linux":
            result = subprocess.run(["cat", "/proc/version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            if result.returncode == 0 and result.stdout:
                version_info = result.stdout.lower()
                if "microsoft" in version_info or "wsl" in version_info:
                    shell_profile += "\ncd ~"
                    console.print("📌 WSL detected - adding 'cd ~' to profile to avoid Windows filesystem")
        shell_profile_path.parent.mkdir(parents=True, exist_ok=True)
        shell_profile_path.write_text(shell_profile, encoding="utf-8")
        console.print(Panel("✅ Profile updated successfully", title="[bold blue]Profile[/bold blue]", border_style="blue"))


# def append_temporarily(dirs: list[str], kind: Literal["append", "prefix", "replace"]) -> str:
#     dirs_ = []
#     for path in dirs:
#         path_rel = PathExtended(path).collapseuser(strict=False)
#         if path_rel.as_posix() in PATH or str(path_rel) in PATH or str(path_rel.expanduser()) in PATH or path_rel.expanduser().as_posix() in PATH:
#             print(f"Path passed `{path}` is already in PATH, skipping the appending.")
#         else:
#             dirs_.append(path_rel.as_posix() if system == "Linux" else str(path_rel))
#     dirs = dirs_
#     if len(dirs) == 0:
#         return ""

#     if system == "Windows":
#         """Source: https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_environment_variables?view=powershell-7.2"""
#         if kind == "append":
#             command = rf'$env:Path += ";{sep.join(dirs)}"'  # Append to the Path variable in the current window:
#         elif kind == "prefix":
#             command = rf'$env:Path = "{sep.join(dirs)};" + $env:Path'  # Prefix the Path variable in the current window:
#         elif kind == "replace":
#             command = rf'$env:Path = "{sep.join(dirs)}"'  # Replace the Path variable in the current window (use with caution!):
#         else:
#             raise KeyError
#         return command  # if run is False else tm.run(command, shell="powershell")
#     elif system in ["Linux", "Darwin"]:
#         result = f'export PATH="{sep.join(dirs)}:$PATH"'
#     else:
#         raise ValueError
#     return result


# def main_add_sources_to_shell_profile(profile_path: Optional[str], choice: Optional[str]) -> None:
#     sources: list[str] = read_toml(LIBRARY_ROOT.joinpath("profile/sources.toml"))[system.lower()]["files"]
#     console.print(Panel("🔄 Adding sources to shell profile", title="[bold blue]Sources[/bold blue]", border_style="blue"))

#     if choice is None:
#         choice_obj = display_options(msg="Which patch to add?", options=sources + ["all", "none(EXIT)"], default="none(EXIT)", multi=True)
#         if isinstance(choice_obj, str):
#             if choice_obj == "all":
#                 choice = choice_obj
#             elif choice_obj == "none(EXIT)":
#                 return
#             else:
#                 sources = [choice_obj]
#         else:  # isinstance(choice_obj, list):
#             sources = choice_obj
#     elif choice == "none(EXIT)":
#         return

#     if isinstance(profile_path, str):
#         profile_path_obj = PathExtended(profile_path)
#     else:
#         profile_path_obj = get_shell_profile_path()
#     profile = profile_path_obj.read_text(encoding="utf-8")

#     for a_file in sources:
#         tmp = a_file.replace("REPO_ROOT", REPO_ROOT.as_posix()).replace("LIBRARY_ROOT", LIBRARY_ROOT.as_posix())
#         file = PathExtended(tmp).collapseuser()  # this makes the shell profile interuseable across machines.
#         file = file.as_posix() if system == "Linux" else str(file)
#         if file not in profile:
#             if system == "Windows":
#                 profile += f"\n. {file}"
#                 console.print(f"➕ Added PowerShell source: {file}")
#             elif system == "Linux":
#                 profile += f"\nsource {file}"
#                 console.print(f"➕ Added Bash source: {file}")
#             else:
#                 raise ValueError(f"Not implemented for this system {system}")
#         else:
#             console.print(f"⏭️  Source already present: {file}")

#     profile_path_obj.write_text(profile, encoding="utf-8")
#     console.print(Panel("✅ Shell profile updated with sources", title="[bold blue]Sources[/bold blue]", border_style="blue"))


# def main_add_patches_to_shell_profile(profile_path: Optional[str], choice: Optional[str]) -> None:
#     patches: list[str] = [item.as_posix() for item in PathExtended(LIBRARY_ROOT).joinpath(f"profile/patches/{system.lower()}").search()]

#     console.print(Panel("🩹 Adding patches to shell profile", title="[bold blue]Patches[/bold blue]", border_style="blue"))

#     if choice is None:
#         choice_chosen = display_options(msg="Which patch to add?", options=list(patches) + ["all", "none(EXIT)"], default="none(EXIT)", multi=False)
#         assert isinstance(choice_chosen, str), f"Choice must be a string or a list of strings, not {type(choice)}"
#         choice = choice_chosen
#     if choice == "none(EXIT)":
#         return None
#     elif str(choice) == "all":
#         console.print("📌 Adding all patches to profile")
#     else:
#         patches = [choice]
#         console.print(f"📌 Adding selected patch: {choice}")

#     profile_path_obj = PathExtended(profile_path) if isinstance(profile_path, str) else get_shell_profile_path()
#     profile = profile_path_obj.read_text(encoding="utf-8")

#     for patch_path in patches:
#         patch_path_obj = PathExtended(patch_path)
#         patch = patch_path_obj.read_text(encoding="utf-8")
#         if patch in profile:
#             console.print(f"⏭️  Patch already present: {patch_path_obj.name}")
#         else:
#             profile += "\n" + patch
#             console.print(f"➕ Added patch: {patch_path_obj.name}")

#     if system == "Linux":
#         res = Terminal().run("cat /proc/version").op
#         if "microsoft" in res.lower() or "wsl" in res.lower():
#             profile += "\ncd ~"  # this is to make sure that the current dir is not in the windows file system, which is terribly slow and its a bad idea to be there anyway.
#             console.print("📌 WSL detected - adding 'cd ~' to profile to avoid Windows filesystem")

#     profile_path_obj.write_text(profile, encoding="utf-8")
#     console.print(Panel("✅ Shell profile updated with patches", title="[bold blue]Patches[/bold blue]", border_style="blue"))


if __name__ == "__main__":
    pass
