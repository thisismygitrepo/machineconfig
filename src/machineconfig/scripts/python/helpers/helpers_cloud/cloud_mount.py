"""Cloud mount script"""

import typer
from typing import Optional, Annotated, Literal


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
    from machineconfig.utils.accessories import randstr
    import platform
    DEFAULT_MOUNT = "~/data/rclone"

    header = f"{' ' + cloud + ' | ' + cloud_brand + ' '}".center(50, "=")
    if platform.system() == "Windows":
        sub_text_path = PathExtended("~/tmp_results/tmp_files").expanduser().joinpath(f"{randstr()}.ps1")
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
    cloud: Annotated[Optional[str], typer.Option(..., "--cloud", "-c", help="cloud to mount.")] = None,
    destination: Annotated[Optional[str], typer.Option(..., "--destination", "-d", help="destination to mount")] = None,
    network: Annotated[Optional[str], typer.Option(..., "--network", "-n", help="mount network drive")] = None,
    zellij_session: Annotated[Optional[str], typer.Option(None, "--zellij-session", "-z", help="zellij session name for Linux/macOS")] = None,
    backend: Annotated[Literal["zellij", "z", "tmux", "t", "auto", "a"], typer.Option("--backend", "-b", help="terminal backend for Linux/macOS")] = "auto",
    interactive: Annotated[bool, typer.Option("--interactive", "-i", help="Choose cloud interactively from config.")] = True,
) -> None:
    if interactive:
        pass
    from machineconfig.utils.options import choose_from_options
    from pathlib import Path
    import platform
    import subprocess
    from rich.console import Console
    from rich.panel import Panel
    from machineconfig.scripts.python.helpers.helpers_cloud.cloud_mount_zellij import build_zellij_launch_command
    from machineconfig.scripts.python.helpers.helpers_cloud.cloud_mont_tmux import build_tmux_launch_command
    console = Console()
    DEFAULT_MOUNT = "~/data/rclone"
    DEFAULT_ZELLIJ_SESSION = "cloud-mount"

    title = "☁️  Cloud Mount Utility"
    console.print(Panel(title, title_align="left", border_style="blue"))

    config = get_rclone_config()
    if cloud is None:
        res: list[str] = choose_from_options(multi=True, msg="which cloud", options=config.sections(), header="CLOUD MOUNT", default=None, tv=True)
        if not res:
            print("❌ Error: No cloud selected")
            raise typer.Exit(code=1)
        clouds: list[str] = res

    else:
        if cloud not in config.sections():
            print(f"❌ Error: Cloud '{cloud}' not found in config")
            raise typer.Exit(code=1)
        clouds = [cloud]

    system_name = platform.system()

    if network and len(clouds) > 1:
        print("❌ Error: Network mode supports only one cloud at a time")
        raise typer.Exit(code=1)

    mount_locations: dict[str, str] = {}
    if network is None:
        mount_lines: list[str] = []
        for cloud_name in clouds:
            if destination is None:
                mount_loc_path = Path(DEFAULT_MOUNT).expanduser().joinpath(cloud_name)
            elif len(clouds) == 1:
                mount_loc_path = Path(destination).expanduser()
            else:
                mount_loc_path = Path(destination).expanduser().joinpath(cloud_name)

            mount_lines.append(f"{cloud_name} → {mount_loc_path}")

            if system_name == "Windows":
                print("🪟 Creating mount directory on Windows...")
                mount_loc_path.parent.mkdir(parents=True, exist_ok=True)
            elif system_name in ["Linux", "Darwin"]:
                printable_name = "Linux" if system_name == "Linux" else "macOS"
                print(f"🐧 Creating mount directory on {printable_name}...")
                try:
                    mount_loc_path.mkdir(parents=True, exist_ok=True)
                except (FileExistsError, OSError) as err:
                    warning_line = "⚠️  WARNING: Mount directory issue"
                    err_line = f"{err}"
                    console.print(Panel(f"{warning_line}\n{err_line}", title="Warning", border_style="yellow"))
            else:
                print("❌ Error: Unsupported platform")
                raise typer.Exit(code=1)
            mount_locations[cloud_name] = str(mount_loc_path)

        mount_info = "📂 Mount locations:\n" + "\n".join(mount_lines)
        console.print(Panel(mount_info, border_style="blue"))

    elif network and system_name == "Windows":
        only_cloud = clouds[0]
        mount_locations[only_cloud] = "X: --network-mode"
        print(f"🔌 Setting up network mount at {mount_locations[only_cloud]}")
    else:
        print("❌ Error: Network mount only supported on Windows")
        raise typer.Exit(code=1)

    mount_commands: dict[str, str] = {
        cloud_name: f"rclone mount {cloud_name}: {mount_locations[cloud_name]} --vfs-cache-mode full --file-perms=0777" for cloud_name in clouds
    }
    mount_command_info = "\n".join([f"{cloud_name}: {mount_commands[cloud_name]}" for cloud_name in clouds])
    console.print(Panel(f"🚀 Preparing mount command(s):\n{mount_command_info}", border_style="blue"))

    if system_name == "Windows":
        if backend not in ["auto", "a"]:
            print("❌ Error: --backend is only available on Linux/macOS for cloud mount")
            raise typer.Exit(code=1)
        if len(clouds) > 1:
            print("❌ Error: Multiple clouds in one command is only supported on Linux/macOS")
            raise typer.Exit(code=1)
        cloud_name = clouds[0]
        mount_cmd = mount_commands[cloud_name]
        txt = f"""
wt --window 0 --profile "Windows PowerShell" --startingDirectory "$HOME/data/rclone" `; split-pane --horizontal  --profile "Command Prompt" --size 0.2 powershell -Command "{mount_cmd}" `; split-pane --vertical --profile "Windows PowerShell" --size 0.2 powershell -NoExit -Command "rclone about {cloud_name}:"  `; move-focus up
"""
    elif system_name in ["Linux", "Darwin"]:
        session_name = zellij_session if zellij_session else DEFAULT_ZELLIJ_SESSION
        backend_resolved: Literal["zellij", "tmux"]
        match backend:
            case "zellij" | "z" | "auto" | "a":
                backend_resolved = "zellij"
            case "tmux" | "t":
                backend_resolved = "tmux"
            case _:
                print(f"❌ Error: Unsupported backend '{backend}'")
                raise typer.Exit(code=1)

        if backend_resolved == "zellij":
            txt = build_zellij_launch_command(mount_commands=mount_commands, mount_locations=mount_locations, session_name=session_name)
        else:
            txt = build_tmux_launch_command(mount_commands=mount_commands, mount_locations=mount_locations, session_name=session_name)
    else:
        print("❌ Error: Unsupported platform")
        raise typer.Exit(code=1)

    subprocess.run(txt, shell=True, check=True)
    # draw success box dynamically
    title1 = "✅ Cloud mount command prepared successfully"
    title2 = "🔄 Running mount process..."
    console.print(Panel(f"{title1}\n{title2}", title="Success", border_style="green"))



def get_app():
    app = typer.Typer(name="cloud-mount", help="Cloud mount utility")
    app.command(name="mount", no_args_is_help=True)(mount)
    return app

if __name__ == "__main__":
    appp = get_app()
    appp()
