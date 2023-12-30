
# gives examples of how to use a command, its halfway between `man tool` and `tool --help`
from machineconfig.utils.installer import find_move_delete_linux, get_latest_release
import crocodile.toolbox as tb
from platform import system
from typing import Optional


repo_url = r'https://github.com/dbrgn/tealdeer'
__doc__ = "Too long, didn't read, but for cli tools."


def main(version: Optional[str] = None):
    release = get_latest_release(repo_url=repo_url, exe_name="tealdeer", version=version)
    if not isinstance(release, tb.P): raise ValueError(f"Failed to get latest release. Expected a Path object, got {repo_url}")
    if system() == 'Windows':
        f = release.joinpath('tealdeer-windows-x86_64-msvc.exe').download().rename('tldr.exe')
        f.move(folder=f.get_env().WindowsApps, overwrite=True)
    elif system() == 'Linux':
        f = release.joinpath('tealdeer-linux-x86_64-musl').download().rename('tldr')
        find_move_delete_linux(f, 'tldr', delete=True)
        tb.Terminal().run("tldr --update")
    else:
        raise NotImplementedError(f"System {system()} not supported")


if __name__ == '__main__':
    main()
