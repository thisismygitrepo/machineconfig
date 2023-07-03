
import crocodile.toolbox as tb
from machineconfig.utils.utils import display_options, PROGRAM_PATH, choose_ssh_host

def main():
    share_path = input("share path? (e.g. machine:/home/alex) [press enter for interactive choice] = ")
    if share_path == "":
        ssh = tb.SSH(choose_ssh_host())
        share_path = display_options("Choose a share path: ", options=tb.L(ssh.run("cat /etc/exports").op.split("\n")).filter(lambda x: not x.startswith("#")).apply(lambda x: f"{ssh.hostname}:{x.split(' ')[0]}").list)

    mount_path_1 = tb.P(share_path.split(":")[-1])
    remote_server = share_path.split(":")[0]

    mount_path_2 = tb.P.home().joinpath(f"mounts/{remote_server}").joinpath(mount_path_1)
    if str(mount_path_1).startswith("/home"):
        mount_path_3 = tb.P.home().joinpath(*mount_path_1.parts[3:])
    else:
        mount_path_3 = tb.P.home().joinpath(f"mounts/{remote_server}/{mount_path_1.name}")

    local_mount_point = display_options(msg="choose mount path OR input custom one", options=[mount_path_1, mount_path_2, mount_path_3], default=mount_path_3, custom_input=True)
    PROGRAM_PATH.write_text(f"""
    remote_server={remote_server}
    share_path={share_path}
    local_mount_point={local_mount_point}
    """)
    print(PROGRAM_PATH.read_text())


if __name__ == '__main__':
    main()
