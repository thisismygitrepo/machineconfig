
"""
The executable of this program is suspicious according to virustotal.
"""

from machineconfig.utils.installer import find_move_delete_linux, get_latest_release
import crocodile.toolbox as tb
from platform import system


url = r'https://github.com/uw-labs/strongbox'


def main():
    d_url = get_latest_release(url, exe_name="strongbox")
    if isinstance(d_url, tb.P):
        v = d_url.name.replace("v", "")
        if system() == 'Linux':
            f = d_url.joinpath(f"strongbox_{v}_linux_amd64").download().with_name("strongbox", inplace=True)
            find_move_delete_linux(f, 'tldr', delete=True)
            tb.Terminal().run("tldr --update")

        elif system() == 'Windows':
            f = d_url.joinpath(f"strongbox_{v}_windows_amd64.exe").download().with_name("strongbox.exe", inplace=True)
            f.move(folder=f.get_env().WindowsApps, overwrite=True)

        else:
            raise NotImplementedError(f"System {system()} not supported")
        tb.Terminal().run("strongbox -git-config", shell="powershell").print()


if __name__ == '__main__':
    main()
