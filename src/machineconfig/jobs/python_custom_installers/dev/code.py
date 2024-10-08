
"""vs code installer as per https://code.visualstudio.com/docs/setup/linux
"""

from typing import Optional
import platform


config_dict = {
        "repo_url": "CUSTOM",
        "doc": "Visual Studio Code",
        "filename_template_windows_amd_64": "VSCodeSetup-{}.exe",
        "filename_template_linux_amd_64": "code_{}.deb",
        "strip_v": True,
        "exe_name": "code"
    }


def main(version: Optional[str] = None):

    if platform.system() == 'Linux':
        import machineconfig.jobs.python_custom_installers as module
        from pathlib import Path
        install_script = Path(module.__file__).parent.joinpath("scripts/linux/vscode.sh").read_text(encoding="utf-8")

    elif platform.system() == 'Windows':
        install_script = "winget install -e --id Microsoft.VisualStudioCode"
    else:
        raise NotImplementedError(f"Unsupported platform: {platform.system()}")
    _ = version
    return install_script


if __name__ == '__main__':
    pass
