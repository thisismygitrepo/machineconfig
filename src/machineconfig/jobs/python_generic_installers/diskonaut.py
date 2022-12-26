
import crocodile.toolbox as tb
from machineconfig.utils.utils import get_latest_release
from rich.console import Console
from platform import system


def main():

    if system() == "Windows":
        console = Console()
        console.rule("Installing diskonaut")
        url = r'https://drive.google.com/uc?id=1MsDaW6JXmS1LVyfThtUuJy4WRxODEjZB&export=download'
        dir_ = tb.P(url).download(name='diskonaut.zip').unzip(inplace=True)
        dir_.search()[0].move(folder=tb.get_env().WindowsApps, overwrite=True)
        dir_.delete(sure=True)
        console.rule("Completed Installation")
    else:
        url = r'https://github.com/imsnif/diskonaut'
        url = get_latest_release(url, download_n_extract=True, suffix="unknown-linux-musl", compression="tar.gz", linux=True)


if __name__ == '__main__':
    main()
