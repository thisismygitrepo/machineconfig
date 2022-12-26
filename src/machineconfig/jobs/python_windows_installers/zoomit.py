
import crocodile.toolbox as tb
from rich.console import Console

url = r'https://download.sysinternals.com/files/ZoomIt.zip'


def main():
    print("\n\n\n")
    console = Console()
    console.rule("Installing ZoomIt")
    folder = tb.P(url).download(tb.P.home().joinpath('Downloads')).unzip(inplace=True)
    folder.joinpath('ZoomIt.exe').move(folder=tb.get_env().WindowsApps, overwrite=True)
    folder.delete(sure=True)
    console.rule("Completed Installation")


if __name__ == '__main__':
    main()
