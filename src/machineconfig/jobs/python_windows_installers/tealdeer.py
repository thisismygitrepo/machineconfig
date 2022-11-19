
# gives examples of how to use a command, its halfway between `man tool` and `tool --help`
from machineconfig.utils.utils import get_latest_release

url = r'https://github.com/dbrgn/tealdeer'


def main():
    f = get_latest_release(url).joinpath('tealdeer-windows-x86_64-msvc.exe').download().rename('tldr.exe')
    f.move(folder=f.get_env().WindowsApps, overwrite=True)


if __name__ == '__main__':
    main()
