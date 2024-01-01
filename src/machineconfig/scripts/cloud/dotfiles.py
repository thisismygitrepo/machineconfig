
"""
share dotfiles.
"""

import crocodile.toolbox as tb
from crocodile.meta import RepeatUntilNoException
from machineconfig.utils.utils import DEFAULTS_PATH
import os
import getpass


def put():
    pwd: str = tb.P.home().joinpath("dotfiles/creds/passwords/quick_password").read_text().strip()

    if os.environ.get("CLOUD_NAME") is not None:
        cloud = os.environ.get("CLOUD_NAME")
        assert cloud is not None
    else:
        try:
            default_cloud: str = tb.Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
        except Exception:
            default_cloud = 'No default cloud found.'
        cloud = input(f"Enter cloud name (default {default_cloud}): ") or default_cloud

    res = tb.P.home().joinpath("dotfiles").zip().encrypt(pwd=pwd).move(folder=tb.P.home().joinpath("tmp_results"), overwrite=True).with_name("dotfiles_share.zip.enc", inplace=True, overwrite=True)
    url_ = res.to_cloud(cloud=cloud, share=True, rel2home=True)
    print(url_.as_url_obj())
    print(url_.as_url_str())


@RepeatUntilNoException()
def get():
    if os.environ.get("DECRYPTION_PASSWORD") is not None:
        pwd = os.environ.get("DECRYPTION_PASSWORD")
    else:
        pwd = getpass.getpass("Enter decryption password: ")


    if os.environ.get("DOTFILES_URL") is not None:
        url = os.environ.get("DOTFILES_URL")
        assert url is not None
    else:
        url = input("Enter dotfiles url: ")

    from rich.progress import Progress
    with Progress(transient=True) as progress:
        _task = progress.add_task("Downloading ... ", total=None)
        url_obj = tb.P(url).download(name="dotfiles.zip.enc")
    with Progress(transient=True) as progress:
        _task = progress.add_task("Decrypting ... ", total=None)
        res = url_obj.decrypt(pwd=pwd).unzip(inplace=True).joinpath("dotfiles")
    with Progress(transient=True) as progress:
        _task = progress.add_task("Moving ... ", total=None)
        res = res.move(folder=tb.P.home(), overwrite=True)
