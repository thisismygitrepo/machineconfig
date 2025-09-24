"""
Utils
"""

import machineconfig
from pathlib import Path

EXCLUDE_DIRS = [".links", ".ai", ".scripts", ".venv", ".git", ".idea", ".vscode", "node_modules", "__pycache__", ".mypy_cache"]

LIBRARY_ROOT = Path(machineconfig.__file__).resolve().parent
REPO_ROOT = LIBRARY_ROOT.parent.parent

CONFIG_PATH = Path.home().joinpath(".config/machineconfig")
DEFAULTS_PATH = Path.home().joinpath("dotfiles/machineconfig/defaults.ini")

INSTALL_VERSION_ROOT = CONFIG_PATH.joinpath("cli_tools_installers/versions")
INSTALL_TMP_DIR = Path.home().joinpath("tmp_results", "tmp_installers")

# LINUX_INSTALL_PATH = '/usr/local/bin'
# LINUX_INSTALL_PATH = '~/.local/bin'
LINUX_INSTALL_PATH = Path.home().joinpath(".local/bin").__str__()
WINDOWS_INSTALL_PATH = Path.home().joinpath("AppData/Local/Microsoft/WindowsApps").__str__()


if __name__ == "__main__":
    pass
