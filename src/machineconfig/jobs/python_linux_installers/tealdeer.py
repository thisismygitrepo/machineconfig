
# gives examples of how to use a command, its halfway between `man tool` and `tool --help`
from machineconfig.utils.utils import get_latest_release, find_move_delete_linux
import crocodile.toolbox as tb

url = r'https://github.com/dbrgn/tealdeer'


def main():
    f = get_latest_release(url).joinpath('tealdeer-linux-x86_64-musl').download().rename('tldr')
    find_move_delete_linux(f, 'tldr', delete=True)
    tb.Terminal().run("tldr --update")


if __name__ == '__main__':
    main()
