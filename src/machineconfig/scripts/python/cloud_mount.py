
import platform
from machineconfig.utils.utils import PROGRAM_PATH, display_options
import crocodile.toolbox as tb


DEFAULT_MOUNT = "~/data/rclone"


def get_mprocs_mount_txt(cloud, rclone_cmd):
    config = tb.Read.ini(tb.P.home().joinpath(".config/rclone/rclone.conf"))
    cloud_brand = config[cloud]["type"]
    header = f"{' ' + cloud + ' | ' + cloud_brand + ' '}".center(50, "=")
    if platform.system() == "Windows":
        sub_text_path = tb.P.tmpfile(suffix=".ps1").write_text(f"""
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


def main(cloud=None, network=None):
    config = tb.Read.ini(tb.P.home().joinpath(".config/rclone/rclone.conf"))
    # default = tb.P.home().joinpath(".machineconfig/
    if cloud is None:
        cloud = display_options(msg="which cloud", options=config.sections(), header="CLOUD MOUNT", default=None)

    if network is None: mount_loc = tb.P(DEFAULT_MOUNT).expanduser().joinpath(cloud)
    elif network and platform.system() == "Windows": mount_loc = "X: --network-mode"
    else: raise ValueError("network mount only supported on windows")

    if platform.system() == "Windows": mount_loc.parent.create()
    elif platform.system() == "Linux": mount_loc.create()
    # else: raise ValueError("unsupported platform")

    mount_cmd = f"rclone mount {cloud}: {mount_loc} --vfs-cache-mode full --file-perms=0777"

    # txt = get_mprocs_mount_txt(cloud, mount_cmd)
    if platform.system() == "Windows": txt = f"""
wt --window 0 --profile "Windows PowerShell" --startingDirectory "$HOME/data/rclone" `; split-pane --horizontal  --profile "Command Prompt" --size 0.1 powershell -Command "{mount_cmd}" `; move-focus up
"""
    elif platform.system() == "Linux": txt = f"""
cd $HOME/data/rclone; zellij run --direction down --name rclone -- {mount_cmd}
"""
    else: raise ValueError("unsupported platform")
    print(f"running command: \n{txt}")
    PROGRAM_PATH.write_text(txt)


if __name__ == '__main__':
    main()
