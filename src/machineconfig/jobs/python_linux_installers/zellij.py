

from machineconfig.utils.utils import get_latest_release, find_move_delete_linux
import crocodile.toolbox as tb


def main():
    # url = get_latest_release("https://github.com/zellij-org/zellij")
    download = tb.P(f"https://github.com/zellij-org/zellij/releases/latest/download/zellij-x86_64-unknown-linux-musl.tar.gz").download().ungz_untar(inplace=True)
    find_move_delete_linux(downloaded=download, tool_name="zellij")


if __name__ == '__main__':
    main()

