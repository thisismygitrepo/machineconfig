
"""Cloud mount script
"""


from machineconfig.utils.utils import PROGRAM_PATH, choose_one_option
from crocodile.file_management import P, Read

import platform
import argparse
from typing import Optional


DEFAULT_MOUNT = "~/data/rclone"


def get_rclone_config():
    if platform.system() == "Windows": config = Read.ini(P.home().joinpath("AppData/Roaming/rclone/rclone.conf"))
    elif platform.system() == "Linux": config = Read.ini(P.home().joinpath(".config/rclone/rclone.conf"))
    else: raise ValueError("unsupported platform")
    return config


def get_mprocs_mount_txt(cloud: str, rclone_cmd: str, cloud_brand: str):  # cloud_brand = config[cloud]["type"]
    # config = Read.ini(P.home().joinpath(".config/rclone/rclone.conf"))
    header = f"{' ' + cloud + ' | ' + cloud_brand + ' '}".center(50, "=")
    if platform.system() == "Windows":
        sub_text_path = P.tmpfile(suffix=".ps1").write_text(f"""
echo "{header}"
iex 'rclone about {cloud}:'
echo 'See {DEFAULT_MOUNT}/{cloud} for the mounted cloud'

echo ''
""")
        txt = f"""
cd ~
mprocs "powershell {sub_text_path}" "{rclone_cmd}" "btm" "timeout 2 & cd {DEFAULT_MOUNT} & lf" "timeout 2 & cd {DEFAULT_MOUNT} & pwsh" "pwsh" --names "info,service,monitor,explorer,main,terminal"
"""
    else: txt = f"""
mprocs "echo 'see {DEFAULT_MOUNT}/{cloud} for the mounted cloud'; rclone about {cloud}:" "{rclone_cmd}" "btm" "cd {DEFAULT_MOUNT}; lf" "bash" "bash" --names "about,service,monitor,explorer,main,shell"
"""
    return txt


def mount(cloud: Optional[str], network: Optional[str], destination: Optional[str]) -> None:

    config = get_rclone_config()
    if cloud is None:
        res = choose_one_option(msg="which cloud", options=config.sections(), header="CLOUD MOUNT", default=None)
        if type(res) is str: cloud = res
        else: raise ValueError("no cloud selected")


    if network is None:
        if destination is None: mount_loc = P(DEFAULT_MOUNT).expanduser().joinpath(cloud)
        else: mount_loc = P(destination)

        if platform.system() == "Windows": mount_loc.parent.create()
        elif platform.system() == "Linux": mount_loc.create()
        else: raise ValueError("unsupported platform")

    elif network and platform.system() == "Windows": mount_loc = "X: --network-mode"
    else: raise ValueError("network mount only supported on windows")

    mount_cmd = f"rclone mount {cloud}: {mount_loc} --vfs-cache-mode full --file-perms=0777"

    # txt = get_mprocs_mount_txt(cloud, mount_cmd)
    if platform.system() == "Windows": txt = f"""
wt --window 0 --profile "Windows PowerShell" --startingDirectory "$HOME/data/rclone" `; split-pane --horizontal  --profile "Command Prompt" --size 0.2 powershell -Command "{mount_cmd}" `; split-pane --vertical --profile "Windows PowerShell" --size 0.2 powershell -NoExit -Command "rclone about {cloud}:"  `; move-focus up
"""
    elif platform.system() == "Linux": txt = f"""

ZJ_SESSIONS=$(zellij list-sessions)

if [[ "${{ZJ_SESSIONS}}" != *"(current)"* ]]; then
    echo "Not inside a zellij session ..."
    echo '{mount_cmd}'
    exit 1
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
zellij run --direction right --name about -- rclone about {cloud}:
zellij action move-focus up
# zellij action write-chars "cd $HOME/data/rclone/{cloud}; sleep 0.1; ls"
zellij run --direction left --cwd $HOME/data/rclone/{cloud} -- lf
zellij run --direction up -- btm --default_widget_type net --expanded
zellij run --in-place --cwd $HOME/data/rclone/{cloud} -- bash
zellij action move-focus up
"""
    else: raise ValueError("unsupported platform")
    # print(f"running command: \n{txt}")
    PROGRAM_PATH.write_text(txt)


def main():
    parser = argparse.ArgumentParser(description='mount cloud')
    parser.add_argument('cloud', nargs='?', type=str, default=None, help='cloud to mount')
    parser.add_argument('destination', nargs='?', type=str, default=None, help='destination to mount')
    parser.add_argument('--network', type=str, default=None, help='mount network drive')
    args = parser.parse_args()
    mount(cloud=args.cloud, network=args.network, destination=args.destination)


if __name__ == '__main__':
    main()
