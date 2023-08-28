

"""
Rust version of lf (GO)
"""

# from machineconfig.utils.utils import get_latest_release, find_move_delete_linux
import crocodile.toolbox as tb
from typing import Optional


__doc__ = """A terminal file manager written in Rust."""
# repo_url = tb.P(r"https://github.com/kamiyaa/joshuto")
# release = get_latest_release(repo_url.as_url_str())
# path = release.joinpath(f"joshuto-{release[-1]}-x86_64-unknown-linux-gnu.tar.gz")

def main(version: Optional[str] = None):
    _ = version
    # pre-release
    path = tb.P(r'https://github.com/kamiyaa/joshuto/releases/download/v0.9.4/joshuto-v0.9.4-x86_64-unknown-linux-gnu.tar.gz')
    path = path.download().ungz_untar(inplace=True)
    exe = path.search().list[0].joinpath("joshuto")
    exe.chmod(0o777)
    tb.Terminal().run(f"sudo mv {exe} /usr/local/bin/").print_if_unsuccessful(desc="MOVING executable to /usr/local/bin", strict_err=True, strict_returncode=True)
    path.delete(sure=True)
    # after first release:
    # url = get_latest_release("https://github.com/kamiyaa/joshuto", suffix="x86_64-unknown-linux-gnu", compression="tar.gz", download_n_extract=True)


if __name__ == '__main__':
    main()
