
from typing import Literal
from machineconfig.utils.source_of_truth import LIBRARY_ROOT, CONFIG_ROOT


def copy_assets_to_machine(which: Literal["scripts", "settings"]):
    # callers, symlink public, shell profile adder (requires init.ps1 and scripts dir to be present on machine)
    import platform
    if platform.system().lower() == "windows":
        system = "windows"
    elif platform.system().lower() == "linux" or platform.system().lower() == "darwin":
        system = "linux"
    else:
        raise NotImplementedError(f"System {platform.system().lower()} not supported")
    match which:
        case "scripts":
            source = LIBRARY_ROOT.joinpath("scripts", system)
            target = CONFIG_ROOT.joinpath("scripts", system)

        case "settings":
            source = LIBRARY_ROOT.joinpath("settings")
            target = CONFIG_ROOT.joinpath("settings")
    from machineconfig.utils.path_extended import PathExtended
    PathExtended(source).copy(folder=target.parent, overwrite=True)
    import platform
    system = platform.system().lower()
    if system == "linux" and which == "scripts":
        import subprocess
        from rich.console import Console
        console = Console()
        console.print("\n[bold]📜 Setting executable permissions for scripts...[/bold]")
        subprocess.run(f"chmod +x {CONFIG_ROOT.joinpath(f'scripts/{system.lower()}')} -R", shell=True, capture_output=True, text=True)
        console.print("[green]✅ Script permissions updated[/green]")


