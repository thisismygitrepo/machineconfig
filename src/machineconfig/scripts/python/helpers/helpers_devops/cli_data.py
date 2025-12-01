
import typer
from typing import Annotated, Optional

def backup(cloud: Annotated[Optional[str], typer.Option("--cloud", "-c", help="☁️  Cloud configuration name (rclone config name)")] = None,
           which: Annotated[Optional[str], typer.Option("--which", "-w", help="📝 Comma-separated list of items to BACKUP (from backup.toml), or 'all' for all items")] = None):
    """💾 BACKUP"""
    from machineconfig.scripts.python.helpers.helpers_devops.devops_backup_retrieve import main_backup_retrieve
    main_backup_retrieve(direction="BACKUP", which=which, cloud=cloud)


def retrieve(cloud: Annotated[Optional[str], typer.Option("--cloud", "-c", help="☁️  Cloud configuration name (rclone config name)")] = None,
             which: Annotated[Optional[str], typer.Option("--which", "-w", help="📝 Comma-separated list of items to RETRIEVE (from backup.toml), or 'all' for all items")] = None):
    """📥 RETRIEVE"""
    from machineconfig.scripts.python.helpers.helpers_devops.devops_backup_retrieve import main_backup_retrieve
    main_backup_retrieve(direction="RETRIEVE", which=which, cloud=cloud)


def get_app() -> typer.Typer:
    app = typer.Typer(name="data", help="💾 [d] Backup and Retrieve configuration files and directories to/from cloud storage using rclone.", no_args_is_help=True, add_help_option=True, add_completion=False)
    app.command(name="backup", no_args_is_help=True, hidden=False, help="💾 [b] Backup files and directories to cloud storage using rclone.")(backup)
    app.command(name="b", no_args_is_help=True, hidden=True,)(backup)
    app.command(name="retrieve", no_args_is_help=True, hidden=False, help="📥 [r] Retrieve files and directories from cloud storage using rclone.")(retrieve)
    app.command(name="r", no_args_is_help=True, hidden=True, )(retrieve)
    return app
