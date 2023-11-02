
from platform import system
from machineconfig.utils.installer import get_latest_release
import crocodile.toolbox as tb
from typing import Optional


__doc__ = """Counts the number of lines of code, comments, and blanks in a project."""
repo_url = 'https://github.com/XAMPPRocky/tokei'


def main(version: Optional[str] = None):
    url = get_latest_release(repo_url=repo_url, exe_name="tokei", download_n_extract=False, version=version)
    assert isinstance(url, tb.P), f"Expected a Path object, got {type(url)} instead."
    if system() == 'Windows':
        url.joinpath('tokei-x86_64-pc-windows-msvc.exe').download().move(folder=tb.P.get_env().WindowsApps, name='tokei.exe', overwrite=True)
    else:
        link = url.joinpath('tokei-x86_64-unknown-linux-gnu.tar.gz').download().ungz_untar(inplace=True)
        exe = link.joinpath('tokei')
        exe.chmod(0o777)
        # exe.move(folder=r"/usr/local/bin", overwrite=False)
        tb.Terminal().run(f"sudo mv {exe} /usr/local/bin/").print_if_unsuccessful(desc="MOVING executable to /usr/local/bin", strict_err=True, strict_returncode=True)


if __name__ == '__main__':
    main()
