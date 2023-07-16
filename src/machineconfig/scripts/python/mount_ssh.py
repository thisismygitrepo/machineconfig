
import crocodile.toolbox as tb
from platform import system


def main():
    if system() == "Linux":
        txt = fr"""
net use Y: \\sshfs\aalsaf01@sshfs\229234!9546
"""
    elif system() == "Windows":
        txt = fr"""
sshfs alex@:/media/dbhdd /media/dbhdd
fusermount -u /mnt/dbhdd
        """
    else: raise ValueError(f"Not implemented for this system {system()}")


if __name__ == '__main__':
    pass
