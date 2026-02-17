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


def _kdl_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _build_cloud_tab_kdl(cloud_name: str, mount_cmd: str, mount_loc: str, focused: bool) -> str:
    focus_segment = " focus=true" if focused else ""
    escaped_cloud_name = _kdl_escape(cloud_name)
    escaped_mount_cmd = _kdl_escape(mount_cmd)
    escaped_mount_loc = _kdl_escape(mount_loc)
    escaped_about_target = _kdl_escape(f"{cloud_name}:")
    return f"""
    tab name=\"{escaped_cloud_name}\"{focus_segment} {{
        pane split_direction=\"vertical\" size=\"60%\" {{
            pane name=\"mount\" command=\"bash\" {{
                args \"-lc\" \"{escaped_mount_cmd}\"
            }}
            pane name=\"about\" command=\"rclone\" {{
                args \"about\" \"{escaped_about_target}\"
            }}
        }}
        pane split_direction=\"vertical\" size=\"40%\" {{
            pane name=\"explorer\" command=\"yazi\" {{
                args \"{escaped_mount_loc}\"
            }}
            pane name=\"monitor\" command=\"btm\" {{
                args \"--default_widget_type\" \"net\" \"--expanded\"
            }}
            pane name=\"shell\" cwd=\"{escaped_mount_loc}\"
        }}
    }}
"""


def _build_zellij_layout_kdl(mount_commands: dict[str, str], mount_locations: dict[str, str]) -> str:
    tab_blocks: list[str] = []
    for index, cloud_name in enumerate(mount_commands):
        tab_blocks.append(_build_cloud_tab_kdl(cloud_name=cloud_name, mount_cmd=mount_commands[cloud_name], mount_loc=mount_locations[cloud_name], focused=index == 0))
    return f"""layout {{
{''.join(tab_blocks)}
}}
"""


def get_within_current_session_code():
    return """

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
zellij run --direction left --cwd $HOME/data/rclone/{cloud} -- yazi $HOME/data/rclone/{cloud}
zellij run --direction up -- btm --default_widget_type net --expanded
zellij run --in-place --cwd $HOME/data/rclone/{cloud} -- bash
zellij action move-focus up
"""


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
    interactive: Annotated[bool, typer.Option("--interactive", "-i", help="Choose cloud interactively from config.")] = True,
) -> None:
    if interactive:
        pass
    from machineconfig.utils.options import choose_from_options
    from pathlib import Path
    import platform
    import shlex
    import subprocess
    import tempfile
    from rich.console import Console
    from rich.panel import Panel
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
        layout_kdl = _build_zellij_layout_kdl(mount_commands=mount_commands, mount_locations=mount_locations)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".kdl", prefix="cloud-mount-", delete=False) as layout_file:
            layout_file.write(layout_kdl)
            layout_path = layout_file.name
        txt = f"zellij --session {shlex.quote(session_name)} --new-session-with-layout {shlex.quote(layout_path)}"
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
