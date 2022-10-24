
import crocodile.toolbox as tb


url = r'https://dystroy.org/broot/download/x86_64-pc-windows-gnu/broot.exe'


def main():
    print("\n\n\n")
    print("Installing Broot".center(100, "-"))
    p = tb.P(url).download()
    p.move(folder=tb.get_env().WindowsApps, overwrite=True)
    print("Completed Installation".center(100, "-"))


if __name__ == '__main__':
    main()
