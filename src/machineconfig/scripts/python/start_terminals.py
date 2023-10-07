
"""Script to start terminals on windows and wsl
"""

from machineconfig.utils.utils import PROGRAM_PATH, display_options, install_n_import, get_ssh_hosts, platform
from typing import Literal, TypeAlias


THIS_MACHINE = "this"
THIS_MACHINE_WSL = "thiswsl"
THIS_MACHINE_HOSTNAME = platform.node()
THIS_MACHINE_HOSTNAME_WSL = f"{THIS_MACHINE_HOSTNAME}wsl"
ORIENTATION: TypeAlias = Literal["vertical", "horizontal"]


def main_windows_and_wsl(window: int, hosts: list[str], orientation: ORIENTATION = "vertical", mprocs: bool = False):
    orientation_oposite = "horizontal" if orientation == "vertical" else "vertical"
    orientation_swap                = "up" if orientation         == "horizontal" else "left"
    orientation_opposite_move_focus = "up" if orientation_oposite == "horizontal" else "left"
    orientation_opposite_move_focus_other = "down" if orientation_oposite == "horizontal" else "right"
    sleep = 3
    sep = f"\nsleep {sleep}; wt --window {window}"  # or '`;'
    ssh_cmd = f"-t 'mprocs'" if mprocs else ''  # 'wsl_ssh_windows_port_forwarding.ps1'
    split_per_machine = 1 / len(hosts)
    size = 0.3
    known_hosts = get_ssh_hosts()
    if len(hosts) == 1:
        if "wsl" in hosts[0] or f"{hosts[0]}wsl" in known_hosts:  # its a windows machine with wsl
            host_wind = hosts[0] if "wsl" not in hosts[0] else hosts[0].split("wsl")[0]
            host_linux = f"{host_wind}wsl"
            cmd = f"""
wt --window {window} --title {hosts[0]} powershell -Command "ssh {host_linux} {ssh_cmd}" `; split-pane --{orientation} --title {hosts[0]}wsl --size 0.5 powershell -Command "ssh {host_wind} `; split-pane --{orientation_oposite} --size 0.5 powershell "
"""
        else:  # its a windows machine without wsl
            cmd = f"""wt --window {window} --title {hosts[0]} powershell -Command "ssh {hosts[0]} {ssh_cmd}" `; split-pane --{orientation} --title {hosts[0]}wsl --size 0.1 powershell """

    elif len(hosts) > 1:
        pane_cmd = f'powershell -Command "ssh {hosts[0]} {ssh_cmd}" ' if hosts[0] != THIS_MACHINE else ''
        cmd = f"""wt --window {window} --title {hosts[0]} {pane_cmd} """
        for a_host in hosts[1:]:
            if a_host != THIS_MACHINE: pane_cmd = f'powershell -Command "ssh {a_host} {ssh_cmd}" '
            else: pane_cmd = 'powershell'
            cmd += f"""{sep} split-pane --{orientation_oposite} --title {a_host}Windows --size {split_per_machine} {pane_cmd}  """
        for idx, a_host in enumerate(hosts[::-1]):
            if f"{a_host}wsl" not in known_hosts and a_host != THIS_MACHINE: continue
            pane_cmd = f'powershell -Command "ssh {a_host}wsl"' if a_host != THIS_MACHINE else 'wsl'
            if idx == 0: tmp = ''
            else: tmp = f"move-focus {orientation_opposite_move_focus}" if idx % 2 == 1 else f"move-focus {orientation_opposite_move_focus_other}"
            cmd += f"""{sep} {tmp} split-pane --{orientation} --title {a_host}wsl --size {size} {pane_cmd} """
            cmd += f"""{sep} swap-pane {orientation_swap} """
    else: raise NotImplementedError(f"len(hosts) = {len(hosts)}. Only 1 or 2 hosts are supported.")
    return cmd


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--vertical", "-V", action="store_true", help="Switch orientation to vertical from default horizontal")
    parser.add_argument("--window", "-w", type=int, help="The window id to use", default=0)  # 0 refers to this window.
    parser.add_argument("--hosts", "-H", type=str, nargs="*", help="The hosts to connect to", default=None)
    args = parser.parse_args()

    if args.hosts is None: hosts = display_options(msg="", options=get_ssh_hosts() + [THIS_MACHINE], multi=True, fzf=True)
    else:
        print("Using provided hosts", args.hosts)
        hosts = args.hosts
    assert isinstance(hosts, list)
    cmd = main_windows_and_wsl(window=args.window, hosts=hosts, orientation="vertical" if args.vertical else "horizontal")
    print(cmd)
    install_n_import("clipboard").copy(cmd)
    PROGRAM_PATH.write_text(cmd)


if __name__ == '__main__':
    main()
