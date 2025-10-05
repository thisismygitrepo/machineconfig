
import typer
from machineconfig.scripts.python.cloud_helpers.cloud_sync import main
from machineconfig.scripts.python.cloud_helpers.cloud_copy import main as copy_main
from machineconfig.scripts.python.cloud_helpers.cloud_mount import main as mount_main


app = typer.Typer(add_completion=False, no_args_is_help=True)
app.command(name="sync", no_args_is_help=True, help="""🔄 Synchronize files/folders between local and cloud storage.""")(main)
app.command(name="copy", no_args_is_help=True, short_help="""📤 Upload or 📥 Download files/folders to/from cloud storage services like Google Drive, Dropbox, OneDrive, etc.""")(copy_main)
app.command(name="mount", no_args_is_help=True, short_help="""🔗 Mount cloud storage services like Google Drive, Dropbox, OneDrive, etc. as local drives.""")(mount_main)

