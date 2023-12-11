
import crocodile.toolbox as tb
from machineconfig.utils.utils import INSTALL_VERSION_ROOT
from machineconfig.utils.installer import get_latest_release
from rich.console import Console
from platform import system
from typing import Optional


__doc__ = """diskonaut is a terminal disk space navigator."""


def main(version: Optional[str] = None) -> None:
    if system() == "Windows":
        console = Console()
        console.rule("Installing diskonaut")
        # url = r'https://drive.google.com/uc?id=1MsDaW6JXmS1LVyfThtUuJy4WRxODEjZB&export=download'
        # dir_ = tb.P(url).download(name='diskonaut.zip').unzip(inplace=True)
        file = tb.P(r"https://api.onedrive.com/v1.0/shares/u!aHR0cHM6Ly8xZHJ2Lm1zL3UvcyFBbV9saHJyWG1yOGhoU21sajdQMmNteEFfcHBh/root/content").download(name="diskonaut.exe")
        file.move(folder=tb.P.get_env().WindowsApps, overwrite=True)
        INSTALL_VERSION_ROOT.create().joinpath("diskonaut").write_text(data="v0.11.0")
        console.rule("Completed Installation")
    else:
        url = r'https://github.com/imsnif/diskonaut'
        url = get_latest_release(repo_url=url, exe_name="diskonaut", download_n_extract=True, suffix="unknown-linux-musl", compression="tar.gz", version=version)


# share on cloud: cloud_copy ~\AppData\Local\Microsoft\WindowsApps\diskonaut.exe odg1:  -rs


if __name__ == '__main__':
    main()
