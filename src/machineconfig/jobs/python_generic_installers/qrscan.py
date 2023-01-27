
from platform import system
from machineconfig.utils.utils import get_latest_release, tb, find_move_delete_linux, find_move_delete_windows


def main(version=None):
    # =================================================== Rust's qrscan to allow computers to scan qr code from webcam.
    if system() == 'Windows': _ = get_latest_release('https://github.com/sayanarijit/qrscan', download_n_extract=True, strip_v=True, version=version)
    else: _ = get_latest_release(repo_url='https://github.com/sayanarijit/qrscan', download_n_extract=True, linux=True, strip_v=True, version=version, suffix="x86_64-unknown-linux-gnu", compression="tar.gz")


if __name__ == '__main__':
    main()
