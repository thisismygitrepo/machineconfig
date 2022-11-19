
# gives examples of how to use a command, its halfway between `man tool` and `tool --help`
from machineconfig.utils.utils import get_latest_release, find_move_delete_linux

url = r'https://github.com/dbrgn/tealdeer'


def main():
    f = get_latest_release(url).joinpath('tealdeer-linux-x86_64-musl').download().rename('tldr')
    find_move_delete_linux(f, 'tldr', delete=True)


if __name__ == '__main__':
    main()
