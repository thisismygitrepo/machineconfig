
import typer
from machineconfig.scripts.python.helpers_cloud.cloud_sync import main as sync_main
from machineconfig.scripts.python.helpers_cloud.cloud_copy import main as copy_main
from machineconfig.scripts.python.helpers_cloud.cloud_mount import mount as mount_main

def get_app():
    app = typer.Typer(add_completion=False, no_args_is_help=True)

    app.command(name="sync", no_args_is_help=True, help="""🔄 [s] Synchronize files/folders between local and cloud storage.""")(sync_main)
    app.command(name="s", no_args_is_help=True, hidden=True)(sync_main)  # short alias

    app.command(name="copy", no_args_is_help=True, short_help="""📤 [c] Upload or 📥 Download files/folders to/from cloud storage services like Google Drive, Dropbox, OneDrive, etc.""")(copy_main)
    app.command(name="c", no_args_is_help=True, hidden=True)(copy_main)  # short alias

    app.command(name="mount", no_args_is_help=True, short_help="""🔗 [m] Mount cloud storage services like Google Drive, Dropbox, OneDrive, etc. as local drives.""")(mount_main)
    app.command(name="m", no_args_is_help=True, hidden=True)(mount_main)  # short alias

    return app


def main():
    app = get_app()
    app()


if __name__ == "__main__":
    pass
    # a = get_app()(asdf)
