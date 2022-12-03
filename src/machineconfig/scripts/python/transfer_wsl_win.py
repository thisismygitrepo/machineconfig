
from crocodile.file_management import P
from crocodile.environment import WIN_FROM_WSL, system, WSL_FROM_WIN, UserName
import argparse


def main():
    parser = argparse.ArgumentParser(description="""Move and copy files across between WSL & Windows."
The direction is automatically determined by sensing the execution environment.
Otherwise, a flag must be raised to indicate the direction.""")

    # positional argument
    parser.add_argument("path", help="path of file/folder to transfer over.")
    # FLAGS
    # this is dangerous and no gaurantee on no corruption.
    parser.add_argument("--same_file_system", "-s", help="Move file.", action="store_true")  # default is False
    # optional argument
    # parser.add_argument("--destination", "-d", help="New path.", default="")
    parser.add_argument("--pwd", "-P", help="Password for encryption", default=None)
    parser.add_argument("--sshkey", "-i", help="path to ssh private key", default=None)
    parser.add_argument("--port", "-p", help="port number", default=2222)

    args = parser.parse_args()
    path = P(args.path).expanduser().absolute()

    if args.same_file_system:
        if system == "Windows":  # move files over to WSL
            path.copy(folder=WSL_FROM_WIN.joinpath(UserName).joinpath(path.rel2home().parent), overwrite=True)  # the following works for files and folders alike.
        else:  # move files from WSL to win
            path.copy(folder=WIN_FROM_WSL.joinpath(UserName).joinpath(path.rel2home().parent), overwrite=True)
    else:
        from crocodile.meta import SSH
        sshkey = args.sshkey
        if args.sshkey is None: sshkey = P.home().joinpath(".ssh").search("*.pub").apply(lambda x: x.with_name(x.stem)); sshkey = sshkey[0] if len(sshkey) else None
        ssh = SSH(port=args.port, sshkey=sshkey)
        ssh.copy_from_here(source=path)


if __name__ == '__main__':
    main()
