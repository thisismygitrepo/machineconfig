

from machineconfig.utils.utils import PROGRAM_PATH, choose_ssh_host, install_n_import


def main_windows_and_wsl(hosts: list[str], orientation="vertical", mprocs=False):
    orientation_oposite = "horizontal" if orientation == "vertical" else "vertical"
    orientation_swap                = "up" if orientation         == "horizontal" else "left"
    orientation_opposite_move_focus = "up" if orientation_oposite == "horizontal" else "left"
    window = 500
    sleep = 3
    sep = f"\nsleep {sleep}; wt --window {window}"  # or '`;'
    ssh_cmd = f"-t 'mprocs'" if mprocs else ''  # 'wsl_ssh_windows_port_forwarding.ps1'
    split_per_machine = 1 / len(hosts)
    size = 0.3
    if len(hosts) == 1:
        cmd = f"""
wt --window {window} --title {hosts[0]}Windows powershell -Command "ssh {hosts[0]} {ssh_cmd}" `; split-pane --{orientation} --title {hosts[0]}wsl --size 0.5 powershell -Command "ssh {hosts[0]}wsl"
"""
    elif len(hosts) > 1:
        cmd = f"""wt --window {window} --title {hosts[0]}Windows powershell -Command "ssh {hosts[0]} {ssh_cmd}" """
        for a_host in hosts[1:]:
            cmd += f"""{sep} split-pane --{orientation_oposite} --title {a_host}Windows --size {split_per_machine} powershell -Command "ssh {a_host} {ssh_cmd}"  """
        for idx, a_host in enumerate(hosts[::-1]):
            tmp = f"move-focus {orientation_opposite_move_focus}" if idx == 0 else ""
            cmd += f"""{sep} {tmp} split-pane --{orientation} --title {a_host}wsl --size {size} powershell -Command "ssh {a_host}wsl" """
            cmd += f"""{sep} swap-pane {orientation_swap} """
    else: raise NotImplementedError(f"len(hosts) = {len(hosts)}. Only 1 or 2 hosts are supported.")
    return cmd


def main():
    import argparse
    parser = argparse.ArgumentParser()
    # parser.add_argument("-p", "--path", type=str, help="The directory containing the jobs", default=".")
    # # optional flag for interactivity
    parser.add_argument("--vertical", "-V", action="store_true", help="Switch orientation to vertical from default horizontal")
    # parser.add_argument("--debug", "-d", action="store_true", help="debug")
    # parser.add_argument("--remote", "-r", action="store_true", help="launch on a remote machine")
    # parser.add_argument("--main", "-m", action="store_true", help="launch the main file")
    # parser.add_argument("--history", "-h", action="store_true", help="choose from history")
    args = parser.parse_args()

    hosts = choose_ssh_host(multi=True)
    cmd = main_windows_and_wsl(hosts=hosts, orientation="vertical" if args.vertical else "horizontal")
    print(cmd)
    install_n_import("pyperclip").copy(cmd)
    PROGRAM_PATH.write_text(cmd)


if __name__ == '__main__':
    main()
