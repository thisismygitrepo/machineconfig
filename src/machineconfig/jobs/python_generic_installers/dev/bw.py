
import crocodile.toolbox as tb
from machineconfig.utils.installer import find_move_delete_linux
from rich.console import Console
from platform import system
from typing import Optional


__doc__ = """Bitwarden (password manager) cli"""
repo_url = "https://github.com/bitwarden/clients"


def main(version: Optional[str] = None):
    _ = version
    if system() == "Windows":
        console = Console()
        console.rule("Installing bitwarden")
        url = r'https://vault.bitwarden.com/download/?app=cli&platform=windows'
        dir_ = tb.P(url).download(name="file.zip").unzip(inplace=True)
        # if isinstance(dir_, tb.P):
        tmp = list(dir_.search(f"bw.exe", r=True))
        tmp[0].move(folder=tb.P.get_env().WindowsApps, overwrite=True)
        dir_.delete(sure=True)
        console.rule("Completed Installation")
    else:
        url = r'https://vault.bitwarden.com/download/?app=cli&platform=linux'
        dir_ = tb.P(url).download(name="file.zip").unzip(inplace=True)
        find_move_delete_linux(dir_, "bw", delete=True)


if __name__ == '__main__':
    main()
