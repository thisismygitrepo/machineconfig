
import crocodile.toolbox as tb
from machineconfig.utils.utils import display_options, PROGRAM_PATH


def main():
    share_path = input("share path? (e.g. machine:/home/alex) = ")
    mount_path_1 = tb.P(share_path.split(":")[-1])
    remote_server = share_path.split(":")[0]

    mount_path_2 = tb.P.home().joinpath(f"mounts/{remote_server}").joinpath(mount_path_1)
    if str(mount_path_1).startswith("/home"):
        mount_path_3 = tb.P.home().joinpath(*mount_path_1.parts[3:])
    else:
        mount_path_3 = tb.P.home().joinpath(f"mounts/{remote_server}/{mount_path_1.name}")

    local_mount_point = display_options(msg="mount path", options=[mount_path_1, mount_path_2, mount_path_3, "enter custom path"], default=mount_path_3)

    PROGRAM_PATH.write_text(f"""
    remote_server={remote_server}
    share_path={share_path}
    local_mount_point={local_mount_point}
    """)


if __name__ == '__main__':
    main()
