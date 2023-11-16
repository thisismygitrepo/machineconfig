
import crocodile.toolbox as tb
from typing import Optional

# fd (rust)
# cargo install fd-find
# search for files/folder names only. Result can be fed to fzf for further filtering. For that use: fd | fzf. one can also make fd the searcher in fzf

repo_url = 'https://github.com/ascii-boxes/boxes'
__doc__ = """ASCI draws boxes around text."""

def main(version: Optional[str]  = None):
    from machineconfig.utils.utils import INSTALL_TMP_DIR
    from machineconfig.utils.installer import get_latest_release
    release = get_latest_release(repo_url=repo_url, exe_name="boxes", suffix="intel-win32", download_n_extract=True, version=version, strip_v=True, delete=False)
    if isinstance(release, tb.P):
        INSTALL_TMP_DIR.search("boxes.cfg", r=True).list[0].move(folder=tb.P.get_env().WindowsApps, overwrite=True)
        INSTALL_TMP_DIR.search("*boxes*", files=False).apply(lambda x: x.delete(sure=True))


if __name__ == '__main__':
    main()
