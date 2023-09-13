
"""Bitwarden CLI installer
"C:\Users\aalsaf01\AppData\Roaming\Bitwarden CLI\data.json";
npm install -g @bitwarden/cli
"""

import crocodile.toolbox as tb
from typing import Optional
import platform


def main(version: Optional[str] = None):
    _ = version
    if platform.system() == "Windows":
        res = tb.P(r"https://vault.bitwarden.com/download/?app=cli&platform=windows").download().unzip(inplace=True)
        res.search("bw.exe").move(tb.P.get_env().WindowsApps)
        res.delete(sure=True)
    elif platform.system() == "Linux":
        raise NotImplementedError("Linux not implemented yet")
    return None
