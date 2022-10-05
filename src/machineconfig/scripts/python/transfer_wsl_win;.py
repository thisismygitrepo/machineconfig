
from crocodile.file_management import P
from crocodile.environment import WIN_FROM_WSL, system, WSL_FROM_WIN, UserName
import argparse


def main():
    parser = argparse.ArgumentParser(description="Move and copy files across from WSL to windows")

    # positional argument
    parser.add_argument("path", help="path to convert")
    parser.add_argument("path", help="path to convert")

    # FLAGS
    parser.add_argument("--move", "-m", help="Move file.", action="store_true")  # default is False
    # optional argument
    parser.add_argument("--destination", "-d", help="New path.", default="")

    args = parser.parse_args()
    path = P(args.path).expanduser().absolute()

    if system == "Windows":  # move files over to WSL
        path.copy(path=WSL_FROM_WIN.joinpath(UserName).joinpath(path.rel2home()), overwrite=True)
    else:  # move files from WSL to win
        path.copy(path=WIN_FROM_WSL.joinpath(UserName).joinpath(path.rel2home()), overwrite=True)



if __name__ == '__main__':
    main()