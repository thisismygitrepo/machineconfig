
from platform import system
from machineconfig.utils.utils import get_latest_release, tb

url = get_latest_release('https://github.com/XAMPPRocky/tokei', download_n_extract=False)


def main():
    if system() == 'Windows':
        url.joinpath('tokei-x86_64-pc-windows-msvc.exe').download().move(folder=tb.get_env().WindowsApps, name='tokei.exe', overwrite=True)
    else:
        link = url.joinpath('tokei-x86_64-unknown-linux-gnu.tar.gz').download().ungz_untar(inplace=True)
        exe = link.joinpath('tokei')
        exe.chmod(0o777)
        # exe.move(folder=r"/usr/local/bin", overwrite=False)
        tb.Terminal().run(f"sudo mv {exe} /usr/local/bin/").print()


if __name__ == '__main__':
    main()
