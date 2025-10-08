"""
Utils
"""

import machineconfig
from pathlib import Path

EXCLUDE_DIRS = [".links", ".ai", ".venv", ".git", ".idea", ".vscode", "node_modules", "__pycache__", ".mypy_cache"]
LIBRARY_ROOT = Path(machineconfig.__file__).resolve().parent

CONFIG_ROOT = Path.home().joinpath(".config/machineconfig")
DEFAULTS_PATH = Path.home().joinpath("dotfiles/machineconfig/defaults.ini")

INSTALL_VERSION_ROOT = CONFIG_ROOT.joinpath("cli_tools_installers/versions")
INSTALL_TMP_DIR = Path.home().joinpath("tmp_results", "tmp_installers")

# LINUX_INSTALL_PATH = '/usr/local/bin'
LINUX_INSTALL_PATH = Path.home().joinpath(".local/bin").__str__()
WINDOWS_INSTALL_PATH = Path.home().joinpath("AppData/Local/Microsoft/WindowsApps").__str__()


def copy_assets_to_machine():
    import platform
    if platform.system().lower() == "windows":
        system = "windows"
    elif platform.system().lower() == "linux" or platform.system().lower() == "darwin":
        system = "linux"
    else:
        raise NotImplementedError(f"System {platform.system().lower()} not supported")
    scripts_dir_source = LIBRARY_ROOT.joinpath("scripts", system)
    settings_dir_source = LIBRARY_ROOT.joinpath("settings")
    scripts_dir_target = CONFIG_ROOT.joinpath("scripts", system)
    settings_dir_target = CONFIG_ROOT.joinpath("settings")
    from machineconfig.utils.path_extended import PathExtended
    PathExtended(scripts_dir_source).copy(folder=scripts_dir_target.parent)
    PathExtended(settings_dir_source).copy(folder=settings_dir_target.parent)


if __name__ == "__main__":
    pass
