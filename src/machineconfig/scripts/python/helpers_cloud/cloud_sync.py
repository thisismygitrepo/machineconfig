"""CS
TODO: use typer or typed-argument-parser to parse args
"""


from typing import Annotated, Optional
import typer


def main(
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

    from machineconfig.scripts.python.helpers_cloud.helpers2 import parse_cloud_source_target
    from machineconfig.scripts.python.helpers_cloud.cloud_helpers import Args
    from machineconfig.scripts.python.helpers_cloud.cloud_mount import get_mprocs_mount_txt
    from rich.console import Console
    from rich.panel import Panel
    console = Console()

    title = "☁️  Cloud Sync Utility"
    console.print(Panel(title, title_align="left", border_style="blue"))

    args_obj = Args(
        root=root,
        key=key,
        pwd=pwd,
        encrypt=encrypt,
        zip=zip_,
        rel2home=True,
        os_specific=False,
    )

    cloud, source, target = parse_cloud_source_target(args=args_obj, source=source, target=target)
    # map short flags to long flags (-u -> --upload), for easier use in the script
    if bisync:
        title = "🔄 BI-DIRECTIONAL SYNC"
        source_line = f"Source: {source}"
        target_line = f"Target: {target}"
        console.print(Panel(f"{source_line}\n{target_line}", title=title, border_style="blue"))
        rclone_cmd = f"""rclone bisync '{source}' '{target}' --resync"""
    else:
        title = "📤 ONE-WAY SYNC"
        source_line = f"Source: {source}"
        arrow_line = "↓"
        target_line = f"Target: {target}"
        console.print(Panel(f"{source_line}\n{arrow_line}\n{target_line}", title=title, border_style="blue"))
        if delete:
            rclone_cmd = f'rclone sync -P "{source}" "{target}" --delete-during --transfers={transfers}'
        else:
            rclone_cmd = f'rclone sync -P "{source}" "{target}" --transfers={transfers}'

    rclone_cmd += f" --progress --transfers={transfers} --verbose"
    # rclone_cmd += f"  --vfs-cache-mode full"
    if delete:
        rclone_cmd += " --delete-during"

    if verbose:
        txt = get_mprocs_mount_txt(cloud=cloud, rclone_cmd=rclone_cmd, cloud_brand="Unknown")
    else:
        txt = f"""{rclone_cmd}"""

    title = "🚀 EXECUTING COMMAND"
    cmd_line = f"{rclone_cmd[:65]}..."
    console.print(Panel(f"{title}\n{cmd_line}", title="[bold blue]Command[/bold blue]", expand=False))

    # import subprocess
    # subprocess.run(txt, shell=True, check=True)
    from machineconfig.utils.code import run_shell_script
    run_shell_script(txt)

