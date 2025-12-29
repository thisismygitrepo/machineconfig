
import typer
from typing import Annotated, Optional, Literal


def sync(
        direction: Annotated[Literal["up", "u", "down", "d"], typer.Argument(..., help="Direction of sync: backup or retrieve")],
        cloud: Annotated[Optional[str], typer.Option("--cloud", "-c", help="☁️  Cloud configuration name (rclone config name)")] = None,
        which: Annotated[Optional[str], typer.Option("--which", "-w", help="📝 Comma-separated list of items to BACKUP (from backup.toml), or 'all' for all items")] = None,
        interactive: Annotated[bool, typer.Option("--interactive", "-i", help="🤔 Prompt the selection of which items to process")] = False,
    ):
    
    from machineconfig.scripts.python.helpers.helpers_devops.devops_backup_retrieve import main_backup_retrieve
    main_backup_retrieve(direction="BACKUP", which=which, cloud=cloud)


def get_app() -> typer.Typer:
    app = typer.Typer(name="data", help="💾 [d] Backup and Retrieve configuration files and directories to/from cloud storage using rclone.", no_args_is_help=True, add_help_option=True, add_completion=False)
    app.command(name="sync", no_args_is_help=True, hidden=False, help="💾 [s] Backup files and directories to cloud storage using rclone.")(sync)
    app.command(name="s", no_args_is_help=True, hidden=True,)(sync)
    return app
