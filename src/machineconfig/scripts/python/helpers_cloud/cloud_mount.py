"""Cloud mount script"""

import typer
from typing import Optional, Annotated


def get_rclone_config():
    from machineconfig.utils.io import read_ini
    from pathlib import Path
    import platform
    if platform.system() == "Windows":
        config = read_ini(Path.home().joinpath("AppData/Roaming/rclone/rclone.conf"))
    elif platform.system() in ["Linux", "Darwin"]:
        config = read_ini(Path.home().joinpath(".config/rclone/rclone.conf"))
    else:
        raise ValueError("unsupported platform")
    return config


def get_mprocs_mount_txt(cloud: str, rclone_cmd: str, cloud_brand: str):  # cloud_brand = config[cloud]["type"]
    from machineconfig.utils.path_extended import PathExtended
    import platform
    DEFAULT_MOUNT = "~/data/rclone"

    header = f"{' ' + cloud + ' | ' + cloud_brand + ' '}".center(50, "=")
    if platform.system() == "Windows":
        sub_text_path = PathExtended.tmpfile(suffix=".ps1")
        sub_text_path.parent.mkdir(parents=True, exist_ok=True)
        sub_text_path.write_text(
            f"""
echo "{header}"
iex 'rclone about {cloud}:'
echo 'See {DEFAULT_MOUNT}/{cloud} for the mounted cloud'

echo ''
""",
            encoding="utf-8",
        )
        txt = f"""
cd ~
mprocs "powershell {sub_text_path}" "{rclone_cmd}" "btm" "timeout 2 & cd {DEFAULT_MOUNT} & lf" "timeout 2 & cd {DEFAULT_MOUNT} & pwsh" "pwsh" --names "info,service,monitor,explorer,main,terminal"
"""
    else:
        txt = f"""
mprocs "echo 'see {DEFAULT_MOUNT}/{cloud} for the mounted cloud'; rclone about {cloud}:" "{rclone_cmd}" "btm" "cd {DEFAULT_MOUNT}; lf" "bash" "bash" --names "about,service,monitor,explorer,main,shell"
"""
    return txt


def mount(
    cloud: Annotated[Optional[str], typer.Option(help="cloud to mount")] = None,
    destination: Annotated[Optional[str], typer.Option(help="destination to mount")] = None,
    network: Annotated[Optional[str], typer.Option(help="mount network drive")] = None,
) -> None:
    from machineconfig.utils.options import choose_from_options
    from pathlib import Path
    import platform
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    DEFAULT_MOUNT = "~/data/rclone"

    # draw header box dynamically
    title = "☁️  Cloud Mount Utility"
    console.print(Panel(title, title_align="left", border_style="blue"))

    config = get_rclone_config()
    if cloud is None:
        res = choose_from_options(multi=False, msg="which cloud", options=config.sections(), header="CLOUD MOUNT", default=None)
        if type(res) is str:
            cloud = res
        else:
            raise ValueError("no cloud selected")
        print(f"🌩️  Selected cloud: {cloud}")

    if network is None:
        if destination is None:
            mount_loc = Path(DEFAULT_MOUNT).expanduser().joinpath(cloud)
        else:
            mount_loc = Path(destination)

        mount_info = f"📂 Mount location: {mount_loc}"
        console.print(Panel(mount_info, border_style="blue"))

        if platform.system() == "Windows":
            print("🪟 Creating mount directory on Windows...")
            mount_loc.parent.mkdir(parents=True, exist_ok=True)
        elif platform.system() in ["Linux", "Darwin"]:
            system_name = "Linux" if platform.system() == "Linux" else "macOS"
            print(f"🐧 Creating mount directory on {system_name}...")
            try:
                mount_loc.mkdir(parents=True, exist_ok=True)
            except (FileExistsError, OSError) as err:
                # We need a umount command here.
                warning_line = "⚠️  WARNING: Mount directory issue"
                err_line = f"{err}"
                console.print(Panel(f"{warning_line}\n{err_line}", title="Warning", border_style="yellow"))
                pass
        else:
            raise ValueError("unsupported platform")

    elif network and platform.system() == "Windows":
        mount_loc = "X: --network-mode"
        print(f"🔌 Setting up network mount at {mount_loc}")
    else:
        raise ValueError("network mount only supported on windows")

    mount_cmd = f"rclone mount {cloud}: {mount_loc} --vfs-cache-mode full --file-perms=0777"
    console.print(Panel(f"🚀 Preparing mount command:\n{mount_cmd}", border_style="blue"))

    # txt = get_mprocs_mount_txt(cloud, mount_cmd)
    if platform.system() == "Windows":
        txt = f"""
wt --window 0 --profile "Windows PowerShell" --startingDirectory "$HOME/data/rclone" `; split-pane --horizontal  --profile "Command Prompt" --size 0.2 powershell -Command "{mount_cmd}" `; split-pane --vertical --profile "Windows PowerShell" --size 0.2 powershell -NoExit -Command "rclone about {cloud}:"  `; move-focus up
"""
    elif platform.system() in ["Linux", "Darwin"]:
        txt = f"""

ZJ_SESSIONS=$(zellij list-sessions)

if [[ "${{ZJ_SESSIONS}}" != *"(current)"* ]]; then
    echo "Not inside a zellij session ..."
    echo '{mount_cmd} --daemon'
    # exit 1

    {mount_cmd} --daemon
fi

zellij run --direction down --name rclone -- {mount_cmd}
sleep 1; zellij action resize decrease down
sleep 0.2; zellij action resize decrease up
sleep 0.2; zellij action resize decrease up
sleep 0.1; zellij action resize decrease up
sleep 0.1; zellij action resize decrease up
sleep 0.1; zellij action resize decrease up
sleep 0.1; zellij action resize decrease up
sleep 0.1; zellij action resize decrease up
sleep 0.1; zellij action resize decrease up
sleep 0.1; zellij action resize decrease up
sleep 0.1; zellij action resize decrease up
sleep 0.1; zellij action resize decrease up
zellij run --direction right --name about -- rclone about {cloud}:
zellij action move-focus up
# zellij action write-chars "cd $HOME/data/rclone/{cloud}; sleep 0.1; ls"
zellij run --direction left --cwd $HOME/data/rclone/{cloud} -- lf
zellij run --direction up -- btm --default_widget_type net --expanded
zellij run --in-place --cwd $HOME/data/rclone/{cloud} -- bash
zellij action move-focus up
"""
    else:
        raise ValueError("unsupported platform")
    # print(f"running command: \n{txt}")
    # PROGRAM_PATH.write_text(txt, encoding="utf-8")
    import subprocess

    subprocess.run(txt, shell=True, check=True)
    # draw success box dynamically
    title1 = "✅ Cloud mount command prepared successfully"
    title2 = "🔄 Running mount process..."
    console.print(Panel(f"{title1}\n{title2}", title="Success", border_style="green"))



def get_app():
    app = typer.Typer(name="cloud-mount", help="Cloud mount utility")
    app.command(name="mount", no_args_is_help=True)(mount)
    return app
