
from platform import system
from machineconfig.utils.utils import get_latest_release, tb, find_move_delete_linux, find_move_delete_windows

# =================================================== python's qr code to create qrcode on terminal from simple text.
tb.Terminal().run("pip install qrcode", shell="pwsh")


# =================================================== Rust's qrscan to allow computers to scan qr code from webcam.
if system() == 'Windows': _ = get_latest_release('https://github.com/sayanarijit/qrscan', download_n_extract=True, strip_v=True)
else: _ = get_latest_release(repo_url='https://github.com/sayanarijit/qrscan', download_n_extract=True, linux=True, strip_v=True, suffix="x86_64-unknown-linux-gnu", compression="tar.gz")


# =================================================== Go's qrcp to allow file transfer between computer and phone.
url = get_latest_release("https://github.com/claudiodangelis/qrcp", download_n_extract=False)
if system() == "Windows":
    downloaded = url.joinpath(f"qrcp_{url[-1].str.replace('v', '')}_Windows_x86_64.tar.gz").download().ungz_untar(inplace=True)
    find_move_delete_windows(downloaded, "qrcp")
else:
    downloaded = url.joinpath(f"qrcp_{url[-1].str.replace('v', '')}_linux_x86_64.tar.gz").download().ungz_untar(inplace=True)
    find_move_delete_linux(downloaded, "qrcp")

