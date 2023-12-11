
from platform import system
from machineconfig.utils.installer import get_latest_release
# import crocodile.toolbox as tb
from typing import Optional


__doc__ = """qr code scanner"""
repo_url = 'https://github.com/sayanarijit/qrscan'


def main(version: Optional[str] = None):
    # =================================================== Rust's qrscan to allow computers to scan qr code from webcam.
    if system() == 'Windows': _ = get_latest_release(repo_url=repo_url, exe_name="qrscan", download_n_extract=True, strip_v=True, version=version)
    else: _ = get_latest_release(repo_url=repo_url, exe_name="qrscan", download_n_extract=True, strip_v=True, version=version, suffix="x86_64-unknown-linux-gnu", compression="tar.gz")


if __name__ == '__main__':
    main()
