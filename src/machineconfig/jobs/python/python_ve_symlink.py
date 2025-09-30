"""Symlinks"""

from rich import box
from rich.console import Console
from rich.panel import Panel

from machineconfig.utils.path_extended import PathExtended


def main() -> None:
    console = Console()
    console.print(
        Panel.fit(
            "\n".join(["Create symlinks for virtual environments"]),
            title="🔗 Symlink Creator",
            border_style="cyan",
            box=box.ROUNDED,
        )
    )
    target = PathExtended(input("🎯 Symlink to which target? ")).expanduser().absolute()
    source = input(f"📍 Symlink from which source? [default to: CWD/{target.name}] ") or PathExtended.cwd().joinpath(target.name)
    if isinstance(source, str):
        source = PathExtended(source).expanduser().absolute()
    source.symlink_to(target, overwrite=True)
    console.print(
        Panel.fit(
            "\n".join([f"📍 Source: {source}", f"🎯 Target: {target}"]),
            title="✅ Symlink Created",
            border_style="green",
            box=box.ROUNDED,
        )
    )
    console.print("🔗 Finished creating symlink.", style="bold cyan")


if __name__ == "__main__":
    pass
