
import crocodile.toolbox as tb
from rich.console import Console
from typing import Optional
from machineconfig.utils.utils import INSTALL_VERSION_ROOT


repo_url = r'https://download.sysinternals.com/files/ZoomIt.zip'
__doc__ = """A screen zoom and annotation tool for presentations"""


def main(version: Optional[str] = None):
    _ = version
    print("\n\n\n")
    console = Console()
    console.rule("Installing ZoomIt")
    folder = tb.P(repo_url).download(tb.P.home().joinpath('Downloads')).unzip(inplace=True)

    import psutil
    for proc in psutil.process_iter():
        if proc.name() == "ZoomIt.exe":
            proc.kill()
    folder.joinpath('ZoomIt.exe').move(folder=tb.P.get_env().WindowsApps, overwrite=True)
    INSTALL_VERSION_ROOT.joinpath('ZoomIt').write_text("latest")
    folder.delete(sure=True)
    console.rule("Completed Installation")


if __name__ == '__main__':
    main()
