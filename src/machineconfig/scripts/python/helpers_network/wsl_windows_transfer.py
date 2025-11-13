"""TWSL"""

from machineconfig.utils.path_extended import PathExtended
from typing import Annotated, Optional
import typer
import platform
import getpass
from pathlib import Path

system = platform.system()  # e.g. "Windows", "Linux", "Darwin" (macOS)
# HostName          = platform.node()  # e.g. "MY-SURFACE", os.env["COMPUTERNAME") only works for windows.
UserName = getpass.getuser()  # e.g: username, os.env["USERNAME") only works for windows.
# UserDomain        = os.environ["USERDOMAIN"]  # e.g. HAD OR MY-SURFACE
# UserDomainRoaming = PathExtended(os.environ["USERDOMAIN_ROAMINGPROFILE"])  # e.g. SURFACE
# LogonServer       = os.environ["LOGONSERVER"]  # e.g. "\\MY-SURFACE"
# UserProfile       = PathExtended(os.env["USERPROFILE"))  # e.g C:\Users\username
# HomePath          = PathExtended(os.env["HOMEPATH"))  # e.g. C:\Users\username
# Public            = PathExtended(os.environ["PUBLIC"])  # C:\Users\Public

WSL_FROM_WIN = Path(r"\\wsl.localhost\Ubuntu-22.04\home")  # PathExtended(rf"\\wsl$\Ubuntu\home")  # see localappdata/canonical
WIN_FROM_WSL = Path(r"/mnt/c/Users")


def main(
    path: Annotated[str, typer.Argument(help="📁 Path of file/folder to transfer over.")],
    same_file_system: Annotated[bool, typer.Option("--same_file_system", "-s", help="⚠️ Move file across the same file system (not recommended).")] = False,
    destination: Annotated[str, typer.Option("--destination", "-d", help="📍 New path.")] = "",
    pwd: Annotated[Optional[str], typer.Option("--pwd", "-P", help="🔑 Password for encryption.")] = None,
    sshkey: Annotated[Optional[str], typer.Option("--sshkey", "-i", help="🔐 Path to SSH private key.")] = None,
    port: Annotated[Optional[str], typer.Option("--port", "-p", help="🔌 Port number.")] = None,
    zip_first: Annotated[bool, typer.Option("--zip_first", "-z", help="📦 Zip before transferring.")] = False,
) -> None:
    print("\n" + "=" * 50)
    print("🔄 Welcome to the WSL-Windows File Transfer Tool")
    print("=" * 50 + "\n")

    path_obj = PathExtended(path).expanduser().absolute()
    relative_home = PathExtended(path_obj.expanduser().absolute().relative_to(Path.home()))

    if same_file_system:
        print("⚠️ Using a not recommended transfer method! Copying files across the same file system.")
        if system == "Windows":  # move files over to WSL
            print("📤 Transferring files from Windows to WSL...")
            path_obj.copy(folder=WSL_FROM_WIN.joinpath(UserName).joinpath(relative_home.parent), overwrite=True)  # the following works for files and folders alike.
        else:  # move files from WSL to win
            print("📤 Transferring files from WSL to Windows...")
            path_obj.copy(folder=WIN_FROM_WSL.joinpath(UserName).joinpath(relative_home.parent), overwrite=True)
        print("✅ Transfer completed successfully!\n")
    else:
        from machineconfig.utils.ssh import SSH
        import platform

        port_int = int(port) if port else (2222 if system == "Windows" else 22)
        username = UserName
        hostname = platform.node()
        ssh = SSH(host=None, username=username, hostname=hostname, ssh_key_path=sshkey, password=pwd, port=port_int, enable_compression=False)
        print("🌐 Initiating SSH transfer...")
        ssh.copy_from_here(source_path=str(path_obj), target_rel2home=destination, compress_with_zip=zip_first, recursive=False, overwrite_existing=False)
        print("✅ SSH transfer completed successfully!\n")


def arg_parser() -> None:
    typer.run(main)


if __name__ == "__main__":
    arg_parser()
