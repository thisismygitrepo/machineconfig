
import crocodile.toolbox as tb
from machineconfig.utils.utils import display_options, PROGRAM_PATH, choose_ssh_host


def main():
    print(f"Mounting NFS Share ... ")
    share_info = input("share path? (e.g. machine:/home/alex/data/share_nfs) [press enter for interactive choice] = ")
    if share_info == "":
        ssh = tb.SSH(choose_ssh_host())
        default = f"{ssh.hostname}:{ssh.run('echo $HOME').op}/data/share_nfs"
        share_info = display_options("Choose a share path: ", options=tb.L(ssh.run("cat /etc/exports").op.split("\n")).filter(lambda x: not x.startswith("#")).apply(lambda x: f"{ssh.hostname}:{x.split(' ')[0]}").list + [default], default=default)

    remote_server = share_info.split(":")[0]
    share_path = share_info.split(":")[1]
    mount_path_1 = tb.P(share_path)

    mount_path_2 = tb.P.home().joinpath(f"mounts/{remote_server}").joinpath(mount_path_1)
    if str(mount_path_1).startswith("/home"): mount_path_3 = tb.P.home().joinpath(*mount_path_1.parts[3:])
    else: mount_path_3 = tb.P.home().joinpath(f"data/mount_nfs/{remote_server}")

    local_mount_point = display_options(msg="choose mount path OR input custom one", options=[mount_path_1, mount_path_2, mount_path_3], default=mount_path_3, custom_input=True)
    PROGRAM_PATH.write_text(f"""
share_info={share_info}
remote_server={remote_server}
share_path={share_path}
local_mount_point={local_mount_point}
    """)
    print(PROGRAM_PATH.read_text())


if __name__ == '__main__':
    main()
