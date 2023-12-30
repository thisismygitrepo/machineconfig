

import crocodile.toolbox as tb
from rich.console import Console
from platform import system
from machineconfig.utils.installer import get_latest_release
from typing import Optional


__doc__ = """broot is an fzf variant for folder structure and layered search."""


if system() == 'Linux':
    repo_url = r'https://dystroy.org/broot/download/x86_64-linux/broot'
elif system() == 'Windows':
    repo_url = r'https://dystroy.org/broot/download/x86_64-pc-windows-gnu/broot.exe'
else:
    raise NotImplementedError(f"Unsupported OS: {system()}")


def main(version: Optional[str] = None) -> None:
    print("\n\n\n")
    console = Console()
    console.rule("Installing Broot")
    _ = get_latest_release("https://github.com/Canop/broot", exe_name="broot", version=version)

    if system() == "Windows":
        p = tb.P(repo_url).download()
        p.move(folder=tb.P.get_env().WindowsApps, overwrite=True)
    else:
        p = tb.P(repo_url).download()
        p.chmod(0o777)  # p.move(folder=r'/usr/local/bin/', overwrite=True) Permission Error
        tb.Terminal().run(f"sudo mv {p} /usr/local/bin/").print_if_unsuccessful(desc="MOVING executable to /usr/local/bin", strict_err=True, strict_returncode=True)

    console.rule("Completed Installation")


if __name__ == '__main__':
    main()
