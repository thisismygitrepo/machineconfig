
# import numpy as np
# import matplotlib.pyplot as plt

# from platform import system
from typing import Optional
from crocodile.file_management import P


config_dict = {
        "repo_url": "CUSTOM",
        "doc": """Plugin for chrome to bypass paywalls""",
        "filename_template_windows_amd_64": "VSCodeSetup-{}.exe",
        "filename_template_linux_amd_64": "code_{}.deb",
        "strip_v": True,
        "exe_name": "code"
    }


def main(version: Optional[str] = None):
    _ = version
    # see remove paywalls and enhance YT experience by Chris Titus
    folder = r"C:\\"
    P("https://github.com/iamadamdev/bypass-paywalls-chrome/archive/master.zip").download().unzip(folder=folder, content=True)
    P(folder).joinpath("bypass-paywalls-chrome-master")
    return ""


if __name__ == '__main__':
    pass
