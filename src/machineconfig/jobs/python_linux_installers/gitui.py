

from machineconfig.utils.utils import get_latest_release, find_move_delete_linux
# import crocodile.toolbox as tb


def main():
    url = get_latest_release("https://github.com/extrawurst/gitui")
    download = url.joinpath(f"gitui-linux-musl.tar.gz").download().ungz_untar(inplace=True)
    find_move_delete_linux(downloaded=download, tool_name="gitui")


if __name__ == '__main__':
    main()
