"""
Utils
"""

import machineconfig
# import platform
from pathlib import Path

LIBRARY_ROOT = Path(machineconfig.__file__).resolve().parent
REPO_ROOT = LIBRARY_ROOT.parent.parent
# PROGRAM_PATH = Path(Path.home().joinpath("tmp_results", "shells", "python_return_command").__str__() + (".ps1" if platform.system() == "Windows" else ".sh"))
CONFIG_PATH = Path.home().joinpath(".config/machineconfig")
DEFAULTS_PATH = Path.home().joinpath("dotfiles/machineconfig/defaults.ini")

INSTALL_VERSION_ROOT = CONFIG_PATH.joinpath("cli_tools_installers/versions")
INSTALL_TMP_DIR = Path.home().joinpath("tmp_results", "tmp_installers")

# LINUX_INSTALL_PATH = '/usr/local/bin'
# LINUX_INSTALL_PATH = '~/.local/bin'
LINUX_INSTALL_PATH = Path.home().joinpath(".local/bin").__str__()
WINDOWS_INSTALL_PATH = Path.home().joinpath("AppData/Local/Microsoft/WindowsApps").__str__()


if __name__ == "__main__":
    # import typer
    # typer.run(check_tool_exists)
    pass
