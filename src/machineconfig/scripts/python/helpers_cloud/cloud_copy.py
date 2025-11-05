"""
CC
"""

from typing import Optional, Annotated
import typer

from tenacity import retry, stop_after_attempt, wait_chain, wait_fixed



@retry(stop=stop_after_attempt(3), wait=wait_chain(wait_fixed(1), wait_fixed(4), wait_fixed(9)))
def get_securely_shared_file(url: Optional[str] = None, folder: Optional[str] = None) -> None:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress
    import getpass
    import os
    from machineconfig.utils.path_extended import PathExtended

    console = Console()

    console.print(Panel("🚀 Secure File Downloader", title="[bold blue]Downloader[/bold blue]", border_style="blue"))

    folder_obj = PathExtended.cwd() if folder is None else PathExtended(folder)
    print(f"📂 Target folder: {folder_obj}")

    if os.environ.get("DECRYPTION_PASSWORD") is not None:
        print("🔑 Using password from environment variables")
        pwd = str(os.environ.get("DECRYPTION_PASSWORD"))
    else:
        pwd = getpass.getpass(prompt="🔑 Enter decryption password: ")

    if url is None:
        if os.environ.get("SHARE_URL") is not None:
            url = os.environ.get("SHARE_URL")
            assert url is not None
            print("🔗 Using URL from environment variables")
        else:
            url = input("🔗 Enter share URL: ")

    console.print(Panel("📡 Downloading from URL...", title="[bold blue]Download[/bold blue]", border_style="blue"))
    with Progress(transient=True) as progress:
        _task = progress.add_task("Downloading... ", total=None)
        url_obj = PathExtended(url).download(folder=folder_obj)

    console.print(Panel(f"📥 Downloaded file: {url_obj}", title="[bold green]Success[/bold green]", border_style="green"))

    console.print(Panel("🔐 Decrypting and extracting...", title="[bold blue]Processing[/bold blue]", border_style="blue"))
    with Progress(transient=True) as progress:
        _task = progress.add_task("Decrypting... ", total=None)
        tmp_folder = PathExtended.tmpdir(prefix="tmp_unzip")
        try:
            res = url_obj.decrypt(pwd=pwd, inplace=True).unzip(inplace=True, folder=tmp_folder)
            for x in res.search("*"):
                x.move(folder=folder_obj, overwrite=True)
        finally:
            # Clean up temporary folder
            if tmp_folder.exists():
                tmp_folder.delete()



def main(
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
    """📤 Upload or 📥 Download files/folders to/from cloud storage services like Google Drive, Dropbox, OneDrive, etc."""
    from rich.console import Console
    from rich.panel import Panel
    from machineconfig.utils.path_extended import PathExtended
    from machineconfig.scripts.python.helpers_cloud.helpers2 import parse_cloud_source_target
    from machineconfig.scripts.python.helpers_cloud.cloud_helpers import Args
    from machineconfig.utils.accessories import pprint

    console = Console()
    console.print(Panel("☁️  Cloud Copy Utility", title="[bold blue]Cloud Copy[/bold blue]", border_style="blue", width=152))
    args_obj = Args(
        overwrite=overwrite,
        share=share,
        rel2home=rel2home,
        root=root,
        key=key,
        pwd=pwd,
        encrypt=encrypt,
        zip=zip_,
        os_specific=os_specific,
        config=config,
    )

    if args_obj.config == "ss" and (source.startswith("http") or source.startswith("bit.ly")):
        console.print(Panel("🔒 Detected secure share link", title="[bold yellow]Warning[/bold yellow]", border_style="yellow"))
        if source.startswith("https://drive.google.com/open?id="):
            file_id = source.split("https://drive.google.com/open?id=")[1]
            if file_id:  # Ensure we actually extracted an ID
                source = f"https://drive.google.com/uc?export=download&id={file_id}"
                print("🔄 Converting Google Drive link to direct download URL")
            else:
                console.print(Panel("❌ Invalid Google Drive link format", title="[bold red]Error[/bold red]", border_style="red"))
                raise ValueError("Invalid Google Drive link format")
        return get_securely_shared_file(url=source, folder=target)

    if args_obj.rel2home is True and args_obj.root is None:
        args_obj.root = "myhome"
        print("🏠 Using 'myhome' as root directory")

    console.print(Panel("🔍 Parsing source and target paths...", title="[bold blue]Info[/bold blue]", border_style="blue"))
    cloud, source, target = parse_cloud_source_target(args=args_obj, source=source, target=target)

    console.print(Panel("⚙️  Configuration:", title="[bold blue]Config[/bold blue]", border_style="blue"))
    pprint(args_obj.__dict__, "CLI config")

    if args_obj.key is not None:
        console.print(Panel("❌ Key-based encryption is not supported yet", title="[bold red]Error[/bold red]", border_style="red"))
        raise ValueError("Key-based encryption is not supported yet.")

    if cloud in source:
        console.print(Panel(f"📥 DOWNLOADING FROM CLOUD\n☁️  Cloud: {cloud}\n📂 Source: {source.replace(cloud + ':', '')}\n🎯 Target: {target}", title="[bold blue]Download[/bold blue]", border_style="blue", width=152))

        PathExtended(target).from_cloud(
            cloud=cloud,
            remotepath=source.replace(cloud + ":", ""),
            unzip=args_obj.zip,
            decrypt=args_obj.encrypt,
            pwd=args_obj.pwd,
            overwrite=args_obj.overwrite,
            rel2home=args_obj.rel2home,
            os_specific=args_obj.os_specific,
            root=args_obj.root,
            strict=False,
        )
        console.print(Panel("✅ Download completed successfully", title="[bold green]Success[/bold green]", border_style="green", width=152))

    elif cloud in target:
        console.print(Panel(f"📤 UPLOADING TO CLOUD\n☁️  Cloud: {cloud}\n📂 Source: {source}\n🎯 Target: {target.replace(cloud + ':', '')}", title="[bold blue]Upload[/bold blue]", border_style="blue", width=152))

        res = PathExtended(source).to_cloud(
            cloud=cloud, remotepath=target.replace(cloud + ":", ""), zip=args_obj.zip, encrypt=args_obj.encrypt, pwd=args_obj.pwd, rel2home=args_obj.rel2home, root=args_obj.root, os_specific=args_obj.os_specific, strict=False, share=args_obj.share
        )
        console.print(Panel("✅ Upload completed successfully", title="[bold green]Success[/bold green]", border_style="green", width=152))

        if args_obj.share:
            fname = f".share_url_{cloud}"
            if PathExtended(source).is_dir():
                share_url_path = PathExtended(source).joinpath(fname)
            else:
                share_url_path = PathExtended(source).with_suffix(fname)
            share_url_path.write_text(res.as_url_str(), encoding="utf-8")
            console.print(Panel(f"🔗 SHARE URL GENERATED\n📝 URL file: {share_url_path}\n🌍 {res.as_url_str()}", title="[bold blue]Share[/bold blue]", border_style="blue", width=152))
    else:
        console.print(Panel(f"❌ ERROR: Cloud '{cloud}' not found in source or target", title="[bold red]Error[/bold red]", border_style="red", width=152))
        raise ValueError(f"Cloud `{cloud}` not found in source or target.")


def arg_parser() -> None:
    typer.run(main)


if __name__ == "__main__":
    arg_parser()
