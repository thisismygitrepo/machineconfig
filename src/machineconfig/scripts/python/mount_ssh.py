
import crocodile.toolbox as tb
from platform import system
from machineconfig.utils.utils import PROGRAM_PATH, choose_ssh_host


def main():

    print(f"Mounting SSHFS ... ")
    share_info = input("share path? (e.g. user@host:/path) [press enter for interactive choice] = ")
    if share_info == "":
        ssh = tb.SSH(choose_ssh_host(multi=False))
        share_info = f"{ssh.username}@{ssh.hostname}:{ssh.run('echo $HOME').op}/data/share_ssh"
    else:
        ssh = tb.SSH(share_info.split(":")[0])
    print(tb.Terminal().run("net use", shell="powershell").op)
    driver_letter = input(r"Choose driver letter (e.g. Z:\) (avoid the ones already used) : ") or "Z:\\"

    mount_point = input(f"Enter the mount point directory (ex: /mnt/network) [default: ~/data/mount_ssh/{ssh.hostname}]: ")
    if mount_point == "": mount_point = tb.P.home().joinpath(fr"data/mount_ssh/{ssh.hostname}")

    if system() == "Linux":
        txt = fr"""
sshfs alex@:/media/dbhdd /media/dbhdd\
"""
    elif system() == "Windows":
        txt = fr"""
net use {driver_letter} {share_info}
fusermount -u /mnt/dbhdd
"""
    else: raise ValueError(f"Not implemented for this system {system()}")
    PROGRAM_PATH.write_text(txt)


if __name__ == '__main__':
    pass
