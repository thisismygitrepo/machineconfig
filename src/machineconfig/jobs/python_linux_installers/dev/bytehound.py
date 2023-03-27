

from machineconfig.utils.utils import get_latest_release
import crocodile.toolbox as tb
from crocodile.meta import Terminal


url = r"https://github.com/koute/bytehound"
fname = r"bytehound-x86_64-unknown-linux-gnu.tgz"


def main(version=None):
    release = get_latest_release(url, version=version)
    downloaded = tb.P(release).joinpath(fname).download().ungz_untar(inplace=True)
    Terminal().run(f"sudo mv {downloaded}/* /usr/local/bin/").print_if_unsuccessful(desc="MOVING executable to /usr/local/bin", strict_err=True, strict_returncode=True)


if __name__ == '__main__':
    main()
