"""Script to start terminals on windows and wsl"""

from machineconfig.utils.options import display_options, get_ssh_hosts
import platform
from itertools import cycle
from typing import Literal


COLOR_SCHEMES = ["Campbell", "Campbell Powershell", "Solarized Dark", "Ubuntu-ColorScheme", "Retro"]
THEMES_ITER = cycle(COLOR_SCHEMES)
INIT_COMMANDS = ["ls", "lf", "cpufetch", "fastfetch", "btm"]
INIT_COMMANDS_ITER = cycle(INIT_COMMANDS)
SIZE_ITER = cycle([0.6, 0.4, 0.3])
ORIENTATION = ["vertical", "horizontal"]
ORIENTATION_ITER = cycle(ORIENTATION)
ORIENTATION_TYPE = Literal["vertical", "horizontal"]

THIS_MACHINE = "this"
THIS_MACHINE_WSL = "thiswsl"
THIS_MACHINE_HOSTNAME = platform.node()
THIS_MACHINE_HOSTNAME_WSL = f"{THIS_MACHINE_HOSTNAME}wsl"


def main_windows_and_wsl(window: int, hosts: list[str], orientation: ORIENTATION_TYPE = "vertical", mprocs: bool = False):
    print("\n🔧 Configuring terminal layout for Windows and WSL...")
    orientation_oposite = "horizontal" if orientation == "vertical" else "vertical"
    orientation_swap = "up" if orientation == "horizontal" else "left"
    orientation_opposite_move_focus = "up" if orientation_oposite == "horizontal" else "left"
    orientation_opposite_move_focus_other = "down" if orientation_oposite == "horizontal" else "right"
    sleep = 3
    sep = f"\nsleep {sleep}; wt --window {window}"  # or '`;'
    ssh_cmd = "-t 'mprocs'" if mprocs else ""  # 'wsl_ssh_windows_port_forwarding.ps1'
    split_per_machine = 1 / len(hosts)
    size = 0.3
    known_hosts = get_ssh_hosts()
    if len(hosts) == 1:
        print("🖥️ Single host detected. Configuring layout...")
        if "wsl" in hosts[0] or f"{hosts[0]}wsl" in known_hosts:  # its a windows machine with wsl
            host_wind = hosts[0] if "wsl" not in hosts[0] else hosts[0].split("wsl")[0]
            host_linux = f"{host_wind}wsl"
            cmd = f"""
wt --window {window} --title {hosts[0]} powershell -Command "ssh {host_linux} {ssh_cmd}" `; split-pane --{orientation} --title {hosts[0]}wsl --size 0.5 powershell -Command "ssh {host_wind} `; split-pane --{orientation_oposite} --size 0.5 powershell "
"""
        else:  # its a windows machine without wsl
            cmd = f"""wt --window {window} --title {hosts[0]} powershell -Command "ssh {hosts[0]} {ssh_cmd}" `; split-pane --{orientation} --title {hosts[0]}wsl --size 0.1 powershell """

    elif len(hosts) > 1:
        print("🖥️ Multiple hosts detected. Configuring layout...")
        pane_cmd = f'powershell -Command "ssh {hosts[0]} {ssh_cmd}" ' if hosts[0] != THIS_MACHINE else ""
        cmd = f"""wt --window {window} --title {hosts[0]} {pane_cmd} """
        for a_host in hosts[1:]:
            if a_host != THIS_MACHINE:
                pane_cmd = f'powershell -Command "ssh {a_host} {ssh_cmd}" '
            else:
                pane_cmd = "powershell"
            cmd += f"""{sep} split-pane --{orientation_oposite} --title {a_host}Windows --size {split_per_machine} {pane_cmd}  """
        for idx, a_host in enumerate(hosts[::-1]):
            if f"{a_host}wsl" not in known_hosts and a_host != THIS_MACHINE:
                continue
            pane_cmd = f'powershell -Command "ssh {a_host}wsl"' if a_host != THIS_MACHINE else "wsl"
            if idx == 0:
                tmp = ""
            else:
                tmp = f"move-focus {orientation_opposite_move_focus}" if idx % 2 == 1 else f"move-focus {orientation_opposite_move_focus_other}"
            cmd += f"""{sep} {tmp} split-pane --{orientation} --title {a_host}wsl --size {size} {pane_cmd} """
            cmd += f"""{sep} swap-pane {orientation_swap} """
    else:
        raise NotImplementedError(f"❌ len(hosts) = {len(hosts)}. Only 1 or 2 hosts are supported.")
    print("✅ Terminal layout configured successfully!\n")
    return cmd


def main():
    import argparse

    print("\n" + "=" * 50)
    print("🖥️ Welcome to the Terminal Starter Tool")
    print("=" * 50 + "\n")

    parser = argparse.ArgumentParser()
    parser.add_argument("--panes", "-p", type=int, help="🔲 The number of panes to open.", default=4)
    parser.add_argument("--vertical", "-V", action="store_true", help="↕️ Switch orientation to vertical from default horizontal.")
    parser.add_argument("--window", "-w", type=int, help="🪟 The window ID to use.", default=0)  # 0 refers to this window.
    parser.add_argument("--hosts", "-H", type=str, nargs="*", help="🌐 The hosts to connect to.", default=None)
    args = parser.parse_args()

    if args.panes:
        print("🔲 Configuring panes...")
        cmd = f"wt --window {args.window} --colorScheme '{next(THEMES_ITER)}' pwsh -NoExit -Command '{next(INIT_COMMANDS_ITER)}' "
        cmd += f" `; new-tab --colorScheme '{next(THEMES_ITER)}' --profile pwsh --title 't2' --tabColor '#f59218' "
        cmd += f" `; new-tab --colorScheme '{next(THEMES_ITER)}' --profile pwsh --title 't3' --tabColor '#009999' "
        for idx in range(args.panes):
            if idx % 2 == 0:
                cmd += f" `; move-focus down split-pane --horizontal --size {next(SIZE_ITER)} --colorScheme '{next(THEMES_ITER)}'  pwsh -NoExit -Command '{next(INIT_COMMANDS_ITER)}' "
            else:
                cmd += f" `; move-focus up split-pane --vertical --size {next(SIZE_ITER)} --colorScheme '{next(THEMES_ITER)}' pwsh -NoExit -Command '{next(INIT_COMMANDS_ITER)}' "

    else:
        if args.hosts is None:
            print("🌐 No hosts provided. Displaying options...")
            hosts = display_options(msg="Select hosts:", options=get_ssh_hosts() + [THIS_MACHINE], multi=True, fzf=True)
        else:
            print("🌐 Using provided hosts:", args.hosts)
            hosts = args.hosts
        assert isinstance(hosts, list)
        cmd = main_windows_and_wsl(window=args.window, hosts=hosts, orientation="vertical" if args.vertical else "horizontal")

    print("\n📋 Generated Command:")
    print("-" * 50)
    print(cmd)
    print("-" * 50 + "\n")

    # PROGRAM_PATH.write_text(cmd, encoding="utf-8")
    import subprocess

    subprocess.run(cmd, shell=True)
    print("✅ Command saved successfully!\n")


if __name__ == "__main__":
    main()
