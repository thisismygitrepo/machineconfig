"""Cloud management commands - lazy loading subcommands."""

import typer
from typing import Optional, Annotated


def sync(
    source: Annotated[str, typer.Argument(help="source")],
    target: Annotated[str, typer.Argument(help="target")],
    transfers: Annotated[int, typer.Option("--transfers", "-t", help="Number of threads in syncing.")] = 10,
    root: Annotated[str, typer.Option("--root", "-R", help="Remote root.")] = "myhome",
    key: Annotated[Optional[str], typer.Option("--key", "-k", help="Key for encryption")] = None,
    pwd: Annotated[Optional[str], typer.Option("--pwd", "-P", help="Password for encryption")] = None,
    encrypt: Annotated[bool, typer.Option("--encrypt", "-e", help="Decrypt after receiving.")] = False,
    zip_: Annotated[bool, typer.Option("--zip", "-z", help="unzip after receiving.")] = False,
    bisync: Annotated[bool, typer.Option("--bisync", "-b", help="Bidirectional sync.")] = False,
    delete: Annotated[bool, typer.Option("--delete", "-D", help="Delete files in remote that are not in local.")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Verbosity of mprocs to show details of syncing.")] = False,
) -> None:
    """🔄 Synchronize files/folders between local and cloud storage."""
    from machineconfig.scripts.python.helpers.helpers_cloud.cloud_sync import main as sync_main
    sync_main(source=source, target=target, transfers=transfers, root=root, key=key, pwd=pwd, encrypt=encrypt, zip_=zip_, bisync=bisync, delete=delete, verbose=verbose)


def copy(
    source: Annotated[str, typer.Argument(help="📂 file/folder path to be taken from here.")],
    target: Annotated[str, typer.Argument(help="🎯 file/folder path to be be sent to here.")],
    overwrite: Annotated[bool, typer.Option("--overwrite", "-o", help="✍️ Overwrite existing file.")] = False,
    share: Annotated[bool, typer.Option("--share", "-s", help="🔗 Share file / directory")] = False,
    rel2home: Annotated[bool, typer.Option("--relative2home", "-r", help="🏠 Relative to `myhome` folder")] = False,
    root: Annotated[Optional[str], typer.Option("--root", "-R", help="🌳 Remote root. None is the default, unless rel2home is raied, making the default `myhome`.")] = None,
    key: Annotated[Optional[str], typer.Option("--key", "-k", help="🔑 Key for encryption")] = None,
    pwd: Annotated[Optional[str], typer.Option("--password", "-p", help="🔒 Password for encryption")] = None,
    encrypt: Annotated[bool, typer.Option("--encrypt", "-e", help="🔐 Encrypt before sending.")] = False,
    zip_: Annotated[bool, typer.Option("--zip", "-z", help="📦 unzip after receiving.")] = False,
    os_specific: Annotated[bool, typer.Option("--os-specific", "-O", help="💻 choose path specific for this OS.")] = False,
    config: Annotated[Optional[str], typer.Option("--config", "-c", help="⚙️ path to cloud.json file.")] = None,
) -> None:
    """📤 Upload or 📥 Download files/folders to/from cloud storage services."""
    from machineconfig.scripts.python.helpers.helpers_cloud.cloud_copy import main as copy_main
    copy_main(source=source, target=target, overwrite=overwrite, share=share, rel2home=rel2home, root=root, key=key, pwd=pwd, encrypt=encrypt, zip_=zip_, os_specific=os_specific, config=config)


def mount(
    cloud: Annotated[Optional[str], typer.Option(help="cloud to mount")] = None,
    destination: Annotated[Optional[str], typer.Option(help="destination to mount")] = None,
    network: Annotated[Optional[str], typer.Option(help="mount network drive")] = None,
) -> None:
    """🔗 Mount cloud storage services as local drives."""
    from machineconfig.scripts.python.helpers.helpers_cloud.cloud_mount import mount as mount_main
    mount_main(cloud=cloud, destination=destination, network=network)


def get_app() -> typer.Typer:
    app = typer.Typer(add_completion=False, no_args_is_help=True, help="☁️ Cloud management commands")

    app.command(name="sync", no_args_is_help=True, short_help="🔄 [s] Synchronize files/folders between local and cloud storage.")(sync)
    app.command(name="s", no_args_is_help=True, hidden=True)(sync)

    app.command(name="copy", no_args_is_help=True, short_help="📤 [c] Upload or 📥 Download files/folders to/from cloud storage.")(copy)
    app.command(name="c", no_args_is_help=True, hidden=True)(copy)

    app.command(name="mount", no_args_is_help=True, short_help="🔗 [m] Mount cloud storage services as local drives.")(mount)
    app.command(name="m", no_args_is_help=True, hidden=True)(mount)

    return app


def main():
    app = get_app()
    app()


if __name__ == "__main__":
    pass
    # a = get_app()(asdf)
