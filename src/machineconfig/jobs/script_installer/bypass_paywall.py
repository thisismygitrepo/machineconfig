
# import numpy as np
# import matplotlib.pyplot as plt

# from platform import system
from typing import Optional
from crocodile.file_management import P


__doc__ = """Plugin for chrome to bypass paywalls"""


def main(version: Optional[str] = None):
    _ = version
    # see remove paywalls and enhance YT experience by Chris Titus
    folder = r"C:\\"
    P("https://github.com/iamadamdev/bypass-paywalls-chrome/archive/master.zip").download().unzip(folder=folder, content=True)
    P(folder).joinpath("bypass-paywalls-chrome-master")
    return ""


if __name__ == '__main__':
    pass
