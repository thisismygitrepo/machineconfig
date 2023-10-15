
"""hx
"""

from machineconfig.utils.installer import get_latest_release
from platform import system
import crocodile.toolbox as tb
from typing import Optional


repo_url = tb.P(r"https://github.com/helix-editor/helix")
__doc__ = f"""Rust-based TUI editor"""
EXE = "hx"


def main(version: Optional[str] = None) -> None:
    if system() == 'Windows':
        from crocodile.environment import AppData
        target = AppData
        suffix = "x86_64-windows"
        compression = "zip"
        exe = get_latest_release(repo_url.as_url_str(), download_n_extract=True, suffix=suffix, delete=False, exe_name=EXE, version=version, compression=compression)
    else:
        target = tb.P.home().joinpath(".config")
        suffix = "x86_64-linux"
        compression = 'tar.xz'
        exe = get_latest_release(repo_url=repo_url.as_url_str(), exe_name="hx", download_n_extract=False, suffix=suffix, version=version, compression=compression)
        if not isinstance(exe, tb.P):
            print(f"Could not find browsh release for version {version}")
            return None
        name = f'{repo_url[-1]}-{exe[-1]}-{suffix}.tar.xz'
        exe = exe.joinpath(name).download().unxz_untar(inplace=True)
        search_res = exe.search()
        tmp = search_res.list[0]
        exe = tmp.joinpath("hx")
        exe.chmod(0o777)
        # exe.move(folder=r"/usr/local/bin", overwrite=True)
        tb.Terminal().run(f"sudo mv {exe} /usr/local/bin/").print_if_unsuccessful(desc="MOVING executable to /usr/local/bin", strict_err=True, strict_returncode=True)

    if not isinstance(exe, tb.P) or not isinstance(target, tb.P):
        print(f"Could not find helix release for version {version}")
        return None
    exe.parent.joinpath("runtime").move(folder=target.joinpath("helix"), overwrite=True)
    exe.parent.joinpath("contrib").move(folder=target.joinpath("helix"), overwrite=True)
    exe.parent.parent.delete(sure=True)

# as per https://github.com/helix-editor/helix/wiki/How-to-install-the-default-language-servers
# and https://spacevim.org/use-vim-as-a-python-ide/


"""
#cd ~; mkdir "tmp_asdf"; cd tmp_asdf
#latest=$(get_latest_release "helix-editor/helix")
#wget https://github.com/helix-editor/helix/releases/download/$latest/helix-$latest-x86_64-linux.tar.xz
#tar -xf *; chmod +x ./nu; sudo mv ./nu /usr/local/bin/; cd ~; rm -rdf tmp_asdf
"""


if __name__ == '__main__':
    main()
