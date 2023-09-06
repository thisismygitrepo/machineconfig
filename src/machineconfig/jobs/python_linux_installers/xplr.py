

from machineconfig.utils.utils import get_latest_release
import crocodile.toolbox as tb
from typing import Optional


__doc__ = """A terminal file explorer with vi keybindings"""


def main(version: Optional[str] = None):
    existing_version = tb.Terminal().run("xplr --version").op_if_successfull_or_default(strict_err=True, strict_returcode=True)
    if existing_version is not None:
        if existing_version == version:
            print(f"XPLR already installed at version {version}")
            return
        else:
            print(f"XPLR already installed at version {existing_version}. Installing version {version}...")
    repo_url = tb.P(r"https://github.com/sayanarijit/xplr")
    release = get_latest_release(repo_url.as_url_str(), version=version)
    if not isinstance(release, tb.P): raise ValueError(f"Failed to get latest release. Expected a Path object, got {release}")
    path = release.joinpath(f"xplr-linux.tar.gz").download().ungz_untar(inplace=True)
    exe = path.joinpath("xplr")
    exe.chmod(0o777)
    # exe.move(folder=r"/usr/local/bin", overwrite=False)
    tb.Terminal().run(f"sudo mv {exe} /usr/local/bin/").print_if_unsuccessful(desc="MOVING executable to /usr/local/bin", strict_err=True, strict_returncode=True)
    path.delete(sure=True)


if __name__ == '__main__':
    pass
