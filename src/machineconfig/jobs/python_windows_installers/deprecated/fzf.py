
# fzf (glang)
# search for files/folder names, but can come with preview option. For that use: my variant fzz.ps1
from machineconfig.utils.installer import get_latest_release
import crocodile.toolbox as tb
from typing import Optional

repo_url = 'https://github.com/junegunn/fzf'
__doc__ = """a general-purpose cli fuzzy finder."""


def main(version: Optional[str] = None):
    # tb.Terminal().run("nu -c 'ps | where name == fzf.exe | each { |it| kill $it.pid --force}'", shell="pwsh").print()
    tb.L(tb.install_n_import("psutil").process_iter()).filter(lambda x: x.name() == 'fzf.exe').apply(lambda x: x.kill())
    get_latest_release(repo_url, exe_name="fzf", suffix='windows_amd64', download_n_extract=True, version=version)


if __name__ == '__main__':
    pass
