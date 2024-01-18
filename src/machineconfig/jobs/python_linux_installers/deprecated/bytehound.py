from machineconfig.utils.installer import get_latest_release
import crocodile.toolbox as tb
from crocodile.meta import Terminal
from typing import Optional


url = r"https://github.com/koute/bytehound"
fname = r"bytehound-x86_64-unknown-linux-gnu.tgz"
__doc__ = """Inspecting the memory usage of a running process"""


def main(version: Optional[str] = None):
    release = get_latest_release(repo_url=url, exe_name="bytehound", version=version)
    if not isinstance(release, tb.P): raise ValueError(f"Failed to get latest release. Expected a Path object, got {release}")
    downloaded = tb.P(release).joinpath(fname).download().ungz_untar(inplace=True)
    Terminal().run(f"sudo mv {downloaded}/* /usr/local/bin/").print_if_unsuccessful(desc="MOVING executable to /usr/local/bin", strict_err=True, strict_returncode=True)


if __name__ == '__main__':
    main()
