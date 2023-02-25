
import platform
from machineconfig.utils.utils import PROGRAM_PATH, display_options
import crocodile.toolbox as tb


def get_mprocs_mount_txt(cloud, cloud_brand, rclone_cmd, localpath):
    if platform.system() == "Windows":
        sub_text_path = tb.P.tmpfile(suffix=".ps1").write_text(f"""
echo "Cloud brand: {cloud_brand}"
iex 'rclone about {cloud}:'
echo 'See ~/mounts/{cloud} for the mounted cloud'

echo ''
""")
        txt = f"""
cd ~
mkdir mounts -ErrorAction SilentlyContinue
# mkdir mounts/{cloud}  # this is not needed on windows

mprocs "powershell {sub_text_path}" "{rclone_cmd}" "btm" "timeout 2 & cd {localpath} & lf" "timeout 2 & cd {localpath} & pwsh" "pwsh" --names "info,service,monitor,explorer,main,terminal"
"""
    else:
        txt = f"""
cd ~
mkdir mounts -p
mkdir {localpath}-p
mprocs "echo 'see ~/mounts/{cloud} for the mounted cloud'; rclone about {cloud}:" "{rclone_cmd}" "btm" "lf" "bash" "bash" --names "about,service,monitor,explorer,main,shell"
"""
    return txt

def main(cloud=None, network=None):
    config = tb.Read.ini(tb.P.home().joinpath(".config/rclone/rclone.conf"))
    # default = tb.P.home().joinpath(".machineconfig/
    if cloud is None:
        cloud = display_options(msg="which cloud", options=config.sections(), header="CLOUD MOUNT", default=None)
    cloud_brand = config[cloud]["type"]

    if network is None: mount_loc = tb.P.home().joinpath(f"mounts/{cloud}")
    elif network and platform.system() == "Windows": mount_loc = "X: --network-mode"
    else: raise ValueError("network mount only supported on windows")

    mount_cmd = f"rclone mount {cloud}: {mount_loc} --vfs-cache-mode full --file-perms=0777"

    txt = get_mprocs_mount_txt(cloud, cloud_brand, mount_cmd, mount_loc)
    PROGRAM_PATH.write_text(txt)


if __name__ == '__main__':
    main()
