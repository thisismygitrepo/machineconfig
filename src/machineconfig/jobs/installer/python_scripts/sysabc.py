

import platform
from typing import Optional
from rich import box
from rich.console import Console
from rich.panel import Panel
from machineconfig.utils.schemas.installer.installer_types import InstallerData
from pathlib import Path


def main(installer_data: InstallerData, version: Optional[str]) -> None:
    console = Console()
    _ = installer_data
    console.print(
        Panel.fit(
            "\n".join([f"💻 Platform: {platform.system()}", f"🔄 Version: {'latest' if version is None else version}"]),
            title="🔧 ABC Installer",
            border_style="blue",
            box=box.ROUNDED,
        )
    )

    _ = version
    if platform.system() == "Windows":
        console.print("🪟 Installing ABC on Windows using winget...", style="bold")
        from machineconfig.jobs.installer import powershell_scripts
        script = Path(powershell_scripts.__path__[0]) / "sysabc.ps1"
        program = script.read_text(encoding="utf-8")
    elif platform.system() == "Linux":
        console.print("🐧 Installing ABC on Linux...", style="bold")
        from machineconfig.jobs.installer import linux_scripts
        script = Path(linux_scripts.__path__[0]) / "sysabc_ubuntu.sh"
        program = script.read_text(encoding="utf-8")
    elif platform.system() == "Darwin":
        console.print("🍎 Installing ABC on macOS...", style="bold")
        from machineconfig.jobs.installer import linux_scripts
        script = Path(linux_scripts.__path__[0]) / "sysabc_macos.sh"
        program = script.read_text(encoding="utf-8")
    else:
        error_msg = f"Unsupported platform: {platform.system()}"
        console.print(
            Panel.fit(
                "\n".join([error_msg]),
                title="❌ Error",
                subtitle="⚠️ Unsupported platform",
                border_style="red",
                box=box.ROUNDED,
            )
        )
        raise NotImplementedError(error_msg)
    from machineconfig.utils.code import print_code, run_shell_script
    print_code(code=program, lexer="shell", desc="Installation Script Preview")
    run_shell_script(program, display_script=True, clean_env=False)
