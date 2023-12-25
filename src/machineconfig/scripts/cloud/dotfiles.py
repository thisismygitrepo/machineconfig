
"""
share dotfiles.
"""

import crocodile.toolbox as tb
import os


def put():
    pwd: str = tb.P.home().joinpath("dotfiles/creds/passwords/quick_password").read_text().strip()

    # from crocodile.file_management import Read
    # from machineconfig.utils.utils import DEFAULTS_PATH
    # cloud: str = Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
    # print(f"⚠️ Using default cloud: {cloud}")

    if os.environ.get("CLOUD_NAME") is not None:
        cloud = os.environ.get("CLOUD_NAME")
        assert cloud is not None
    else:
        cloud = input("Enter cloud name: ")

    res = tb.P.home().joinpath("dotfiles").zip().encrypt(pwd=pwd).move(folder=tb.P.home().joinpath("tmp_results"), overwrite=True).with_name("dotfiles_share.zip.enc", inplace=True, overwrite=True)
    url_ = res.to_cloud(cloud=cloud, share=True, rel2home=True)
    print(url_)


def get():
    if os.environ.get("DECRYPTION_PASSWORD") is not None:
        pwd = os.environ.get("DECRYPTION_PASSWORD")
    else:
        pwd = input("Enter dotfiles decryption password: ")


    if os.environ.get("DOTFILES_URL") is not None:
        url = os.environ.get("DOTFILES_URL")
        assert url is not None
    else:
        url = input("Enter dotfiles url: ")

    url_obj = tb.P(url).download(name="dotfiles.zip.enc")
    res = url_obj.decrypt(pwd=pwd).unzip(inplace=True).joinpath("dotfiles")
    res = res.move(folder=tb.P.home(), overwrite=True)
