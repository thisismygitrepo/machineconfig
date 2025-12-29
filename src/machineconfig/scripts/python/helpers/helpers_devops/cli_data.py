import typer
from typing import Annotated, Optional, Literal


def sync(
    direction: Annotated[Literal["up", "u", "down", "d"], typer.Argument(..., help="Direction of sync: backup or retrieve")],
    cloud: Annotated[Optional[str], typer.Option("--cloud", "-c", help="☁️  Cloud configuration name (rclone config name)")] = None,
    which: Annotated[
        Optional[str], typer.Option("--which", "-w", help="📝 Comma-separated list of items to BACKUP (from backup.toml), or 'all' for all items")
    ] = None,
    repo: Annotated[
        Literal["library", "l", "user", "u", "all", "a"],
        typer.Option("--repo", "-r", help="📁 Which backup configuration to use: 'library' or 'user'"),
    ] = "library",
    # interactive: Annotated[bool, typer.Option("--interactive", "-i", help="🤔 Prompt the selection of which items to process")] = False,
):
    from machineconfig.scripts.python.helpers.helpers_devops.devops_backup_retrieve import main_backup_retrieve

    match direction:
        case "up" | "u":
            direction_resolved = "BACKUP"
        case "down" | "d":
            direction_resolved = "RETRIEVE"
    main_backup_retrieve(direction=direction_resolved, which=which, cloud=cloud, repo=repo)


def register_data(
    path_local: Annotated[str, typer.Argument(..., help="Local file/folder path to back up.")],
    name: Annotated[Optional[str], typer.Option("--name", "-n", help="Entry name in the user backup.toml.")] = None,
    path_remote: Annotated[Optional[str], typer.Option("--remote", "-R", help="Remote path override (optional).")] = None,
    zip_: Annotated[bool, typer.Option("--zip/--no-zip", "-z/-nz", help="Zip before uploading.")] = True,
    encrypt: Annotated[bool, typer.Option("--encrypt/--no-encrypt", "-e/-ne", help="Encrypt before uploading.")] = True,
    rel2home: Annotated[Optional[bool], typer.Option("--rel2home/--no-rel2home", "-r/-nr", help="Treat the local path as relative to home.")] = None,
    os: Annotated[Literal["any", "windows", "linux", "darwin"], typer.Option("--os", "-o", help="OS filter for this backup entry.")] = "any",
    os_specific: Annotated[Optional[bool], typer.Option("--os-specific/--no-os-specific", "-O/-nO", help="Mark the path as OS-specific.")] = None,
) -> None:
    from machineconfig.scripts.python.helpers.helpers_devops.devops_backup_retrieve import register_backup_entry

    try:
        backup_path, entry_name, replaced = register_backup_entry(
            path_local=path_local,
            entry_name=name,
            path_remote=path_remote,
            zip=zip_,
            encrypt=encrypt,
            rel2home=rel2home,
            os_specific=os_specific,
            os=os,
        )
    except ValueError as exc:
        typer.echo(f"[red]Error:[/] {exc}")
        raise typer.Exit(code=1)
    action = "Updated" if replaced else "Added"
    typer.echo(f"{action} backup entry '{entry_name}' in {backup_path}")


def get_app() -> typer.Typer:
    app = typer.Typer(
        name="data",
        help="🗄️ [d] Backup and retrieve configuration files and directories to/from cloud storage using rclone.",
        no_args_is_help=True,
        add_help_option=True,
        add_completion=False,
    )

    app.command(name="sync", no_args_is_help=True, hidden=False, help="🔄 [s] Sync (backup) files and directories to cloud storage using rclone.")(
        sync
    )

    app.command(name="s", no_args_is_help=True, hidden=True)(sync)

    app.command(name="register", no_args_is_help=True, hidden=False, help="📝 [r] Register a new backup entry in user backup.toml.")(register_data)

    app.command(name="r", no_args_is_help=True, hidden=True)(register_data)

    return app
