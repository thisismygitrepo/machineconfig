
# import numpy as np
# import matplotlib.pyplot as plt
import crocodile.toolbox as tb
# from platform import system
from typing import Optional


__doc__ = """Plugin for chrome to bypass paywalls"""


def main(version: Optional[str] = None):
    _ = version
    # see remove paywalls and enhance YT experience by Chris Titus
    folder = r"C:\\"
    tb.P("https://github.com/iamadamdev/bypass-paywalls-chrome/archive/master.zip").download().unzip(folder=folder, content=True)
    tb.P(folder).joinpath("bypass-paywalls-chrome-master")
    return ""


if __name__ == '__main__':
    main()
