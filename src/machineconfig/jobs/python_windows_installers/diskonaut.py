
import crocodile.toolbox as tb


def main():
    print("\n\n\n")
    print("Installing Broot".center(100, "-"))
    url = r'https://drive.google.com/uc?id=1MsDaW6JXmS1LVyfThtUuJy4WRxODEjZB&export=download'
    dir_ = tb.P(url).download(name='diskonaut.zip').unzip(inplace=True)
    dir_.search()[0].move(folder=tb.get_env().WindowsApps, overwrite=True)
    dir_.delete(sure=True)
    print("Completed Installation".center(100, "-"))


if __name__ == '__main__':
    main()