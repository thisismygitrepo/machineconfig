
import crocodile.toolbox as tb
from typing import Optional

# fd (rust)
# cargo install fd-find
# search for files/folder names only. Result can be fed to fzf for further filtering. For that use: fd | fzf. one can also make fd the searcher in fzf

url = 'https://github.com/ascii-boxes/boxes'
__doc__ = """ASCI draws boxes around text."""

def main(version: Optional[str]  = None):
    from machineconfig.utils.utils import get_latest_release, tmp_install_dir

    get_latest_release(url, suffix="intel-win32", download_n_extract=True, version=version, strip_v=True, delete=False)
    tmp_install_dir.search("boxes.cfg", r=True)[0].move(folder=tb.P.get_env().WindowsApps, overwrite=True)
    tmp_install_dir.search("*boxes*", files=False).apply(lambda x: x.delete(sure=True))


if __name__ == '__main__':
    main()
