
from machineconfig.utils.utils import get_latest_release

url = 'https://github.com/tbillington/kondo'


if __name__ == '__main__':
    get_latest_release(url, download_n_extract=True, file_name='kondo-x86_64-pc-windows-msvc.zip')
