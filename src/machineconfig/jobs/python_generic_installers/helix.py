
from machineconfig.utils.utils import get_latest_release
from platform import system
import crocodile.toolbox as tb

repo_url = tb.P(r"https://github.com/helix-editor/helix")

if system() == 'Windows':
    from crocodile.environment import AppData
    target = AppData
    suffix = "x86_64-windows"
    compression = "zip"
    exe = get_latest_release(repo_url.as_url_str(), download_n_extract=True, suffix=suffix, delete=False, exe_name="hx")
else:
    target = tb.P.home().joinpath(".config")
    suffix = "x86_64-linux"
    compression = 'tar.xz'
    exe = get_latest_release(repo_url.as_url_str(), download_n_extract=False, suffix=suffix)
    name = f'{repo_url[-1]}-{exe[-1]}-{suffix}.tar.xz'
    exe = exe.joinpath(name).download().unxz_untar(inplace=True)
    exe = exe.search()[0].joinpath("hx")
    exe.chmod(0o777)
    # exe.move(folder=r"/usr/local/bin", overwrite=True)
    tb.Terminal().run(f"sudo mv {exe} /usr/local/bin/").print()


exe.parent.joinpath("runtime").move(folder=target.joinpath("helix"), overwrite=True)
exe.parent.joinpath("contrib").move(folder=target.joinpath("helix"), overwrite=True)
exe.parent.parent.delete(sure=True)

# as per https://github.com/helix-editor/helix/wiki/How-to-install-the-default-language-servers
# and https://spacevim.org/use-vim-as-a-python-ide/

""" 
pip install python-lsp-server

pip install --user pylint
pip install --user yapf
pip install --user isort

"""
