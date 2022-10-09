
from machineconfig.utils.utils import get_latest_release
from crocodile.environment import AppData

exe = get_latest_release("https://github.com/helix-editor/helix", download_n_extract=True, suffix="x86_64-windows")
exe.parent.joinpath("runtime").move(folder=AppData.joinpath("helix"), overwrite=True)
exe.parent.joinpath("contrib").move(folder=AppData.joinpath("helix"), overwrite=True)

# as per https://github.com/helix-editor/helix/wiki/How-to-install-the-default-language-servers
# and https://spacevim.org/use-vim-as-a-python-ide/

""" 
pip install python-lsp-server

pip install --user pylint
pip install --user yapf
pip install --user isort

"""
