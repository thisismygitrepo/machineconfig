
from machineconfig.utils.utils import get_latest_release
from platform import system
import crocodile.toolbox as tb

repo_url = tb.P(r"https://github.com/helix-editor/helix")


def main(version=None):
    if system() == 'Windows':
        from crocodile.environment import AppData
        target = AppData
        suffix = "x86_64-windows"
        compression = "zip"
        exe = get_latest_release(repo_url.as_url_str(), download_n_extract=True, suffix=suffix, delete=False, exe_name="hx", version=version)
    else:
        target = tb.P.home().joinpath(".config")
        suffix = "x86_64-linux"
        compression = 'tar.xz'
        exe = get_latest_release(repo_url.as_url_str(), download_n_extract=False, suffix=suffix, version=version)
        name = f'{repo_url[-1]}-{exe[-1]}-{suffix}.tar.xz'
        exe = exe.joinpath(name).download().unxz_untar(inplace=True)
        exe = exe.search()[0].joinpath("hx")
        exe.chmod(0o777)
        # exe.move(folder=r"/usr/local/bin", overwrite=True)
        tb.Terminal().run(f"sudo mv {exe} /usr/local/bin/").print_if_unsuccessful(desc="MOVING executable to /usr/local/bin", strict_err=True, strict_returncode=True)

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
