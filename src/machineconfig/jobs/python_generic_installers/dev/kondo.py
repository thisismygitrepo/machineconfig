
from machineconfig.utils.utils import get_latest_release, find_move_delete_linux
from platform import system


url = 'https://github.com/tbillington/kondo'


def main(version=None):
    if system() == 'Windows':
        get_latest_release(url, download_n_extract=True, file_name='kondo-x86_64-pc-windows-msvc.zip', version=version)
    elif system() == 'Linux':
        downloaded = get_latest_release(url, download_n_extract=False, version=version).joinpath("kondo-x86_64-unknown-linux-gnu.tar.gz").download().ungz_untar(inplace=True)
        find_move_delete_linux(downloaded=downloaded, tool_name="kondo")
    else:
        raise NotImplementedError(f"System {system()} not supported")


if __name__ == '__main__':
    main()
