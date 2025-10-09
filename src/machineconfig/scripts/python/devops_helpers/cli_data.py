
import typer

app_data = typer.Typer(help="💾 [d] data subcommands", no_args_is_help=True)

@app_data.command()
def backup():
    """💾 BACKUP"""
    from machineconfig.scripts.python.devops_helpers.devops_backup_retrieve import main_backup_retrieve
    main_backup_retrieve(direction="BACKUP")


@app_data.command()
def retrieve():
    """📥 RETRIEVE"""
    from machineconfig.scripts.python.devops_helpers.devops_backup_retrieve import main_backup_retrieve
    main_backup_retrieve(direction="RETRIEVE")

