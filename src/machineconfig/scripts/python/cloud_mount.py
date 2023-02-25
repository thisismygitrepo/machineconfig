
import platform
from machineconfig.utils.utils import PROGRAM_PATH, display_options
import crocodile.toolbox as tb


def main(cloud=None, network=None):
    config = tb.Read.ini(tb.P.home().joinpath(".config/rclone/rclone.conf"))
    # default = tb.P.home().joinpath(".machineconfig/
    if cloud is None:
        cloud = display_options(msg="which cloud", options=config.sections(), header="CLOUD MOUNT", default=None)
    cloud_brand = config[cloud]["type"]
    if platform.system() == "Windows":
        if network is None:
            mount_loc = tb.P.home().joinpath(f"mounts/{cloud}")
        else:
            mount_loc = "X: --network-mode"
        mount_cmd = f"rclone mount {cloud}: {mount_loc} --vfs-cache-mode full --file-perms=0777"
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

mprocs "powershell {sub_text_path}" "{mount_cmd}" "btm" "timeout 2 & cd {mount_loc} & lf" "timeout 2 & cd {mount_loc} & pwsh" "pwsh" --names "info,service,monitor,explorer,main,terminal"
"""
    else:
        mount_cmd = f"rclone mount {cloud}: mounts/{cloud} --vfs-cache-mode full --file-perms=0777"
        txt = f"""
cd ~
mkdir mounts -p
mkdir mounts/{cloud} -p
mprocs "echo 'see ~/mounts/{cloud} for the mounted cloud'; rclone about {cloud}:" "{mount_cmd}" "btm" "lf" "bash" "bash" --name "about,service,monitor,explorer,main,shell"
"""

    PROGRAM_PATH.write_text(txt)


if __name__ == '__main__':
    main()
