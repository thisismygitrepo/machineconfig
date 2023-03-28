

from machineconfig.utils.utils import get_latest_release
from platform import system
import crocodile.toolbox as tb

repo_url = tb.P(r"https://github.com/mgunyho/tere")
__doc__ = """Tere is a terminal file explorer written in Rust. No more ls + cd"""

def main(version=None):
    if system() == 'Windows':
        from crocodile.environment import AppData
        target = AppData
        suffix = "x86_64-pc-windows-gnu"
        exe = get_latest_release(repo_url.as_url_str(), suffix=suffix, download_n_extract=True, delete=False, strip_v=True, version=version)
    else:
        release = get_latest_release(repo_url.as_url_str(), version=version)
        path = release.joinpath(f"tere-{str(release[-1]).replace('v', '')}-x86_64-unknown-linux-gnu.zip").download()
        exe = path.unzip(inplace=True).joinpath("tere")
        exe.chmod(0o777)
        # exe.move(folder=r"/usr/local/bin", overwrite=False)
        tb.Terminal().run(f"sudo mv {exe} /usr/local/bin/").print_if_unsuccessful(desc="MOVING executable to /usr/local/bin", strict_err=True, strict_returncode=True)


if __name__ == '__main__':
    main()