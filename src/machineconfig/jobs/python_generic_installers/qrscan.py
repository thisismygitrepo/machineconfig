
import crocodile.toolbox as tb
from platform import system
from machineconfig.utils.utils import get_latest_release, tb

# python's qr code to create qrcode on terminal from simple text.
tb.Terminal().run("pip install qrcode", shell="pwsh")

# Rust's qrscan to allow computers to scan qr code from webcam.


if system() == 'Windows':
    url = get_latest_release('https://github.com/sayanarijit/qrscan', download_n_extract=True, strip_v=True)
else:
    url = get_latest_release('https://github.com/sayanarijit/qrscan', download_n_extract=True, linux=True, strip_v=True, suffix="x86_64-unknown-linux-gnu")


