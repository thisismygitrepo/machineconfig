
import crocodile.toolbox as tb

url = r'https://download.sysinternals.com/files/ZoomIt.zip'


if __name__ == '__main__':
    print("\n\n\n")
    print("Installing ZoomIt".center(100, "-"))
    folder = tb.P(url).download(tb.P.home().joinpath('Downloads')).unzip(inplace=True)
    folder.joinpath('ZoomIt.exe').move(folder=tb.get_env().WindowsApps, overwrite=True)
    folder.delete(sure=True)
    print("Completed Installation".center(100, "-"))

