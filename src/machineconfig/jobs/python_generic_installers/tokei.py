
from platform import system
from machineconfig.utils.utils import get_latest_release, tb


def main(version=None):
    url = get_latest_release('https://github.com/XAMPPRocky/tokei', download_n_extract=False, version=version)

    if system() == 'Windows':
        url.joinpath('tokei-x86_64-pc-windows-msvc.exe').download().move(folder=tb.get_env().WindowsApps, name='tokei.exe', overwrite=True)
    else:
        link = url.joinpath('tokei-x86_64-unknown-linux-gnu.tar.gz').download().ungz_untar(inplace=True)
        exe = link.joinpath('tokei')
        exe.chmod(0o777)
        # exe.move(folder=r"/usr/local/bin", overwrite=False)
        tb.Terminal().run(f"sudo mv {exe} /usr/local/bin/").print_if_unsuccessful(desc="MOVING executable to /usr/local/bin", strict_err=True, strict_returncode=True)


if __name__ == '__main__':
    main()
