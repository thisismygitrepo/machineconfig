
from machineconfig.utils.utils import get_latest_release, find_move_delete_linux
import crocodile.toolbox as tb

url = r'https://github.com/ClementTsang/bottom'
fname = 'bottom_x86_64-unknown-linux-gnu.tar.gz'


def main():
    release = get_latest_release(url)
    downloaded = tb.P(release).joinpath(fname).download().ungz_untar(inplace=True)
    find_move_delete_linux(downloaded, 'btm', delete=True)


if __name__ == '__main__':
    main()
