
# gives examples of how to use a command, its halfway between `man tool` and `tool --help`
from machineconfig.utils.utils import get_latest_release, find_move_delete_linux
import crocodile.toolbox as tb
from platform import system
from typing import Optional


url = r'https://github.com/dbrgn/tealdeer'
__doc__ = "Too long, didn't read, but for cli tools."


def main(version: Optional[str] = None):
    if system() == 'Windows':
        f = get_latest_release(url, version=version).joinpath('tealdeer-windows-x86_64-msvc.exe').download().rename('tldr.exe')
        f.move(folder=f.get_env().WindowsApps, overwrite=True)
    elif system() == 'Linux':
        f = get_latest_release(url, version=version).joinpath('tealdeer-linux-x86_64-musl').download().rename('tldr')
        find_move_delete_linux(f, 'tldr', delete=True)
        tb.Terminal().run("tldr --update")
    else:
        raise NotImplementedError(f"System {system()} not supported")


if __name__ == '__main__':
    main()
