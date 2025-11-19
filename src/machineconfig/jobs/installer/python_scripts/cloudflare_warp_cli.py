
from typing import Optional
import platform
from machineconfig.utils.schemas.installer.installer_types import InstallerData


def main(installer_data: InstallerData, version: Optional[str]):
    _ = installer_data, version
    system = platform.system()
    if system == "Windows":
        raise NotImplementedError("Installer is not yet implemented for Windows.")
    elif system == "Linux":
        from pathlib import Path
        import machineconfig.jobs.installer as module
        program = Path(module.__file__).parent.joinpath("linux_scripts/cloudflare_warp_cli.sh").read_text(encoding="utf-8")
    elif system == "Darwin":
        program = "brew install --cask cloudflare-warp"
    else:
        raise NotImplementedError(f"Unsupported platform: {system}")
    import subprocess
    subprocess.run(program, shell=True, check=True)
    return f"Cloudflare WARP CLI installed successfully on {system}."

