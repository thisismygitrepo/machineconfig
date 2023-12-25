from machineconfig.utils.installer import get_latest_release
import crocodile.toolbox as tb
from typing import Optional


__doc__ = """A terminal file explorer with vi keybindings"""


def main(version: Optional[str] = None):
    repo_url = tb.P(r"https://github.com/sayanarijit/xplr")
    release = get_latest_release(repo_url=repo_url.as_url_str(), exe_name="xplr", version=version)
    if isinstance(release, tb.P):
        path = release.joinpath(f"xplr-linux.tar.gz").download().ungz_untar(inplace=True)
        exe = path.joinpath("xplr")
        exe.chmod(0o777)
        # exe.move(folder=r"/usr/local/bin", overwrite=False)
        tb.Terminal().run(f"sudo mv {exe} /usr/local/bin/").print_if_unsuccessful(desc="MOVING executable to /usr/local/bin", strict_err=True, strict_returncode=True)
        path.delete(sure=True)


if __name__ == '__main__':
    pass
